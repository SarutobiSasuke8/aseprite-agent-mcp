"""Batch operation registry + one-script Lua assembler.

Pure-Python (no Aseprite): validates a list of `{"op": str, "args": {...}}` operations
against a curated registry, then provides the Lua body that runs them all in a single
process inside one `app.transaction` (open once -> all ops -> save once, atomically).

Validation happens before any Aseprite launch and is the basis of `dry_run`. It checks
*shape* (unknown op, missing/typed args, bad colour/number) — not runtime sprite state
(a missing layer/frame is an execute-time failure).
"""

from __future__ import annotations

from .errors import ValidationFailed
from .limits import MAX_BATCH_OPERATIONS, check_list_length
from .models import ColorSpec

# Arg kinds.
_INT, _STR, _BOOL, _COLOR = "int", "str", "bool", "color"
_ROWS, _KEY = "rows", "key"  # pixel_rows: list of strings, char -> colour map

MAX_ROWS = 256  # rows per pixel_rows op, and characters per row

# Curated v1 op set. Each entry maps arg name -> (kind, required).
_DRAW_TARGET = {"layer": (_STR, False), "frame": (_INT, False)}
OP_SPECS: dict[str, dict] = {
    # layers
    "add_layer": {"name": (_STR, True), "opacity": (_INT, False),
                  "blend_mode": (_STR, False), "visible": (_BOOL, False)},
    "rename_layer": {"layer": (_STR, True), "new_name": (_STR, True)},
    "set_layer_visible": {"layer": (_STR, True), "visible": (_BOOL, True)},
    "set_layer_opacity": {"layer": (_STR, True), "opacity": (_INT, True)},
    "remove_layer": {"layer": (_STR, True)},
    # frames
    "add_frame": {"duration_ms": (_INT, False), "copy_from": (_INT, False)},
    "duplicate_frame": {"frame": (_INT, True)},
    "set_frame_duration": {"frame": (_INT, True), "duration_ms": (_INT, True)},
    # tags
    "add_tag": {"name": (_STR, True), "from": (_INT, True), "to": (_INT, True),
                "direction": (_STR, False), "color": (_COLOR, False)},
    "remove_tag": {"name": (_STR, True)},
    # drawing
    "set_pixel": {**_DRAW_TARGET, "x": (_INT, True), "y": (_INT, True), "color": (_COLOR, True)},
    "draw_line": {**_DRAW_TARGET, "x1": (_INT, True), "y1": (_INT, True),
                  "x2": (_INT, True), "y2": (_INT, True), "color": (_COLOR, True)},
    "draw_rectangle": {**_DRAW_TARGET, "x": (_INT, True), "y": (_INT, True),
                       "width": (_INT, True), "height": (_INT, True), "color": (_COLOR, True)},
    "fill_rectangle": {**_DRAW_TARGET, "x": (_INT, True), "y": (_INT, True),
                       "width": (_INT, True), "height": (_INT, True), "color": (_COLOR, True)},
    "draw_ellipse": {**_DRAW_TARGET, "cx": (_INT, True), "cy": (_INT, True),
                     "rx": (_INT, True), "ry": (_INT, True), "color": (_COLOR, True)},
    "fill_ellipse": {**_DRAW_TARGET, "cx": (_INT, True), "cy": (_INT, True),
                     "rx": (_INT, True), "ry": (_INT, True), "color": (_COLOR, True)},
    "fill_layer": {**_DRAW_TARGET, "color": (_COLOR, True)},
    "clear_layer": {**_DRAW_TARGET},
    # slices
    "add_slice": {"name": (_STR, True), "x": (_INT, True), "y": (_INT, True),
                  "width": (_INT, True), "height": (_INT, True), "color": (_COLOR, False)},
    "remove_slice": {"name": (_STR, True)},
    # palette / colour
    "replace_color": {**_DRAW_TARGET, "from": (_COLOR, True), "to": (_COLOR, True),
                      "tolerance": (_INT, False)},
    # pixel art in one op: each character of each row is looked up in `key`
    "pixel_rows": {**_DRAW_TARGET, "rows": (_ROWS, True), "key": (_KEY, True),
                   "x": (_INT, False), "y": (_INT, False), "clear": (_BOOL, False)},
    # cels (animation motion without redrawing)
    "copy_cel": {"from_frame": (_INT, True), "to_frame": (_INT, True),
                 "layer": (_STR, False), "to_layer": (_STR, False)},
    "offset_cel": {**_DRAW_TARGET, "dx": (_INT, True), "dy": (_INT, True)},
}

# One-line meaning of each op, used to build the tool descriptions agents read.
OP_HELP: dict[str, str] = {
    "add_layer": "new layer on top",
    "rename_layer": "rename a layer",
    "set_layer_visible": "show or hide a layer",
    "set_layer_opacity": "layer opacity 0-255",
    "remove_layer": "delete a layer (not the last one)",
    "add_frame": "append a frame (copy_from copies an existing frame)",
    "duplicate_frame": "insert a copy of a frame after it",
    "set_frame_duration": "frame duration in milliseconds",
    "add_tag": "animation tag over frames from..to (direction forward|reverse|pingpong)",
    "remove_tag": "delete a tag by name",
    "set_pixel": "one pixel",
    "draw_line": "1px line between two points",
    "draw_rectangle": "rectangle outline",
    "fill_rectangle": "filled rectangle",
    "draw_ellipse": "ellipse outline",
    "fill_ellipse": "filled ellipse",
    "fill_layer": "fill the whole cel",
    "clear_layer": "make the cel fully transparent",
    "add_slice": "named slice rectangle",
    "remove_slice": "delete a slice",
    "replace_color": "swap one colour for another in a cel",
    "pixel_rows": ("draw a block of pixel art: rows is a list of strings, key maps each "
                   "character to a colour; '.' and ' ' are skipped unless key defines them; "
                   "clear=true erases the cel first; x,y place the top-left"),
    "copy_cel": "copy a layer's cel from one frame to another (to_layer defaults to the same layer)",
    "offset_cel": "move a cel's pixels by dx,dy (bob, step or shake without redrawing)",
}


def describe_ops() -> str:
    """Op vocabulary for tool descriptions, generated from the registry."""
    lines = []
    for name, spec in OP_SPECS.items():
        args = ", ".join(f"{a}{'' if req else '?'}:{kind}" for a, (kind, req) in spec.items())
        lines.append(f"- {name}({args}): {OP_HELP.get(name, '')}")
    return "\n".join(lines)


def validate_operations(operations) -> list[dict]:
    """Validate + normalize a list of operations. Raises ValidationFailed (with the
    offending op index) on shape errors. Colours are parsed to dicts; ints coerced."""
    if not isinstance(operations, list) or not operations:
        raise ValidationFailed("operations must be a non-empty list.")
    check_list_length(
        "operations", operations, MAX_BATCH_OPERATIONS,
        remedy="Split the edit into multiple batches.",
    )

    normalized: list[dict] = []
    for i, op in enumerate(operations):
        if not isinstance(op, dict) or "op" not in op:
            raise ValidationFailed(f"op {i}: each operation needs an 'op' field.")
        name = op["op"]
        spec = OP_SPECS.get(name)
        if spec is None:
            raise ValidationFailed(
                f"op {i}: unknown operation '{name}'. Known ops: {sorted(OP_SPECS)}."
            )
        args = op.get("args", {})
        if not isinstance(args, dict):
            raise ValidationFailed(f"op {i} ({name}): 'args' must be an object.")

        norm: dict = {}
        for arg, (kind, required) in spec.items():
            if arg not in args or args[arg] is None:
                if required:
                    raise ValidationFailed(f"op {i} ({name}): missing required arg '{arg}'.")
                continue
            value = args[arg]
            try:
                if kind == _INT:
                    norm[arg] = int(value)
                elif kind == _STR:
                    norm[arg] = str(value)
                elif kind == _BOOL:
                    norm[arg] = bool(value)
                elif kind == _COLOR:
                    norm[arg] = ColorSpec.parse(value).as_dict()
                elif kind == _ROWS:
                    norm[arg] = _validate_rows(value)
                elif kind == _KEY:
                    norm[arg] = _validate_key(value)
            except (ValueError, TypeError) as exc:
                raise ValidationFailed(f"op {i} ({name}): bad value for '{arg}': {exc}") from exc
        entry = {"op": name, "args": norm}
        if name == "pixel_rows":
            check_rows_use_key(entry, i)
        normalized.append(entry)
    return normalized


def _validate_rows(value) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError("rows must be a non-empty list of strings")
    if len(value) > MAX_ROWS:
        raise ValueError(f"at most {MAX_ROWS} rows per op; split the drawing")
    rows = []
    for r in value:
        if not isinstance(r, str):
            raise ValueError("every row must be a string")
        if len(r) > MAX_ROWS:
            raise ValueError(f"rows may be at most {MAX_ROWS} characters")
        rows.append(r)
    return rows


def _validate_key(value) -> dict:
    if not isinstance(value, dict) or not value:
        raise ValueError("key must be a non-empty object mapping one character to a colour")
    out = {}
    for ch, colour in value.items():
        if not isinstance(ch, str) or len(ch) != 1:
            raise ValueError(f"key entries must be single characters, got {ch!r}")
        out[ch] = ColorSpec.parse(colour).as_dict()
    return out


def check_rows_use_key(op: dict, index: int) -> None:
    """Every non-skip character in rows must be defined in key."""
    a = op["args"]
    known = set(a["key"]) | {".", " "}
    unknown = sorted({ch for row in a["rows"] for ch in row} - known)
    if unknown:
        raise ValidationFailed(
            f"op {index} (pixel_rows): characters {unknown} are not in key. "
            "Add them to key, or use '.' for transparent/skip."
        )


def summarize(op: dict) -> str:
    """A short human/agent-readable summary of a (normalized) op."""
    args = op.get("args", {})
    inner = ", ".join(f"{k}={v}" for k, v in args.items())
    return f"{op['op']}({inner})"


# The Lua body run via core.runner.run_lua. It reads ARG.operations (a list of
# {op, args}) and applies them atomically. On any op failure it raises a JSON-encoded
# error (level 0, no position prefix) so Python can surface a structured message; the
# transaction rolls back and the file is never saved.
BATCH_LUA_BODY = r"""
local spr = open_sprite(ARG.src)
local applied = {}

local function run_op(op)
  local a = op.args
  local name = op.op
  -- layers
  if name == "add_layer" then
    local l = spr:newLayer(); l.name = a.name
    if a.opacity ~= nil then l.opacity = a.opacity end
    if a.blend_mode ~= nil then l.blendMode = blendmode_from(a.blend_mode) end
    if a.visible ~= nil then l.isVisible = a.visible end
    return "added layer '" .. a.name .. "'"
  elseif name == "rename_layer" then
    find_layer(spr, a.layer).name = a.new_name
    return "renamed '" .. tostring(a.layer) .. "' -> '" .. a.new_name .. "'"
  elseif name == "set_layer_visible" then
    find_layer(spr, a.layer).isVisible = a.visible
    return "set '" .. tostring(a.layer) .. "' visible=" .. tostring(a.visible)
  elseif name == "set_layer_opacity" then
    find_layer(spr, a.layer).opacity = a.opacity
    return "set '" .. tostring(a.layer) .. "' opacity=" .. a.opacity
  elseif name == "remove_layer" then
    if #spr.layers <= 1 then error("cannot delete the only layer", 0) end
    spr:deleteLayer(find_layer(spr, a.layer))
    return "removed layer '" .. tostring(a.layer) .. "'"
  -- frames
  elseif name == "add_frame" then
    local fr
    if a.copy_from ~= nil then fr = append_frame(spr, clamp_frame(spr, a.copy_from))
    else fr = append_frame(spr, nil) end
    if a.duration_ms ~= nil then fr.duration = a.duration_ms / 1000.0 end
    return "added frame " .. fr.frameNumber
  elseif name == "duplicate_frame" then
    local fr = spr:newFrame(clamp_frame(spr, a.frame))
    return "duplicated frame -> " .. fr.frameNumber
  elseif name == "set_frame_duration" then
    spr.frames[clamp_frame(spr, a.frame)].duration = a.duration_ms / 1000.0
    return "set frame " .. a.frame .. " duration"
  -- tags
  elseif name == "add_tag" then
    local f1, f2 = clamp_frame(spr, a["from"]), clamp_frame(spr, a.to)
    if f1 > f2 then f1, f2 = f2, f1 end
    local t = spr:newTag(f1, f2); t.name = a.name
    if a.direction ~= nil then t.aniDir = anidir_from(a.direction) end
    if a.color ~= nil then t.color = mkcolor(a.color) end
    return "added tag '" .. a.name .. "'"
  elseif name == "remove_tag" then
    local found = nil
    for _, tg in ipairs(spr.tags) do if tg.name == a.name then found = tg end end
    if found == nil then error("no tag named '" .. tostring(a.name) .. "'", 0) end
    spr:deleteTag(found)
    return "removed tag '" .. a.name .. "'"
  -- slices
  elseif name == "add_slice" then
    local sl = spr:newSlice(Rectangle(a.x, a.y, a.width, a.height)); sl.name = a.name
    if a.color ~= nil then sl.color = mkcolor(a.color) end
    return "added slice '" .. a.name .. "'"
  elseif name == "remove_slice" then
    local found = nil
    for _, s in ipairs(spr.slices) do if s.name == a.name then found = s end end
    if found == nil then error("no slice named '" .. tostring(a.name) .. "'", 0) end
    spr:deleteSlice(found)
    return "removed slice '" .. a.name .. "'"
  -- palette / colour
  elseif name == "replace_color" then
    local layer = find_layer(spr, a.layer)
    if layer.isGroup then error("cannot edit a group layer: " .. layer.name, 0) end
    local n = clamp_frame(spr, a.frame or 1)
    local img = get_draw_image(spr, layer, n)
    local from = a["from"]
    if from.index ~= nil then
      local c = spr.palettes[1]:getColor(math.floor(from.index))
      from = { r = c.red, g = c.green, b = c.blue, a = c.alpha }
    end
    local fr, fg, fb, fa = from.r, from.g, from.b, from.a or 255
    local tol = a.tolerance or 0
    local tp = to_pixel(spr, a.to)
    for yy = 0, img.height - 1 do
      for xx = 0, img.width - 1 do
        local r, g, b, al = px_to_rgba(spr, img:getPixel(xx, yy))
        if math.abs(r - fr) <= tol and math.abs(g - fg) <= tol
           and math.abs(b - fb) <= tol and math.abs(al - fa) <= tol then
          img:drawPixel(xx, yy, tp)
        end
      end
    end
    commit_image(spr, layer, n, img)
    return "replaced colour"
  -- cels
  elseif name == "copy_cel" then
    local src_layer = find_layer(spr, a.layer)
    local dst_layer = src_layer
    if a.to_layer ~= nil then dst_layer = find_layer(spr, a.to_layer) end
    local f1, f2 = clamp_frame(spr, a.from_frame), clamp_frame(spr, a.to_frame)
    local cel = src_layer:cel(f1)
    if cel == nil then error("no cel on '" .. src_layer.name .. "' at frame " .. f1, 0) end
    local existing = dst_layer:cel(f2)
    if existing ~= nil then spr:deleteCel(existing) end
    spr:newCel(dst_layer, f2, cel.image:clone(), cel.position)
    return "copied cel " .. src_layer.name .. "@" .. f1 .. " -> " .. dst_layer.name .. "@" .. f2
  elseif name == "offset_cel" then
    local layer = find_layer(spr, a.layer)
    local n = clamp_frame(spr, a.frame or 1)
    local cel = layer:cel(n)
    if cel == nil then error("no cel on '" .. layer.name .. "' at frame " .. n, 0) end
    cel.position = Point(cel.position.x + a.dx, cel.position.y + a.dy)
    return "moved cel by " .. a.dx .. "," .. a.dy
  -- drawing (shared open/commit)
  else
    local layer = find_layer(spr, a.layer)
    if layer.isGroup then error("cannot draw on a group layer: " .. layer.name, 0) end
    local n = clamp_frame(spr, a.frame or 1)
    local img = get_draw_image(spr, layer, n)
    if name == "set_pixel" then
      img_set(img, a.x, a.y, to_pixel(spr, a.color))
    elseif name == "draw_line" then
      draw_line_img(img, a.x1, a.y1, a.x2, a.y2, to_pixel(spr, a.color))
    elseif name == "draw_rectangle" then
      draw_rect_img(img, a.x, a.y, a.width, a.height, to_pixel(spr, a.color), false)
    elseif name == "fill_rectangle" then
      draw_rect_img(img, a.x, a.y, a.width, a.height, to_pixel(spr, a.color), true)
    elseif name == "draw_ellipse" then
      draw_ellipse_img(img, a.cx, a.cy, a.rx, a.ry, to_pixel(spr, a.color), false)
    elseif name == "fill_ellipse" then
      draw_ellipse_img(img, a.cx, a.cy, a.rx, a.ry, to_pixel(spr, a.color), true)
    elseif name == "fill_layer" then
      draw_rect_img(img, 0, 0, spr.width, spr.height, to_pixel(spr, a.color), true)
    elseif name == "clear_layer" then
      img:clear()
    elseif name == "pixel_rows" then
      if a.clear then img:clear() end
      local ox, oy = a.x or 0, a.y or 0
      local lut = {}
      for ch, c in pairs(a.key) do lut[ch] = to_pixel(spr, c) end
      for ry, row in ipairs(a.rows) do
        for rx = 1, #row do
          local px = lut[row:sub(rx, rx)]
          if px ~= nil then img_set(img, ox + rx - 1, oy + ry - 1, px) end
        end
      end
    else
      error("unknown op '" .. tostring(name) .. "'", 0)
    end
    commit_image(spr, layer, n, img)
    return name
  end
end

app.transaction(function()
  for i, op in ipairs(ARG.operations) do
    local ok, ret = pcall(run_op, op)
    if not ok then
      error(json_encode({ failed_op_index = i - 1, failed_op = op.op, error = tostring(ret) }), 0)
    end
    applied[i] = { index = i - 1, op = op.op, status = "applied", summary = ret }
  end
end)

save_sprite(spr)
RESULT = { sprite = sprite_info(spr), operations = applied }
"""
