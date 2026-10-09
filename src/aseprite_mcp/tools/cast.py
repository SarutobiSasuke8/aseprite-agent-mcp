"""Character-cast tools: fast pixel art, derived directions, shared bases and recolours.

These cover the repetitive parts of building a cast of small game characters:
drawing a whole frame in one call, deriving a mirrored direction from an existing
tag, copying animation frames from a shared base file, and recolouring one
template into a new character. Every tool edits the native .aseprite master and
saves it with the crash-safe save path.
"""

from __future__ import annotations

from ..app import mcp
from ..core.paths import ensure_output_path
from ..core.runner import run_lua
from .batch import apply_operations
from .common import lua_path, parse_color, resolve_path

# Shared Lua helpers for this module.
_HELPERS = """
local function find_tag(spr, name)
  for _, t in ipairs(spr.tags) do if t.name == name then return t end end
  return nil
end

local function tag_names(spr)
  local names = {}
  for _, t in ipairs(spr.tags) do names[#names + 1] = t.name end
  if #names == 0 then return "(none)" end
  return table.concat(names, ", ")
end

"""


@mcp.tool()
def draw_pixel_rows(
    filename: str,
    rows: list[str],
    key: dict[str, str],
    layer: str | int | None = None,
    frame: int = 1,
    x: int = 0,
    y: int = 0,
    clear: bool = False,
) -> dict:
    """Draw a block of pixel art in one call, like a text-art bitmap.

    Each string in `rows` is one pixel row; each character is looked up in `key`
    and painted at (x + column, y + row), with (0,0) the top-left of the canvas.
    '.' and ' ' are left untouched unless `key` defines them. Any other character
    missing from `key` is an error, so typos never paint silently.

    Example: rows=["..oo..", ".oxxo.", "..oo.."], key={"o": "#203040", "x": "#f0c060"}.

    Args:
        rows: Up to 256 strings of up to 256 characters each.
        key: Single character -> colour ("#RRGGBB", "#RRGGBBAA", "r,g,b", "index:N", a name).
            Map a character to "transparent" to erase pixels.
        layer: Layer name or 1-based index (default: top layer).
        frame: 1-based frame; it must already exist.
        clear: Erase the whole cel before drawing (use for full-frame redraws).
    """
    args = {"rows": rows, "key": key, "x": x, "y": y, "clear": clear, "frame": frame}
    if layer is not None:
        args["layer"] = str(layer)
    return apply_operations(filename, [{"op": "pixel_rows", "args": args}])


@mcp.tool()
def derive_mirrored_tag(
    filename: str,
    source_tag: str,
    new_tag: str,
    axis: str = "horizontal",
) -> dict:
    """Create a new animation tag by mirroring an existing one (e.g. walk_left from walk_right).

    Copies every frame of `source_tag` to new frames at the end of the sprite,
    flips every layer's cel along `axis`, keeps each frame's duration, and tags
    the new frames `new_tag` with the source tag's playback direction. Other tags
    keep their exact ranges. Asymmetric details (a sword hand, a logo) flip too,
    so review the result with ase_preview_animation.

    Args:
        source_tag: Existing tag to mirror.
        new_tag: Name for the new tag; must not exist yet.
        axis: "horizontal" (left/right) or "vertical" (up/down).
    """
    if axis not in ("horizontal", "vertical"):
        raise ValueError('axis must be "horizontal" or "vertical".')
    args = {
        "src": lua_path(resolve_path(filename)),
        "source_tag": source_tag,
        "new_tag": new_tag,
        "horizontal": axis == "horizontal",
    }
    body = _HELPERS + """
    local spr = open_sprite(ARG.src)
    local src = find_tag(spr, ARG.source_tag)
    if src == nil then error("No tag named '" .. ARG.source_tag .. "'. Tags: " .. tag_names(spr)) end
    if find_tag(spr, ARG.new_tag) ~= nil then error("Tag '" .. ARG.new_tag .. "' already exists") end
    local f1, f2 = src.fromFrame.frameNumber, src.toFrame.frameNumber
    local start = #spr.frames + 1
    local snap = snapshot_tags(spr)
    local layers = leaf_layers(spr.layers)
    app.transaction(function()
      for i = f1, f2 do
        local fr = spr:newEmptyFrame(#spr.frames + 1)
        fr.duration = spr.frames[i].duration
        for _, lyr in ipairs(layers) do
          local cel = lyr:cel(i)
          if cel ~= nil then
            if lyr.isTilemap then error("Cannot mirror tilemap layer '" .. lyr.name .. "'") end
            local img = cel.image
            local out = Image(img.spec)
            out:clear()
            local w, h = img.width, img.height
            for yy = 0, h - 1 do
              for xx = 0, w - 1 do
                local px = img:getPixel(xx, yy)
                if ARG.horizontal then out:drawPixel(w - 1 - xx, yy, px)
                else out:drawPixel(xx, h - 1 - yy, px) end
              end
            end
            local pos = cel.position
            local nx, ny = pos.x, pos.y
            if ARG.horizontal then nx = spr.width - pos.x - w else ny = spr.height - pos.y - h end
            spr:newCel(lyr, fr, out, Point(nx, ny))
          end
        end
      end
      restore_tags(snap)
      local tg = spr:newTag(start, #spr.frames)
      tg.name = ARG.new_tag
      tg.aniDir = src.aniDir
    end)
    save_sprite(spr)
    RESULT = { ok = true, filename = spr.filename, tag = ARG.new_tag,
               from = start, to = #spr.frames, source = { from = f1, to = f2 },
               sprite = sprite_info(spr) }
    """
    return run_lua(body, args)


@mcp.tool()
def copy_frames_from(
    filename: str,
    source: str,
    source_tag: str | None = None,
    from_frame: int | None = None,
    to_frame: int | None = None,
    layer: str | int | None = None,
    new_tag: str | None = None,
) -> dict:
    """Append frames from another sprite file, flattened onto one layer of this sprite.

    Use it to start every character from a shared base body or animation. The
    source frames are composited (all visible layers) and placed on `layer` of
    `filename`, keeping each frame's duration. If this sprite has a single empty
    frame (a fresh file), the first copied frame fills it instead of leaving a
    blank frame in front.

    Args:
        source: The .aseprite file to copy from (same width, height and colour mode).
        source_tag: Copy this tag's frames. Or give from_frame/to_frame (1-based,
            inclusive). With neither, every frame is copied.
        layer: Destination layer name or 1-based index (default: top layer).
        new_tag: Optionally tag the copied frames with this name (must not exist yet).
    """
    if source_tag is not None and (from_frame is not None or to_frame is not None):
        raise ValueError("Give source_tag or from_frame/to_frame, not both.")
    args = {
        "dst": lua_path(resolve_path(filename)),
        "src": lua_path(resolve_path(source)),
        "source_tag": source_tag,
        "from_frame": from_frame,
        "to_frame": to_frame,
        "layer": None if layer is None else str(layer),
        "new_tag": new_tag,
    }
    body = _HELPERS + """
    local src = open_sprite(ARG.src)
    local dst = open_sprite(ARG.dst)
    if src.width ~= dst.width or src.height ~= dst.height then
      error("Size mismatch: source is " .. src.width .. "x" .. src.height ..
            ", target is " .. dst.width .. "x" .. dst.height)
    end
    if src.colorMode ~= dst.colorMode then error("Colour modes differ; convert one sprite first") end
    local f1, f2 = 1, #src.frames
    if ARG.source_tag ~= nil then
      local t = find_tag(src, ARG.source_tag)
      if t == nil then error("Source has no tag '" .. ARG.source_tag .. "'. Tags: " .. tag_names(src)) end
      f1, f2 = t.fromFrame.frameNumber, t.toFrame.frameNumber
    else
      if ARG.from_frame ~= nil then f1 = clamp_frame(src, ARG.from_frame) end
      if ARG.to_frame ~= nil then f2 = clamp_frame(src, ARG.to_frame) end
      if f1 > f2 then error("from_frame must not be after to_frame") end
    end
    if ARG.new_tag ~= nil and find_tag(dst, ARG.new_tag) ~= nil then
      error("Tag '" .. ARG.new_tag .. "' already exists in the target")
    end
    local layer = find_layer(dst, ARG.layer)
    if layer.isGroup or layer.isTilemap then error("Target layer must be a normal image layer") end
    local reuse_first = false
    if #dst.frames == 1 then
      reuse_first = true
      for _, c in ipairs(dst.cels) do
        if c.image ~= nil and not c.image:isEmpty() then reuse_first = false end
      end
    end
    local snap = snapshot_tags(dst)
    local first_new = reuse_first and 1 or (#dst.frames + 1)
    app.sprite = dst
    app.transaction(function()
      for i = f1, f2 do
        local fr
        if reuse_first and i == f1 then fr = dst.frames[1]
        else fr = dst:newEmptyFrame(#dst.frames + 1) end
        fr.duration = src.frames[i].duration
        local img = Image(dst.spec)
        img:clear()
        img:drawSprite(src, i)
        local old = layer:cel(fr.frameNumber)
        if old ~= nil then dst:deleteCel(old) end
        dst:newCel(layer, fr, img, Point(0, 0))
      end
      restore_tags(snap)
      if ARG.new_tag ~= nil then
        local tg = dst:newTag(first_new, #dst.frames)
        tg.name = ARG.new_tag
      end
    end)
    save_sprite(dst)
    src:close()
    RESULT = { ok = true, filename = dst.filename, copied = f2 - f1 + 1,
               from = first_new, to = #dst.frames, reused_empty_first_frame = reuse_first,
               sprite = sprite_info(dst) }
    """
    return run_lua(body, args)


@mcp.tool()
def recolor_sprite(
    filename: str,
    mapping: dict[str, str],
    output: str | None = None,
    tolerance: int = 0,
    overwrite: bool = False,
) -> dict:
    """Replace colours across every layer, frame and palette entry of a sprite.

    Use it to turn one character template into another (new shirt, hair, skin).
    Each source colour is matched per channel within `tolerance` and replaced by
    its target; every pixel is mapped once from its original value, so swaps such
    as A->B and B->A work. With `output`, the recoloured sprite is saved as a new
    file and the original is left untouched.

    Args:
        mapping: Source colour -> target colour, e.g. {"#3060c0": "#c03030"}.
        output: Optional new .aseprite path. Without it the sprite is edited in place.
        tolerance: Per-channel match tolerance 0-255 (default exact).
        overwrite: Allow `output` to replace an existing file.

    Returns per-colour pixel counts; a source colour with zero matches is listed
    under `unmatched` so a typo is visible.
    """
    if not mapping:
        raise ValueError("mapping must contain at least one colour pair.")
    if len(mapping) > 256:
        raise ValueError("mapping may contain at most 256 colour pairs.")
    if not 0 <= int(tolerance) <= 255:
        raise ValueError("tolerance must be 0..255.")
    pairs = [{"src": k, "from": parse_color(k), "to": parse_color(v)} for k, v in mapping.items()]
    out_path = None
    if output is not None:
        out_path = ensure_output_path(output, overwrite=overwrite)
        if out_path.suffix.lower() not in {".aseprite", ".ase"}:
            raise ValueError("output must be an .aseprite or .ase file.")
    args = {
        "src": lua_path(resolve_path(filename)),
        "output": None if out_path is None else lua_path(out_path),
        "pairs": pairs,
        "tol": int(tolerance),
    }
    body = """
    local spr = open_sprite(ARG.src)
    local pal = spr.palettes[1]
    local function resolve(c)
      if c.index ~= nil then
        local pc = pal:getColor(math.floor(c.index))
        return { r = pc.red, g = pc.green, b = pc.blue, a = pc.alpha }
      end
      return { r = c.r, g = c.g, b = c.b, a = c.a or 255 }
    end
    local pairs_ = {}
    for i, p in ipairs(ARG.pairs) do
      pairs_[i] = { src = p.src, from = resolve(p["from"]), to = resolve(p.to), count = 0 }
    end
    local function match(r, g, b, a)
      for _, p in ipairs(pairs_) do
        local f = p["from"]
        if math.abs(r - f.r) <= ARG.tol and math.abs(g - f.g) <= ARG.tol
           and math.abs(b - f.b) <= ARG.tol and math.abs(a - f.a) <= ARG.tol then
          return p
        end
      end
      return nil
    end
    local palette_hits = 0
    app.transaction(function()
      for i = 0, #pal - 1 do
        local c = pal:getColor(i)
        local p = match(c.red, c.green, c.blue, c.alpha)
        if p ~= nil then
          pal:setColor(i, Color{ r = p.to.r, g = p.to.g, b = p.to.b, a = p.to.a })
          palette_hits = palette_hits + 1
        end
      end
      if spr.colorMode ~= ColorMode.INDEXED then
        local seen = {}
        for _, cel in ipairs(spr.cels) do
          if not cel.layer.isTilemap and cel.image ~= nil then
            local ok, id = pcall(function() return cel.image.id end)
            if not (ok and id ~= nil and seen[id]) then
              if ok and id ~= nil then seen[id] = true end
              local img = cel.image
              local out = img:clone()
              for yy = 0, img.height - 1 do
                for xx = 0, img.width - 1 do
                  local r, g, b, a = px_to_rgba(spr, img:getPixel(xx, yy))
                  if a > 0 then
                    local p = match(r, g, b, a)
                    if p ~= nil then
                      out:drawPixel(xx, yy, rgba_to_px(spr, p.to.r, p.to.g, p.to.b, p.to.a))
                      p.count = p.count + 1
                    end
                  end
                end
              end
              cel.image = out
            end
          end
        end
      end
    end)
    if ARG.output ~= nil then spr:saveAs(ARG.output) else save_sprite(spr) end
    local counts, unmatched = {}, {}
    for _, p in ipairs(pairs_) do
      counts[#counts + 1] = { color = p.src, pixels = p.count }
      if p.count == 0 and spr.colorMode ~= ColorMode.INDEXED then unmatched[#unmatched + 1] = p.src end
    end
    RESULT = { ok = true, filename = spr.filename, replaced = counts, unmatched = unmatched,
               palette_entries_changed = palette_hits, colorMode = colormode_name(spr.colorMode) }
    """
    return run_lua(body, args)
