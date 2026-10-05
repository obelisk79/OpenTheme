2024.MAY.03
- Resolved issue #3
- Modified color scheme to be slightly lighter and less blue/silver
- Resolved undefined/unreadable colors for unified measurement tool

2024.MAY.16
- corrected several issues related to text color in spreadsheets
- fixed color of snap indicator in Draft WB
- corrected display issues with SelectorToolbar addon in vertical orientation
- corrected color/display issues related to list-views

2024.MAY.17
- corrected a regression causing radio buttons to be styled like checkboxes
- change QGroupBox header padding to resolve text clipping for some users

2024.MAY.20-22
- Multiple fixes for tree-view, preferences page
- changed selection color
- homgenized styling of OpenDark and OpenLight better
- tweaked sketch mode display settings
- enabled section view mode by default when entering sketcher (is not retroactive to existing sketches)
- fixed checkboxes in preference window having broken borders
- removed QtNormalizer as it is no longer needed.

2024.JULY.30
- Fixed more than 12 long-standing theme issues and inconsistencies.

2024.AUGUST.09
- Added explicit declaration of color to text in status bar and panel title bar

2024.AUGUST.10
- Changed panel titlebar and splitterbar background colors to better fit the OpenDark theme.

2024.AUGUST.15
- Defined the color for the axis/coordinate symbol in the corner
- Defined focus colors for input fields.

2024.AUGUST.17
- Add missing disabled widget definitions

2024.AUGUST31
- Initial Implementation of 'OpenPreferences' pack based on proposed new default FreeCAD settings

2026.OCTOBER.03
- Themes now use FreeCAD style parameters: one stylesheet for every pack, with colours supplied by each pack's parameters/<Pack>.yaml. Older FreeCAD versions should use the OpenTheme_Legacy branch
- Each theme is defined by a plain text file in tools/themes/ (one `Name = colour` per line); tools/make_themes.py builds a pack for every file it finds
- OpenDark and OpenLight are built from ten seed colours on a more neutral grey ramp
- New pack OpenSystem: the same styling in the desktop's own colours
- Geometry tokens for border width and corner radius
- Contrast reviewed with APCA: links, text on selected items, disabled buttons, borders, scrollbar handles, report view and Sketcher colours
- Hover and selected now look different everywhere both exist: hover is a tint of the accent, selected is the full accent
- Selected rows in lists and overlay panels have a text colour and a visible highlight (#132, #175, #143)
- Property editor group headers have a text colour (#182)
- Progress bar shows its real value and the fill stands out from the track (#82, #136)
- Unselected tabs recede; selected tab is filled and outlined (#183, #146)
- Default button is outlined (#28)
- Less padding on buttons, tool buttons and tree items (#145, #163, #166, #130, #141, #168, #172)
- Dark overlay headers readable; overlay line edits no longer clip text (PR #187)
- Tables: selected text colour, row banding, disabled state, corner button, header states, themed cell checkboxes; the spreadsheet grid has alternating row colours
- Document tab close buttons use the theme's close glyph
- Dark theme no longer draws tree branch lines, matching the light theme
- OpenPreferences no longer restores a saved window layout, saves workbench toolbars per tab, or background-loads workbenches (#177, #181, #184, #174)
- Seed-based definitions for other palettes (Catppuccin, Nord, Dracula, Gruvbox, Solarized, Tokyo Night, Rose Pine, One, Everforest, Kanagawa, Monokai, High Contrast) are kept in tools/themes-saved/ and are not built by default
- Model tree and other trees show dotted branch lines; the Preferences page list and the property editor do not
- File dialogs opened from a task panel no longer squash their navigation button icons
- Spin boxes, buttons and line edits are the same height as combo boxes, in task panels and overlay panels
