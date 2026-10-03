# Theme definitions

Each `.theme` file in this folder becomes one theme in FreeCAD. To make your own:

1. Copy a file that is close to what you want and give it a new name, for example `MyTheme.theme`.
2. Change the colours.
3. Run `python3 tools/make_themes.py` from the addon folder (or `./build.sh`).
4. Restart FreeCAD and pick the theme under Preferences.

The theme is named after the file. Every theme works the same way: change the ten `0_Seed…` colours at the top and every other colour follows.

## Format

One entry per line:

    Name = value

A line that starts with `#` is a note and is ignored. Blank lines are ignored.

A value is one of:

| Value | Example | Meaning |
|---|---|---|
| A colour | `#339af0` | Red, green, blue in hex |
| A name | `Gray7` | The colour of another entry in the same file |
| A mix | `blend(Gray9, Blue5, 20)` | Start at the first colour and go 20 % of the way to the second |
| Lighter or darker | `lighten(Blue5, 20)`, `darken(Blue5, 20)` | The colour made lighter or darker by 20 % |
| A system colour | `palette(window)` | A colour taken from the desktop (used by `OpenSystem.theme`) |

Names start with a capital letter. A name may begin with a digit and underscore (for example `0_SeedAccent`), which lists a theme's own colours first in FreeCAD's theme editor.

## Settings

| Entry | Value |
|---|---|
| `description` | One line shown in FreeCAD's list of themes |
| `mode` | `dark`, `light` or `system`. Chooses light or dark icons and the starting 3D view colours |
| `base` | Optional. The name of another theme whose 3D view, Sketcher and editor colours to copy. Any palette colour you redefine under the same name is swapped in. Without `base`, those colours are worked out from the roles below |

## Palette and roles

An entry whose name is not in the list below is a **palette** colour: a name of your own that other entries can use.

The entries below are **roles**: where a colour is used. Every theme must set all of them, except those marked optional.

| Role | Used for |
|---|---|
| `TextPrimary` | Normal text |
| `TextSecondary` | Less important text, unselected tabs |
| `TextDisabled` | Text of disabled items |
| `TextStrong` | Emphasised text |
| `TextLink` | Links |
| `SurfaceBase` | Window and panel background |
| `SurfaceOverlay` | Menus and pop-ups |
| `SurfaceOverlayHover` | Hovered item in a menu |
| `MenuBarBackground` | Menu bar |
| `SurfaceHover` | Hovered toolbar button |
| `SurfaceDisabled` | Background of disabled controls |
| `FieldBackground` | Inside of text boxes, lists and trees |
| `FieldBorder` | Outline of text boxes |
| `ControlBackground` | Push buttons |
| `ControlBackgroundHover` | Hovered push button |
| `ControlBorder` | Outline of push buttons |
| `IndicatorBorder` | Outline of check boxes and radio buttons |
| `AccentColor` | FreeCAD's own accent colour |
| `AccentSubtle` | Background of a hovered row or tab |
| `AccentSubtleBorder` | Outline of a hovered row or tab |
| `TextOnAccentSubtle` | Text on a hovered row or tab |
| `AccentStrong` | Background of a selected row, tab or checked button |
| `TextOnAccent` | Text on a selected row, tab or checked button |
| `BorderSubtle` | Faint dividing lines |
| `BorderStrong` | Stronger dividing lines |
| `BorderDisabled` | Outline of disabled controls |
| `BorderHover` | Outline of a control under the mouse |
| `BorderFocus` | Outline of the control being typed in |
| `BorderEmphasis` | Outline of selected items and the default button |
| `ViewAlternateRow` | Every other row in tables |
| `ViewGridLines` | Table grid lines |
| `ViewHeaderBackground` | Table headers |
| `ViewHeaderBorder` | Lines between table headers |
| `ViewGroupBackground` | Group rows in the property editor |
| `ScrollbarTrack` | Scrollbar background |
| `ScrollbarHandle` | Scrollbar handle |
| `ScrollbarHandleHover` | Scrollbar handle under the mouse |
| `ProgressBackground` | Empty part of a progress bar |
| `ProgressChunk` | Filled part of a progress bar |
| `ProgressText` | Progress bar text |
| `TooltipBackground`, `TooltipText`, `TooltipBorder` | Tooltips |
| `OverlayHeaderBackground` | Headers inside overlay panels |
| `OverlayGroupBackground` | Group rows inside overlay panels |
| `OverlayTitleBackground` | Optional. Overlay panel title bar; `SurfaceBase` if left out |
| `StatusError`, `StatusWarning`, `StatusSuccess` | Error, warning and success colours in the report view and Sketcher |
| `ViewportHighlight`, `ViewportSelection` | Preselection and selection in the 3D view |
| `BorderWidth` | Optional. Outline thickness, `1px` if left out |
| `CornerRadius` | Optional. Corner rounding, `2px` if left out |
| `CornerRadiusLarge` | Optional. Rounding of tabs and tool buttons, `3px` if left out |

If something is wrong, the script stops and names the file and the line.
