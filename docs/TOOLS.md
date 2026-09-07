# Tool reference

Generated from the supported entry point. Frames are 1-based.

## add_drop_shadow

Add a hard drop shadow for a layer's artwork on a new layer placed beneath it.

    Args:
        layer: The layer casting the shadow.
        offset_x, offset_y: Shadow offset in pixels.
        color: Shadow colour (often semi-transparent black, the default).
        opacity: Opacity (0-255) of the shadow layer.
        frame: Frame to build the shadow for.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "offset_x": {
      "default": 1,
      "title": "Offset X",
      "type": "integer"
    },
    "offset_y": {
      "default": 1,
      "title": "Offset Y",
      "type": "integer"
    },
    "color": {
      "default": "#00000080",
      "title": "Color",
      "type": "string"
    },
    "opacity": {
      "default": 255,
      "title": "Opacity",
      "type": "integer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "add_drop_shadowArguments",
  "type": "object"
}
```

## add_frame

Append a new frame to the animation.

    Args:
        duration_ms: Frame duration in milliseconds (default 100).
        copy_from: If given (1-based), duplicate the content of that frame;
            otherwise the new frame is empty.

    Returns the new frame number and updated frame count.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "duration_ms": {
      "default": 100,
      "title": "Duration Ms",
      "type": "integer"
    },
    "copy_from": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Copy From"
    }
  },
  "required": [
    "filename"
  ],
  "title": "add_frameArguments",
  "type": "object"
}
```

## add_group_layer

Add a new (empty) group layer on top of the stack. Nest layers into it
    with add_layer(group=...) or move_layer(group=...).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "name"
  ],
  "title": "add_group_layerArguments",
  "type": "object"
}
```

## add_layer

Add a new (empty) normal layer on top of the stack.

    Args:
        name: Layer name.
        group: Optional name of an existing group layer to nest the new layer in.
        opacity: 0-255.
        blend_mode: normal, multiply, screen, overlay, darken, lighten,
            color_dodge, color_burn, hard_light, soft_light, difference,
            exclusion, hue, saturation, color, luminosity, addition, subtract, divide.
        visible: Initial visibility.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "group": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Group"
    },
    "opacity": {
      "default": 255,
      "title": "Opacity",
      "type": "integer"
    },
    "blend_mode": {
      "default": "normal",
      "title": "Blend Mode",
      "type": "string"
    },
    "visible": {
      "default": true,
      "title": "Visible",
      "type": "boolean"
    }
  },
  "required": [
    "filename",
    "name"
  ],
  "title": "add_layerArguments",
  "type": "object"
}
```

## add_outline

Add a pixel outline around the artwork on a layer.

    Args:
        color: Outline colour.
        thickness: Outline width in pixels (default 1).
        connectivity: 4 (orthogonal only) or 8 (includes diagonals, default).
        where: "outside" (grow into transparency, default) or "inside"
            (recolour the shape's border pixels).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "thickness": {
      "default": 1,
      "title": "Thickness",
      "type": "integer"
    },
    "connectivity": {
      "default": 8,
      "title": "Connectivity",
      "type": "integer"
    },
    "where": {
      "default": "outside",
      "title": "Where",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "color"
  ],
  "title": "add_outlineArguments",
  "type": "object"
}
```

## add_palette_color

Append a colour to the end of the palette.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "color": {
      "title": "Color",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "color"
  ],
  "title": "add_palette_colorArguments",
  "type": "object"
}
```

## add_reference_layer

Add a dimmed, locked layer holding a reference image to trace over.

    Args:
        image_file: The reference image/sprite.
        layer_name: Name for the new layer (default "reference").
        opacity: Layer opacity (0-255); dim it so your art stands out.
        scale_to_fit: Resize the reference to the canvas size (smooth).
        x, y: Placement when not scaling to fit.

    Exclude this layer from exports with ignore_layer="<layer_name>".


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "image_file": {
      "title": "Image File",
      "type": "string"
    },
    "layer_name": {
      "default": "reference",
      "title": "Layer Name",
      "type": "string"
    },
    "opacity": {
      "default": 128,
      "title": "Opacity",
      "type": "integer"
    },
    "scale_to_fit": {
      "default": false,
      "title": "Scale To Fit",
      "type": "boolean"
    },
    "x": {
      "default": 0,
      "title": "X",
      "type": "integer"
    },
    "y": {
      "default": 0,
      "title": "Y",
      "type": "integer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "image_file"
  ],
  "title": "add_reference_layerArguments",
  "type": "object"
}
```

## add_slice

Create a slice (named region) at (x, y, width, height).

    Args:
        center_*: Optional 9-patch center rectangle, **relative to the slice's
            top-left**. Provide all four to mark the stretchable middle.
        pivot_*: Optional pivot point (relative to the slice).
        color: Optional slice colour shown in the editor.
        data: Optional user data string.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "x": {
      "title": "X",
      "type": "integer"
    },
    "y": {
      "title": "Y",
      "type": "integer"
    },
    "width": {
      "title": "Width",
      "type": "integer"
    },
    "height": {
      "title": "Height",
      "type": "integer"
    },
    "center_x": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Center X"
    },
    "center_y": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Center Y"
    },
    "center_width": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Center Width"
    },
    "center_height": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Center Height"
    },
    "pivot_x": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Pivot X"
    },
    "pivot_y": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Pivot Y"
    },
    "color": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Color"
    },
    "data": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Data"
    }
  },
  "required": [
    "filename",
    "name",
    "x",
    "y",
    "width",
    "height"
  ],
  "title": "add_sliceArguments",
  "type": "object"
}
```

## add_tag

Create an animation tag spanning frames [from_frame, to_frame] (1-based).

    direction: "forward" (default), "reverse", "pingpong", or "pingpong_reverse".
    color: optional tag colour (shown in the timeline).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "from_frame": {
      "title": "From Frame",
      "type": "integer"
    },
    "to_frame": {
      "title": "To Frame",
      "type": "integer"
    },
    "direction": {
      "default": "forward",
      "title": "Direction",
      "type": "string"
    },
    "color": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Color"
    }
  },
  "required": [
    "filename",
    "name",
    "from_frame",
    "to_frame"
  ],
  "title": "add_tagArguments",
  "type": "object"
}
```

## add_tile

Add a new tile to the layer's tileset (optionally filled with a solid colour).
    Returns the new tile's index.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "color": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Color"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "add_tileArguments",
  "type": "object"
}
```

## adjust_brightness_contrast

Adjust brightness (-255..255, additive) and contrast (-255..255) of a layer.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "brightness": {
      "default": 0,
      "title": "Brightness",
      "type": "integer"
    },
    "contrast": {
      "default": 0,
      "title": "Contrast",
      "type": "integer"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "adjust_brightness_contrastArguments",
  "type": "object"
}
```

## adjust_hue_saturation

Shift hue (degrees) and scale saturation/lightness (percent, -100..100).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "hue": {
      "default": 0,
      "title": "Hue",
      "type": "integer"
    },
    "saturation": {
      "default": 0,
      "title": "Saturation",
      "type": "integer"
    },
    "lightness": {
      "default": 0,
      "title": "Lightness",
      "type": "integer"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "adjust_hue_saturationArguments",
  "type": "object"
}
```

## apply_operations

Apply a list of edit operations to a sprite in one atomic, single-process batch.

    Each operation is `{"op": "<name>", "args": {...}}`. Supported ops (v1):
    add_layer, rename_layer, set_layer_visible, set_layer_opacity, remove_layer,
    add_frame, duplicate_frame, set_frame_duration, add_tag, remove_tag, set_pixel,
    draw_line, draw_rectangle, fill_rectangle, draw_ellipse, fill_ellipse, fill_layer,
    clear_layer, add_slice, remove_slice, replace_color. Ops run **in order against the
    same open sprite**, so later ops see earlier ones (e.g. add a layer then draw on it).

    Atomic: if any op fails the whole batch is rolled back and nothing is saved; the
    error names the failing op index. `dry_run=True` validates the op list and returns
    the plan **without launching Aseprite** (shape checks only — runtime issues like a
    missing layer surface on a real run).

    Returns a `workflow_manifest.v1` (kind "batch") with a per-op `operations` list.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "operations": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Operations",
      "type": "array"
    },
    "dry_run": {
      "default": false,
      "title": "Dry Run",
      "type": "boolean"
    }
  },
  "required": [
    "filename",
    "operations"
  ],
  "title": "apply_operationsArguments",
  "type": "object"
}
```

## ase_apply_and_preview

Atomically apply typed batch operations to a native master, then return state and a nearest-neighbour PNG. Save succeeds before preview; a preview failure is reported as saved, not rolled back.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "operations": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Operations",
      "type": "array"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "operations"
  ],
  "title": "ase_apply_and_previewArguments",
  "type": "object"
}
```

## ase_export_phaser

Validate a native master and export a new bundle directory: row sheet, Phaser hash atlas, per-frame animation timing, QA and loader JS. Reopen master and PNG, compare every decoded RGBA pixel before publishing. Existing directories are never overwritten.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "output_directory": {
      "title": "Output Directory",
      "type": "string"
    },
    "contract": {
      "additionalProperties": true,
      "title": "Contract",
      "type": "object"
    }
  },
  "required": [
    "filename",
    "output_directory",
    "contract"
  ],
  "title": "ase_export_phaserArguments",
  "type": "object"
}
```

## ase_preview_animation

Return a contact-sheet PNG of every frame using nearest-neighbour scaling, with native frame timing and tag metadata. This is a review sheet, not a claim of correct motion.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "scale": {
      "default": 4,
      "title": "Scale",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "ase_preview_animationArguments",
  "type": "object"
}
```

## ase_validate_asset_contract

Reopen a native master and check every frame: geometry, tags, alpha, palette, empty frames and optional per-tag foot/centre drift. Unknown contract fields are rejected. Art quality still needs visual review.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "contract": {
      "additionalProperties": true,
      "title": "Contract",
      "type": "object"
    }
  },
  "required": [
    "filename",
    "contract"
  ],
  "title": "ase_validate_asset_contractArguments",
  "type": "object"
}
```

## clear_layer

Erase the target layer/frame cel to full transparency.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "clear_layerArguments",
  "type": "object"
}
```

## convert_background_to_layer

Convert the Background layer back into a normal (transparent-capable) layer.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "convert_background_to_layerArguments",
  "type": "object"
}
```

## convert_layer_to_background

Convert a normal layer into the sprite's opaque Background layer.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "convert_layer_to_backgroundArguments",
  "type": "object"
}
```

## copy_cel

Copy a cel's image (and position) from one frame to another on the same layer.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "from_frame": {
      "title": "From Frame",
      "type": "integer"
    },
    "to_frame": {
      "title": "To Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "from_frame",
    "to_frame"
  ],
  "title": "copy_celArguments",
  "type": "object"
}
```

## create_character_sprite

Scaffold a character sprite project: a transparent canvas with a tidy layer
    stack (body + details), an auto-generated shading palette ramp from `base_color`,
    and (optionally) an outlined placeholder body to draw over.

    Returns a ``workflow_manifest.v1`` manifest (sprite summary, created files,
    palette, and suggested next actions).


```json
{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "width": {
      "default": 32,
      "title": "Width",
      "type": "integer"
    },
    "height": {
      "default": 32,
      "title": "Height",
      "type": "integer"
    },
    "base_color": {
      "default": "#3878c8",
      "title": "Base Color",
      "type": "string"
    },
    "with_placeholder": {
      "default": true,
      "title": "With Placeholder",
      "type": "boolean"
    }
  },
  "required": [
    "name"
  ],
  "title": "create_character_spriteArguments",
  "type": "object"
}
```

## create_icon_set

Scaffold an icon set: a grid sheet with `count` icon cells, each a placeholder
    inside a named slice (`icon_0`, `icon_1`, …) for easy atlas export.

    Returns a ``workflow_manifest.v1`` manifest (kind "icon_set"); the per-icon regions
    appear as slices under `sprite.slices`.


```json
{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "icon_size": {
      "default": 16,
      "title": "Icon Size",
      "type": "integer"
    },
    "count": {
      "default": 4,
      "title": "Count",
      "type": "integer"
    },
    "columns": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Columns"
    }
  },
  "required": [
    "name"
  ],
  "title": "create_icon_setArguments",
  "type": "object"
}
```

## create_rpg_item_sheet

Scaffold an RPG item sheet: a grid sheet with one named slice per item
    (default sword/shield/potion/coin/key/gem), each with a placeholder.

    Returns a ``workflow_manifest.v1`` manifest (kind "rpg_item_sheet"); item regions
    appear as slices (named after each item) under `sprite.slices`.


```json
{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "item_size": {
      "default": 16,
      "title": "Item Size",
      "type": "integer"
    },
    "items": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Items"
    },
    "columns": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Columns"
    }
  },
  "required": [
    "name"
  ],
  "title": "create_rpg_item_sheetArguments",
  "type": "object"
}
```

## create_sprite

Create a new sprite file and save it.

    Args:
        filename: Output path. Relative paths go in the workspace. Use a
            .aseprite/.ase extension to keep layers & frames editable.
        width, height: Canvas size in pixels (1-65535).
        color_mode: "rgb" (default), "indexed", or "gray".
        background: Optional fill colour for the first layer (e.g. "#1d2b53").
            Omit for a transparent canvas.
        overwrite: Replace `filename` if it already exists (default False = no-clobber).

    Returns the new sprite's structured info.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "width": {
      "title": "Width",
      "type": "integer"
    },
    "height": {
      "title": "Height",
      "type": "integer"
    },
    "color_mode": {
      "default": "rgb",
      "title": "Color Mode",
      "type": "string"
    },
    "background": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Background"
    },
    "overwrite": {
      "default": false,
      "title": "Overwrite",
      "type": "boolean"
    }
  },
  "required": [
    "filename",
    "width",
    "height"
  ],
  "title": "create_spriteArguments",
  "type": "object"
}
```

## create_tilemap_layer

Create a tilemap layer with an empty grid.

    Args:
        name: Layer name.
        tile_width, tile_height: Tile size in pixels (sets the sprite grid).
        columns, rows: Grid size in tiles (default: enough to cover the canvas).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "tile_width": {
      "default": 16,
      "title": "Tile Width",
      "type": "integer"
    },
    "tile_height": {
      "default": 16,
      "title": "Tile Height",
      "type": "integer"
    },
    "columns": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Columns"
    },
    "rows": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Rows"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "name"
  ],
  "title": "create_tilemap_layerArguments",
  "type": "object"
}
```

## create_tileset_project

Scaffold a tilemap project: a canvas sized columns×rows tiles, a tilemap layer,
    and a starter tileset (grass/dirt/water/stone by default, or your own
    [{"name","color"}] list). The grid is filled with the first tile to start.

    Returns a ``workflow_manifest.v1`` manifest with a tilemap block mapping tile
    names to their tileset indices.


```json
{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "tile_size": {
      "default": 16,
      "title": "Tile Size",
      "type": "integer"
    },
    "columns": {
      "default": 4,
      "title": "Columns",
      "type": "integer"
    },
    "rows": {
      "default": 4,
      "title": "Rows",
      "type": "integer"
    },
    "tiles": {
      "anyOf": [
        {
          "items": {
            "additionalProperties": true,
            "type": "object"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Tiles"
    }
  },
  "required": [
    "name"
  ],
  "title": "create_tileset_projectArguments",
  "type": "object"
}
```

## crop_sprite

Crop the canvas to the rectangle (x, y, width, height).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "x": {
      "title": "X",
      "type": "integer"
    },
    "y": {
      "title": "Y",
      "type": "integer"
    },
    "width": {
      "title": "Width",
      "type": "integer"
    },
    "height": {
      "title": "Height",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "x",
    "y",
    "width",
    "height"
  ],
  "title": "crop_spriteArguments",
  "type": "object"
}
```

## delete_cel

Delete a cel (the layer becomes empty at that frame).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "frame": {
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "frame"
  ],
  "title": "delete_celArguments",
  "type": "object"
}
```

## desaturate

Desaturate toward grayscale by `amount` percent (0-100).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "amount": {
      "default": 100,
      "title": "Amount",
      "type": "integer"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "desaturateArguments",
  "type": "object"
}
```

## draw_brush

Stamp a custom brush shape at a list of points.

    Args:
        brush: The brush as rows of characters. Any character other than space,
            '.', or '0' is a filled cell. e.g. a plus brush: ["010", "111", "010"].
        points: Positions to stamp at, list of {"x": int, "y": int}.
        color: Colour to stamp the brush in.
        anchor: "center" (default) or "topleft" — where each point sits in the brush.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "brush": {
      "items": {
        "type": "string"
      },
      "title": "Brush",
      "type": "array"
    },
    "points": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Points",
      "type": "array"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "anchor": {
      "default": "center",
      "title": "Anchor",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "brush",
    "points",
    "color"
  ],
  "title": "draw_brushArguments",
  "type": "object"
}
```

## draw_curve

Draw a quadratic Bézier curve from (x0,y0) to (x1,y1) bending toward the
    control point (control_x, control_y). `steps` controls smoothness.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "x0": {
      "title": "X0",
      "type": "integer"
    },
    "y0": {
      "title": "Y0",
      "type": "integer"
    },
    "control_x": {
      "title": "Control X",
      "type": "integer"
    },
    "control_y": {
      "title": "Control Y",
      "type": "integer"
    },
    "x1": {
      "title": "X1",
      "type": "integer"
    },
    "y1": {
      "title": "Y1",
      "type": "integer"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "steps": {
      "default": 32,
      "title": "Steps",
      "type": "integer"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "x0",
    "y0",
    "control_x",
    "control_y",
    "x1",
    "y1",
    "color"
  ],
  "title": "draw_curveArguments",
  "type": "object"
}
```

## draw_ellipse

Draw an ellipse centred at (center_x, center_y) with the given radii.

    For a circle, use the same value for radius_x and radius_y. filled=False
    draws a 1px outline. antialias smooths a *filled* ellipse with sub-pixel
    coverage (RGB sprites only; ignored otherwise).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "center_x": {
      "title": "Center X",
      "type": "integer"
    },
    "center_y": {
      "title": "Center Y",
      "type": "integer"
    },
    "radius_x": {
      "title": "Radius X",
      "type": "integer"
    },
    "radius_y": {
      "title": "Radius Y",
      "type": "integer"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "filled": {
      "default": false,
      "title": "Filled",
      "type": "boolean"
    },
    "antialias": {
      "default": false,
      "title": "Antialias",
      "type": "boolean"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "center_x",
    "center_y",
    "radius_x",
    "radius_y",
    "color"
  ],
  "title": "draw_ellipseArguments",
  "type": "object"
}
```

## draw_image_base64

Composite an inline base64-encoded PNG (or other image) onto a layer at (x, y).

    Useful for pasting externally generated artwork. `image_base64` may include a
    `data:image/png;base64,` prefix.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "image_base64": {
      "title": "Image Base64",
      "type": "string"
    },
    "x": {
      "title": "X",
      "type": "integer"
    },
    "y": {
      "title": "Y",
      "type": "integer"
    },
    "opacity": {
      "default": 255,
      "title": "Opacity",
      "type": "integer"
    },
    "blend_mode": {
      "default": "normal",
      "title": "Blend Mode",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "image_base64",
    "x",
    "y"
  ],
  "title": "draw_image_base64Arguments",
  "type": "object"
}
```

## draw_line

Draw a straight line from (x1,y1) to (x2,y2).

    Args:
        pixel_perfect: Remove L-shaped corner pixels for a clean 1px pixel-art line.
        antialias: Smooth (Xiaolin Wu) line with alpha blending — RGB sprites only;
            ignored on indexed/gray. Takes precedence over pixel_perfect.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "x1": {
      "title": "X1",
      "type": "integer"
    },
    "y1": {
      "title": "Y1",
      "type": "integer"
    },
    "x2": {
      "title": "X2",
      "type": "integer"
    },
    "y2": {
      "title": "Y2",
      "type": "integer"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "pixel_perfect": {
      "default": false,
      "title": "Pixel Perfect",
      "type": "boolean"
    },
    "antialias": {
      "default": false,
      "title": "Antialias",
      "type": "boolean"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "x1",
    "y1",
    "x2",
    "y2",
    "color"
  ],
  "title": "draw_lineArguments",
  "type": "object"
}
```

## draw_pixels

Plot individual pixels.

    Args:
        pixels: List of {"x": int, "y": int, "color": "#hex"?}. If a pixel omits
            "color", the shared `color` argument is used.
        color: Default colour for pixels that don't specify their own.
        layer: Target layer name or 1-based index (default: top layer).
        frame: Target frame, 1-based (default 1).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "pixels": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Pixels",
      "type": "array"
    },
    "color": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Color"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "pixels"
  ],
  "title": "draw_pixelsArguments",
  "type": "object"
}
```

## draw_polyline

Draw connected line segments through a list of points.

    points: list of {"x": int, "y": int}. Set closed=True to connect the last
    point back to the first (outline a polygon). pixel_perfect removes L-corner
    pixels across the whole path for a clean pixel-art outline.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "points": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Points",
      "type": "array"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "closed": {
      "default": false,
      "title": "Closed",
      "type": "boolean"
    },
    "pixel_perfect": {
      "default": false,
      "title": "Pixel Perfect",
      "type": "boolean"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "points",
    "color"
  ],
  "title": "draw_polylineArguments",
  "type": "object"
}
```

## draw_rectangle

Draw a rectangle. filled=False draws a 1px outline, True fills it.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "x": {
      "title": "X",
      "type": "integer"
    },
    "y": {
      "title": "Y",
      "type": "integer"
    },
    "width": {
      "title": "Width",
      "type": "integer"
    },
    "height": {
      "title": "Height",
      "type": "integer"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "filled": {
      "default": false,
      "title": "Filled",
      "type": "boolean"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "x",
    "y",
    "width",
    "height",
    "color"
  ],
  "title": "draw_rectangleArguments",
  "type": "object"
}
```

## draw_symmetric_pixels

Plot pixels together with their mirror image(s).

    mode: "horizontal" (mirror across vertical axis_x), "vertical" (across axis_y),
    or "both" (4-way radial symmetry). Axes default to the canvas centre.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "pixels": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Pixels",
      "type": "array"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "mode": {
      "default": "horizontal",
      "title": "Mode",
      "type": "string"
    },
    "axis_x": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Axis X"
    },
    "axis_y": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Axis Y"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "pixels",
    "color"
  ],
  "title": "draw_symmetric_pixelsArguments",
  "type": "object"
}
```

## draw_text

Draw text onto a layer at (x, y) in a single colour.

    Args:
        text: The string (supports "\n" for multiple lines).
        x, y: Top-left position of the text.
        color: Text colour.
        scale: Integer pixel-scaling of the rendered glyphs (default 1).
        font_path: Optional path to a .ttf/.otf font. If omitted, a built-in
            bitmap font is used (best for tiny pixel text).
        font_size: Point size when a TrueType font_path is given.
        spacing: Extra pixels between lines.
        threshold: 0-255 cutoff; pixels brighter than this are drawn (lower =
            heavier text). Keeps glyphs crisp (no anti-aliasing artefacts).

    Returns the standard draw result plus the rendered text's pixel size.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "text": {
      "title": "Text",
      "type": "string"
    },
    "x": {
      "title": "X",
      "type": "integer"
    },
    "y": {
      "title": "Y",
      "type": "integer"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "scale": {
      "default": 1,
      "title": "Scale",
      "type": "integer"
    },
    "font_path": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Font Path"
    },
    "font_size": {
      "default": 16,
      "title": "Font Size",
      "type": "integer"
    },
    "spacing": {
      "default": 1,
      "title": "Spacing",
      "type": "integer"
    },
    "threshold": {
      "default": 128,
      "title": "Threshold",
      "type": "integer"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "text",
    "x",
    "y",
    "color"
  ],
  "title": "draw_textArguments",
  "type": "object"
}
```

## duplicate_frame

Duplicate an existing frame (1-based); the copy is inserted after it.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "frame": {
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "frame"
  ],
  "title": "duplicate_frameArguments",
  "type": "object"
}
```

## duplicate_layer

Duplicate a layer (including its cels) as a new layer on top.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "duplicate_layerArguments",
  "type": "object"
}
```

## export_gif

Export the full animation as an animated GIF (honours frame durations & tags).

    overwrite: Replace `output` if it already exists (default False = no-clobber).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "output": {
      "title": "Output",
      "type": "string"
    },
    "scale": {
      "default": 1,
      "title": "Scale",
      "type": "integer"
    },
    "overwrite": {
      "default": false,
      "title": "Overwrite",
      "type": "boolean"
    }
  },
  "required": [
    "filename",
    "output"
  ],
  "title": "export_gifArguments",
  "type": "object"
}
```

## export_onion_skin

Export a frame with neighbouring frames ghosted behind it (onion skin).

    Args:
        frame: The in-focus frame (drawn fully opaque), 1-based.
        previous, next: How many earlier/later frames to ghost.
        ghost_opacity: Max opacity (0-255) of the nearest ghost; further frames fade.
        scale: Integer upscaling factor for the output PNG.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "frame": {
      "title": "Frame",
      "type": "integer"
    },
    "output": {
      "title": "Output",
      "type": "string"
    },
    "previous": {
      "default": 2,
      "title": "Previous",
      "type": "integer"
    },
    "next": {
      "default": 0,
      "title": "Next",
      "type": "integer"
    },
    "ghost_opacity": {
      "default": 80,
      "title": "Ghost Opacity",
      "type": "integer"
    },
    "scale": {
      "default": 4,
      "title": "Scale",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "frame",
    "output"
  ],
  "title": "export_onion_skinArguments",
  "type": "object"
}
```

## export_png

Export one frame as a flattened PNG.

    Args:
        output: Destination .png path.
        frame: Frame to export, 1-based (default 1).
        scale: Integer upscaling factor (default 1).
        overwrite: Replace `output` if it already exists (default False = no-clobber).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "output": {
      "title": "Output",
      "type": "string"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    },
    "scale": {
      "default": 1,
      "title": "Scale",
      "type": "integer"
    },
    "overwrite": {
      "default": false,
      "title": "Overwrite",
      "type": "boolean"
    }
  },
  "required": [
    "filename",
    "output"
  ],
  "title": "export_pngArguments",
  "type": "object"
}
```

## export_slice_metadata

Export every slice as engine-agnostic JSON (``aseprite_mcp.slice_metadata.v1``).

    Each slice becomes ``{name, type, id, bounds, pivot, nine_slice, color, data,
    raw_data}``. **Type detection:** a slice's user-data JSON ``type`` wins; otherwise the
    name convention ``<type>:<id>`` (recognized types: hitbox, hurtbox, collision, interact,
    pivot, origin, attach, spawn, nine_slice — anything else becomes ``"custom"``, never an
    error). ``id`` comes from the data ``id`` or the name's ``:<id>`` suffix. ``nine_slice``
    (Aseprite's 9-patch center) and ``pivot`` are emitted whenever the slice has them. Slice
    user-data that is valid JSON is parsed into ``data``; the raw string is kept in ``raw_data``.

    Args:
        output: Destination .json path. Defaults to ``<sprite>_slices.json`` beside the sprite.
        overwrite: Replace an existing file (default False = no-clobber).

    Returns a ``workflow_manifest.v1`` manifest (kind ``engine_metadata``).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "output": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Output"
    },
    "overwrite": {
      "default": false,
      "title": "Overwrite",
      "type": "boolean"
    }
  },
  "required": [
    "filename"
  ],
  "title": "export_slice_metadataArguments",
  "type": "object"
}
```

## export_spritesheet

Export frames into a single sprite-sheet image.

    Args:
        output: Destination sheet image (.png).
        sheet_type: one of horizontal, vertical, rows, columns, packed.
        scale: Integer upscaling factor.
        data_output: Optional .json path to also write frame/tag/slice metadata
            (JSON-array format) describing each frame's rectangle in the sheet.
        padding: Pixels of padding around/between frames.
        layer: Only include this layer.
        ignore_layer: Exclude this layer (e.g. a "reference" layer).
        split_layers: Lay out each layer as separate cels in the sheet.
        split_tags: Treat each tag as a separate set in the sheet.
        overwrite: Replace existing output(s) (default False = no-clobber). When
            data_output is given, both files are checked before anything is written.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "output": {
      "title": "Output",
      "type": "string"
    },
    "sheet_type": {
      "default": "packed",
      "title": "Sheet Type",
      "type": "string"
    },
    "scale": {
      "default": 1,
      "title": "Scale",
      "type": "integer"
    },
    "data_output": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Data Output"
    },
    "padding": {
      "default": 0,
      "title": "Padding",
      "type": "integer"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "ignore_layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Ignore Layer"
    },
    "split_layers": {
      "default": false,
      "title": "Split Layers",
      "type": "boolean"
    },
    "split_tags": {
      "default": false,
      "title": "Split Tags",
      "type": "boolean"
    },
    "overwrite": {
      "default": false,
      "title": "Overwrite",
      "type": "boolean"
    }
  },
  "required": [
    "filename",
    "output"
  ],
  "title": "export_spritesheetArguments",
  "type": "object"
}
```

## export_tag_gif

Export only the frames of a named animation tag as an animated GIF.

    overwrite: Replace `output` if it already exists (default False = no-clobber).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "tag": {
      "title": "Tag",
      "type": "string"
    },
    "output": {
      "title": "Output",
      "type": "string"
    },
    "scale": {
      "default": 1,
      "title": "Scale",
      "type": "integer"
    },
    "overwrite": {
      "default": false,
      "title": "Overwrite",
      "type": "boolean"
    }
  },
  "required": [
    "filename",
    "tag",
    "output"
  ],
  "title": "export_tag_gifArguments",
  "type": "object"
}
```

## extract_palette

Extract the unique colours used in a sprite (or another image).

    Args:
        from_image: Optional image/sprite to scan instead of `filename`.
        set_as_palette: Apply the extracted colours as `filename`'s palette.
        include_alpha: Treat differing alpha as distinct colours (default off).
        max_colors: Error out if more unique colours than this are found.

    Returns the list of "#RRGGBBAA" colours found.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "from_image": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "From Image"
    },
    "set_as_palette": {
      "default": true,
      "title": "Set As Palette",
      "type": "boolean"
    },
    "include_alpha": {
      "default": false,
      "title": "Include Alpha",
      "type": "boolean"
    },
    "max_colors": {
      "default": 256,
      "title": "Max Colors",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "extract_paletteArguments",
  "type": "object"
}
```

## fill_area

Flood fill (paint bucket): replace the contiguous region of matching
    colour starting at (x,y) on the target layer with `color`.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "x": {
      "title": "X",
      "type": "integer"
    },
    "y": {
      "title": "Y",
      "type": "integer"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "x",
    "y",
    "color"
  ],
  "title": "fill_areaArguments",
  "type": "object"
}
```

## fill_checkerboard

Fill a region with a 2-colour checkerboard of `size`-pixel squares.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "color1": {
      "title": "Color1",
      "type": "string"
    },
    "color2": {
      "title": "Color2",
      "type": "string"
    },
    "size": {
      "default": 1,
      "title": "Size",
      "type": "integer"
    },
    "x": {
      "default": 0,
      "title": "X",
      "type": "integer"
    },
    "y": {
      "default": 0,
      "title": "Y",
      "type": "integer"
    },
    "width": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Width"
    },
    "height": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Height"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "color1",
    "color2"
  ],
  "title": "fill_checkerboardArguments",
  "type": "object"
}
```

## fill_gradient

Fill a region with a gradient.

    Args:
        colors: 2+ colour stops, e.g. ["#000000", "#ff004d", "#ffec27"], spread
            evenly. For dither=True, provide exactly 2 colours.
        gradient_type: "linear" or "radial".
        angle: Direction in degrees for linear gradients (0 = left->right).
        dither: Ordered (Bayer 4x4) dithering between 2 colours instead of smooth
            interpolation — great for limited palettes / retro looks.
        x, y, width, height: Region (defaults to the whole canvas).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "colors": {
      "items": {
        "type": "string"
      },
      "title": "Colors",
      "type": "array"
    },
    "gradient_type": {
      "default": "linear",
      "title": "Gradient Type",
      "type": "string"
    },
    "angle": {
      "default": 0.0,
      "title": "Angle",
      "type": "number"
    },
    "dither": {
      "default": false,
      "title": "Dither",
      "type": "boolean"
    },
    "x": {
      "default": 0,
      "title": "X",
      "type": "integer"
    },
    "y": {
      "default": 0,
      "title": "Y",
      "type": "integer"
    },
    "width": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Width"
    },
    "height": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Height"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "colors"
  ],
  "title": "fill_gradientArguments",
  "type": "object"
}
```

## fill_layer

Fill the entire target layer/frame cel with a solid colour.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "color"
  ],
  "title": "fill_layerArguments",
  "type": "object"
}
```

## fill_tile

Fill an existing tile's artwork with a solid colour.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "tile_index": {
      "title": "Tile Index",
      "type": "integer"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "tile_index",
    "color"
  ],
  "title": "fill_tileArguments",
  "type": "object"
}
```

## fill_tilemap

Fill the entire tilemap grid with a single tile index.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "tile_index": {
      "title": "Tile Index",
      "type": "integer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "tile_index"
  ],
  "title": "fill_tilemapArguments",
  "type": "object"
}
```

## flatten_sprite

Flatten all layers into a single layer (in place).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "flatten_spriteArguments",
  "type": "object"
}
```

## flip_sprite

Flip the entire sprite. direction: "horizontal" or "vertical".

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "direction": {
      "default": "horizontal",
      "title": "Direction",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "flip_spriteArguments",
  "type": "object"
}
```

## generate_ramp

Generate a shading ramp from a base colour (dark -> light).

    Produces `steps` colours by varying lightness across `light_range`, optionally
    rotating hue by `hue_shift` total degrees across the ramp (classic pixel-art
    hue shifting: cool shadows / warm highlights) and scaling saturation by
    `saturation_shift` percent across the ramp.

    Args:
        filename: If set with apply, write the ramp into that sprite's palette.
        apply: "none" (just return), "append" (add to palette), or "replace".

    Returns the ramp as a list of "#RRGGBB" colours (darkest first).


```json
{
  "properties": {
    "base_color": {
      "title": "Base Color",
      "type": "string"
    },
    "steps": {
      "default": 5,
      "title": "Steps",
      "type": "integer"
    },
    "hue_shift": {
      "default": 0.0,
      "title": "Hue Shift",
      "type": "number"
    },
    "saturation_shift": {
      "default": 0.0,
      "title": "Saturation Shift",
      "type": "number"
    },
    "light_range": {
      "default": 0.6,
      "title": "Light Range",
      "type": "number"
    },
    "filename": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Filename"
    },
    "apply": {
      "default": "none",
      "title": "Apply",
      "type": "string"
    }
  },
  "required": [
    "base_color"
  ],
  "title": "generate_rampArguments",
  "type": "object"
}
```

## get_cel

Inspect a cel: whether it exists, its position, bounds, and opacity.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "get_celArguments",
  "type": "object"
}
```

## get_palette

Return the sprite's palette as a list of "#RRGGBBAA" colours.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "get_paletteArguments",
  "type": "object"
}
```

## get_pixels

Read the composited (all visible layers) pixel colours of a region.

    Returns rows of "#RRGGBBAA" hex strings. The region is capped at 64x64
    (4096 pixels) per call to keep responses small — read in tiles for bigger areas.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "x": {
      "default": 0,
      "title": "X",
      "type": "integer"
    },
    "y": {
      "default": 0,
      "title": "Y",
      "type": "integer"
    },
    "width": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Width"
    },
    "height": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Height"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "get_pixelsArguments",
  "type": "object"
}
```

## get_sprite_info

Return structured info about a sprite: size, colour mode, frames (with
    durations), the full layer tree (names, opacity, blend mode, visibility),
    animation tags, and palette size.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "get_sprite_infoArguments",
  "type": "object"
}
```

## get_tilemap

Read the tilemap as a 2D grid of tile indices, plus tile size and count.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "get_tilemapArguments",
  "type": "object"
}
```

## gui_available

Check whether the Aseprite GUI can be launched (executable resolvable).

```json
{
  "properties": {},
  "title": "gui_availableArguments",
  "type": "object"
}
```

## health_check

Run a self-test of the server and its Aseprite integration.

    Returns whether Aseprite was found, its version, the resolved workspace, the
    number of registered tools, and whether a real create-sprite + export-PNG
    round-trip succeeds. `ok` is True only if the full round-trip works.


```json
{
  "properties": {},
  "title": "health_checkArguments",
  "type": "object"
}
```

## import_image

Create an editable .aseprite sprite from a flat image (.png/.bmp/.jpg/...).

    Args:
        input_image: Source raster image.
        output: Destination .aseprite path.


```json
{
  "properties": {
    "input_image": {
      "title": "Input Image",
      "type": "string"
    },
    "output": {
      "title": "Output",
      "type": "string"
    }
  },
  "required": [
    "input_image",
    "output"
  ],
  "title": "import_imageArguments",
  "type": "object"
}
```

## import_reference_sequence

Import a sequence of images as per-frame references for rotoscoping.

    Each image is placed on its own frame in a single dimmed, locked layer
    (frames are created as needed). Draw your animation on a layer above, then
    exclude this layer at export with ignore_layer="<layer_name>".


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "images": {
      "items": {
        "type": "string"
      },
      "title": "Images",
      "type": "array"
    },
    "layer_name": {
      "default": "rotoscope",
      "title": "Layer Name",
      "type": "string"
    },
    "opacity": {
      "default": 128,
      "title": "Opacity",
      "type": "integer"
    },
    "scale_to_fit": {
      "default": false,
      "title": "Scale To Fit",
      "type": "boolean"
    },
    "start_frame": {
      "default": 1,
      "title": "Start Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "images"
  ],
  "title": "import_reference_sequenceArguments",
  "type": "object"
}
```

## invert_colors

Invert the RGB colours of a layer's pixels (alpha preserved).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "invert_colorsArguments",
  "type": "object"
}
```

## list_slices

List all slices in the sprite with their bounds, center, and pivot.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "list_slicesArguments",
  "type": "object"
}
```

## list_sprites

List sprite/image files in the workspace directory.

```json
{
  "properties": {},
  "title": "list_spritesArguments",
  "type": "object"
}
```

## load_palette

Load a palette from a file (.gpl, .pal, .aseprite, .png, ...) and apply it.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "palette_file": {
      "title": "Palette File",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "palette_file"
  ],
  "title": "load_paletteArguments",
  "type": "object"
}
```

## make_4_frame_idle_animation

Turn a single-frame sprite into a 4-frame idle "bob" loop.

    Duplicates frame 1 to 4 frames, nudges `layer` down by `bob_pixels` on frames 2
    and 4 for a subtle bob, sets uniform durations, and adds a looping tag.

    Returns a ``workflow_manifest.v1`` manifest (sprite summary + animation block).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "default": "body",
      "title": "Layer",
      "type": "string"
    },
    "frame_duration_ms": {
      "default": 150,
      "title": "Frame Duration Ms",
      "type": "integer"
    },
    "bob_pixels": {
      "default": 1,
      "title": "Bob Pixels",
      "type": "integer"
    },
    "tag_name": {
      "default": "idle",
      "title": "Tag Name",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "make_4_frame_idle_animationArguments",
  "type": "object"
}
```

## make_8_direction_walk_template

Scaffold an 8-direction walk-cycle template on an existing sprite: enough frames
    for `frames_per_direction` per direction, with one animation tag per direction
    (N, NE, E, SE, S, SW, W, NW by default).

    Frames are placeholders to draw over. Returns a ``workflow_manifest.v1`` manifest
    (kind "walk_template") with an animation block listing the directions/tags.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "frames_per_direction": {
      "default": 4,
      "title": "Frames Per Direction",
      "type": "integer"
    },
    "frame_duration_ms": {
      "default": 120,
      "title": "Frame Duration Ms",
      "type": "integer"
    },
    "directions": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Directions"
    }
  },
  "required": [
    "filename"
  ],
  "title": "make_8_direction_walk_templateArguments",
  "type": "object"
}
```

## merge_layer_down

Merge a layer down into the layer directly beneath it.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "merge_layer_downArguments",
  "type": "object"
}
```

## mirror_layer

Mirror one half of a layer onto the other (build symmetric artwork).

    Args:
        direction: "horizontal" (reflect left<->right) or "vertical" (top<->bottom).
        source_side: which half is copied: "first" (left/top) or "second" (right/bottom).
        axis: mirror line position (x for horizontal, y for vertical); default = centre.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "direction": {
      "default": "horizontal",
      "title": "Direction",
      "type": "string"
    },
    "source_side": {
      "default": "first",
      "title": "Source Side",
      "type": "string"
    },
    "axis": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Axis"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "mirror_layerArguments",
  "type": "object"
}
```

## move_layer

Reorder a layer to a new 1-based stack index (1 = bottom-most).

    Note: moves within the layer's current parent group.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "to_index": {
      "title": "To Index",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "to_index"
  ],
  "title": "move_layerArguments",
  "type": "object"
}
```

## paint_tile_pixels

Draw individual pixels into a tile's artwork (tile-local coordinates).

    pixels: list of {"x", "y", "color"?}; falls back to the shared `color`.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "tile_index": {
      "title": "Tile Index",
      "type": "integer"
    },
    "pixels": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Pixels",
      "type": "array"
    },
    "color": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Color"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "tile_index",
    "pixels"
  ],
  "title": "paint_tile_pixelsArguments",
  "type": "object"
}
```

## plan_asset_spec

Return the ordered build steps for an asset spec **without launching Aseprite**.

    The pure dry-run: each step is ``{tool, args, purpose}`` naming the existing tool that
    `build_asset_from_spec` would call. Returns a ``workflow_manifest.v1`` (kind
    ``asset_spec``) with the steps under `plan` and `dry_run=true`. If the spec is invalid,
    returns the validation report instead.


```json
{
  "properties": {
    "spec": {
      "additionalProperties": true,
      "title": "Spec",
      "type": "object"
    }
  },
  "required": [
    "spec"
  ],
  "title": "plan_asset_specArguments",
  "type": "object"
}
```

## remove_frame

Delete a frame (1-based). The sprite must have more than one frame.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "frame": {
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "frame"
  ],
  "title": "remove_frameArguments",
  "type": "object"
}
```

## remove_layer

Delete a layer (or group, including its children) by name or 1-based index.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "remove_layerArguments",
  "type": "object"
}
```

## remove_slice

Delete a slice by name.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "name"
  ],
  "title": "remove_sliceArguments",
  "type": "object"
}
```

## remove_tag

Delete an animation tag by name.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "name"
  ],
  "title": "remove_tagArguments",
  "type": "object"
}
```

## rename_layer

Rename a layer.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "new_name": {
      "title": "New Name",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "layer",
    "new_name"
  ],
  "title": "rename_layerArguments",
  "type": "object"
}
```

## render_preview

Render a single frame to a PNG and return it as an image you can view.

    Use this to *see* your work. frame is 1-based; scale enlarges small sprites
    (default 8x) so individual pixels are visible.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    },
    "scale": {
      "default": 8,
      "title": "Scale",
      "type": "integer"
    }
  },
  "required": [
    "filename"
  ],
  "title": "render_previewArguments",
  "type": "object"
}
```

## replace_color

Replace every pixel matching `from_color` (within `tolerance` per channel)
    with `to_color`, on the chosen layer + frame.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "from_color": {
      "title": "From Color",
      "type": "string"
    },
    "to_color": {
      "title": "To Color",
      "type": "string"
    },
    "tolerance": {
      "default": 0,
      "title": "Tolerance",
      "type": "integer"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "from_color",
    "to_color"
  ],
  "title": "replace_colorArguments",
  "type": "object"
}
```

## resize_canvas

Resize the canvas WITHOUT scaling the artwork (adds or trims space).

    anchor controls where existing content sits in the new canvas:
    "top_left" (default) or "center".


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "width": {
      "title": "Width",
      "type": "integer"
    },
    "height": {
      "title": "Height",
      "type": "integer"
    },
    "anchor": {
      "default": "top_left",
      "title": "Anchor",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "width",
    "height"
  ],
  "title": "resize_canvasArguments",
  "type": "object"
}
```

## resize_palette

Resize the palette to `size` entries (new entries are black).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "size": {
      "title": "Size",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "size"
  ],
  "title": "resize_paletteArguments",
  "type": "object"
}
```

## rotate_sprite

Rotate the entire sprite by 90, 180, or 270 degrees (clockwise).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "angle": {
      "title": "Angle",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "angle"
  ],
  "title": "rotate_spriteArguments",
  "type": "object"
}
```

## save_sprite_as

Save a copy of a sprite under a new path (optionally flattened).

    The original file is left untouched. Useful for exporting an editable
    .aseprite to another .aseprite, or snapshotting a version.

    overwrite: Replace `new_filename` if it already exists (default False = no-clobber).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "new_filename": {
      "title": "New Filename",
      "type": "string"
    },
    "flatten": {
      "default": false,
      "title": "Flatten",
      "type": "boolean"
    },
    "overwrite": {
      "default": false,
      "title": "Overwrite",
      "type": "boolean"
    }
  },
  "required": [
    "filename",
    "new_filename"
  ],
  "title": "save_sprite_asArguments",
  "type": "object"
}
```

## scale_sprite

Scale the whole sprite (artwork included).

    Provide either `factor` (e.g. 2.0 to double) OR explicit `width`/`height`.
    method: "nearest" (crisp pixels, default) or "bilinear" (smooth).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "factor": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Factor"
    },
    "width": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Width"
    },
    "height": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Height"
    },
    "method": {
      "default": "nearest",
      "title": "Method",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "scale_spriteArguments",
  "type": "object"
}
```

## set_all_frame_durations

Set every frame's duration in milliseconds (uniform animation speed).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "duration_ms": {
      "title": "Duration Ms",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "duration_ms"
  ],
  "title": "set_all_frame_durationsArguments",
  "type": "object"
}
```

## set_cel_opacity

Set a cel's opacity (0-255).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "frame": {
      "title": "Frame",
      "type": "integer"
    },
    "opacity": {
      "title": "Opacity",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "frame",
    "opacity"
  ],
  "title": "set_cel_opacityArguments",
  "type": "object"
}
```

## set_cel_position

Move a cel's image to position (x, y) within the canvas.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "frame": {
      "title": "Frame",
      "type": "integer"
    },
    "x": {
      "title": "X",
      "type": "integer"
    },
    "y": {
      "title": "Y",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "frame",
    "x",
    "y"
  ],
  "title": "set_cel_positionArguments",
  "type": "object"
}
```

## set_color_mode

Convert a sprite between colour modes ("rgb", "indexed", "gray").

    When converting to "indexed", dithering can be "none", "ordered", or
    "old" to control how RGB colours are mapped to the palette.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "color_mode": {
      "title": "Color Mode",
      "type": "string"
    },
    "dithering": {
      "default": "none",
      "title": "Dithering",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "color_mode"
  ],
  "title": "set_color_modeArguments",
  "type": "object"
}
```

## set_frame_duration

Set a single frame's duration in milliseconds (1-based frame).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "frame": {
      "title": "Frame",
      "type": "integer"
    },
    "duration_ms": {
      "title": "Duration Ms",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "frame",
    "duration_ms"
  ],
  "title": "set_frame_durationArguments",
  "type": "object"
}
```

## set_layer_properties

Update one or more layer properties. Only the arguments you pass are changed.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "opacity": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Opacity"
    },
    "blend_mode": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Blend Mode"
    },
    "visible": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Visible"
    },
    "editable": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Editable"
    },
    "name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Name"
    }
  },
  "required": [
    "filename",
    "layer"
  ],
  "title": "set_layer_propertiesArguments",
  "type": "object"
}
```

## set_palette

Replace the entire palette with the given list of colours.

    colors: list of colour strings, e.g. ["#000000", "#ffffff", "255,0,0"].


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "colors": {
      "items": {
        "type": "string"
      },
      "title": "Colors",
      "type": "array"
    }
  },
  "required": [
    "filename",
    "colors"
  ],
  "title": "set_paletteArguments",
  "type": "object"
}
```

## set_palette_color

Set a single palette entry by index (0-based). Grows the palette if needed.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "index": {
      "title": "Index",
      "type": "integer"
    },
    "color": {
      "title": "Color",
      "type": "string"
    }
  },
  "required": [
    "filename",
    "index",
    "color"
  ],
  "title": "set_palette_colorArguments",
  "type": "object"
}
```

## set_slice

Update an existing slice's bounds, name, colour, or data.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "x": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "X"
    },
    "y": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Y"
    },
    "width": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Width"
    },
    "height": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Height"
    },
    "new_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "New Name"
    },
    "color": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Color"
    },
    "data": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Data"
    }
  },
  "required": [
    "filename",
    "name"
  ],
  "title": "set_sliceArguments",
  "type": "object"
}
```

## set_tag

Update an existing tag. Only the arguments you pass are changed.

    Note: changing from_frame/to_frame recreates the tag in place to update its
    range reliably across Aseprite versions.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "from_frame": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "From Frame"
    },
    "to_frame": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "To Frame"
    },
    "new_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "New Name"
    },
    "direction": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Direction"
    },
    "color": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Color"
    }
  },
  "required": [
    "filename",
    "name"
  ],
  "title": "set_tagArguments",
  "type": "object"
}
```

## set_tile

Place a tile (by tileset index, 0 = empty) at grid cell (column, row).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "column": {
      "title": "Column",
      "type": "integer"
    },
    "row": {
      "title": "Row",
      "type": "integer"
    },
    "tile_index": {
      "title": "Tile Index",
      "type": "integer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "column",
    "row",
    "tile_index"
  ],
  "title": "set_tileArguments",
  "type": "object"
}
```

## set_tiles

Place many tiles at once. tiles: list of {"column", "row", "index"}.

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "layer": {
      "title": "Layer",
      "type": "string"
    },
    "tiles": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Tiles",
      "type": "array"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "layer",
    "tiles"
  ],
  "title": "set_tilesArguments",
  "type": "object"
}
```

## set_transparent_color

Set which palette index is treated as transparent (indexed sprites only).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "index": {
      "title": "Index",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "index"
  ],
  "title": "set_transparent_colorArguments",
  "type": "object"
}
```

## sort_palette

Sort the palette by "hue", "luminance" (default), "saturation", or "value".

    For indexed sprites the pixel indices are remapped so the image looks identical.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "by": {
      "default": "luminance",
      "title": "By",
      "type": "string"
    },
    "reverse": {
      "default": false,
      "title": "Reverse",
      "type": "boolean"
    }
  },
  "required": [
    "filename"
  ],
  "title": "sort_paletteArguments",
  "type": "object"
}
```

## stamp_file

Composite another image/sprite file onto a layer at (x, y).

    Args:
        source: Path to a .aseprite/.png/.bmp/... to stamp in.
        x, y: Top-left placement on the target canvas.
        source_frame: Which frame of the source to use (1-based).
        opacity: 0-255.
        blend_mode: Blend mode for compositing (normal, multiply, …).


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "source": {
      "title": "Source",
      "type": "string"
    },
    "x": {
      "title": "X",
      "type": "integer"
    },
    "y": {
      "title": "Y",
      "type": "integer"
    },
    "source_frame": {
      "default": 1,
      "title": "Source Frame",
      "type": "integer"
    },
    "opacity": {
      "default": 255,
      "title": "Opacity",
      "type": "integer"
    },
    "blend_mode": {
      "default": "normal",
      "title": "Blend Mode",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "source",
    "x",
    "y"
  ],
  "title": "stamp_fileArguments",
  "type": "object"
}
```

## stamp_pattern

Tile an image/sprite across a region to fill it with a repeating pattern.

    Args:
        source: Image/sprite to tile.
        x, y, width, height: Region to fill (defaults to the whole canvas).
        spacing_x, spacing_y: Gap between tiles.
        opacity, blend_mode: Compositing of each tile.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "source": {
      "title": "Source",
      "type": "string"
    },
    "x": {
      "default": 0,
      "title": "X",
      "type": "integer"
    },
    "y": {
      "default": 0,
      "title": "Y",
      "type": "integer"
    },
    "width": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Width"
    },
    "height": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Height"
    },
    "spacing_x": {
      "default": 0,
      "title": "Spacing X",
      "type": "integer"
    },
    "spacing_y": {
      "default": 0,
      "title": "Spacing Y",
      "type": "integer"
    },
    "opacity": {
      "default": 255,
      "title": "Opacity",
      "type": "integer"
    },
    "blend_mode": {
      "default": "normal",
      "title": "Blend Mode",
      "type": "string"
    },
    "layer": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Layer"
    },
    "frame": {
      "default": 1,
      "title": "Frame",
      "type": "integer"
    }
  },
  "required": [
    "filename",
    "source"
  ],
  "title": "stamp_patternArguments",
  "type": "object"
}
```

## trim_sprite

Auto-crop the canvas to the bounding box of all non-transparent content
    (across every frame).

```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    }
  },
  "required": [
    "filename"
  ],
  "title": "trim_spriteArguments",
  "type": "object"
}
```

## validate_asset_spec

Validate an ``aseprite_mcp.asset_spec.v1`` document (does the *spec* make sense?).

    Checks the schema, kind, canvas, per-kind fields, palette, layers, animations
    (`frame_count`, not `frames`), slices, and export formats. Returns a
    ``workflow_manifest.v1`` (kind ``asset_spec``) with a `validation` block
    `{passed, checks, errors, warnings}`. This does **not** check a finished sprite against
    the spec — that's a separate future tool.


```json
{
  "properties": {
    "spec": {
      "additionalProperties": true,
      "title": "Spec",
      "type": "object"
    }
  },
  "required": [
    "spec"
  ],
  "title": "validate_asset_specArguments",
  "type": "object"
}
```

## validate_sprite_for_game_export

Check whether a sprite is game-ready against the criteria you specify.

    Runs a series of checks — does the file open, do dimensions match (exactly or as
    a tile multiple), is the colour mode allowed, are frame counts / required animation
    tags present, is the background transparent, is the palette within budget, do
    expected export files exist, and is sprite-sheet metadata readable — plus soft
    warnings for oversized canvases, missing tags, and default/blank layer names.

    All criteria are optional; only the ones you pass are enforced. Returns a
    ``workflow_manifest.v1`` manifest (kind "validation") with a `validation` section
    `{passed, checks[], errors[], warnings[]}`. `validation.passed` is the verdict;
    `ok` just means the check ran.


```json
{
  "properties": {
    "filename": {
      "title": "Filename",
      "type": "string"
    },
    "expected_width": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Width"
    },
    "expected_height": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Height"
    },
    "tile_multiple": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Tile Multiple"
    },
    "allowed_color_modes": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Allowed Color Modes"
    },
    "min_frames": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Min Frames"
    },
    "max_frames": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Frames"
    },
    "required_tags": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Required Tags"
    },
    "require_transparent_background": {
      "default": false,
      "title": "Require Transparent Background",
      "type": "boolean"
    },
    "max_palette_size": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Max Palette Size"
    },
    "expected_exports": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Expected Exports"
    },
    "spritesheet_data": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Spritesheet Data"
    }
  },
  "required": [
    "filename"
  ],
  "title": "validate_sprite_for_game_exportArguments",
  "type": "object"
}
```
