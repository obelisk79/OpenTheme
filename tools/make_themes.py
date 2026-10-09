#!/usr/bin/env python3
"""Generate each pack's token file, the variant packs' .cfg, and package.xml.

    tools/make_themes.py                         write everything
    tools/make_themes.py --check                 also report missing tokens and contrast
    tools/make_themes.py --into DIR A.theme ...  make packs from other .theme files in DIR and list them in DIR/package.xml

Each tools/themes/<Name>.theme file defines one pack: add or edit a file there and rerun.
"""
import colorsys
import functools
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUFFIX = ""   # e.g. "Beta" builds a copy whose packs can sit beside a release
HOST_PACK = "OpenDark"   # its folder holds the stylesheets and images every pack uses
STYLESHEET, OVERLAY_STYLESHEET = f"OpenTheme{SUFFIX}.qss", f"OpenTheme{SUFFIX}_Overlay.qss"
ICON_VARIANT = {True: "ondark", False: "onlight", None: "onsystem"}   # suffix of the glyph files a pack uses
OVERLAY_TITLE_ALPHA = 191   # of 255; overlay title bars are translucent
TEXT_MIN, UI_MIN, DISABLED_MIN = 4.5, 3.0, 2.5

# ------------------------------------------------------------------------------ roles
# Grouping and order of the role tokens in every yaml. Every pack defines all of them.
ROLE_GROUPS = {
    "Text": "TextPrimary TextSecondary TextDisabled TextStrong TextLink",
    "Surfaces": "SurfaceBase SurfaceOverlay SurfaceOverlayHover MenuBarBackground SurfaceHover SurfaceDisabled",
    "Inputs and controls": "FieldBackground FieldBorder ControlBackground ControlBackgroundHover ControlBorder IndicatorBorder",
    "Accent: Subtle is the hover tint, Strong the selected fill":
        "AccentColor AccentSubtle AccentSubtleBorder TextOnAccentSubtle AccentStrong TextOnAccent",
    "Borders": "BorderSubtle BorderStrong BorderDisabled BorderHover BorderFocus BorderEmphasis",
    "Item views": "ViewAlternateRow ViewGridLines ViewHeaderBackground ViewHeaderBorder ViewGroupBackground",
    "Scrollbars, progress, tooltips": "ScrollbarTrack ScrollbarHandle ScrollbarHandleHover ProgressBackground "
                                      "ProgressChunk ProgressText TooltipBackground TooltipText TooltipBorder",
    "Overlay panels": "OverlayHeaderBackground OverlayGroupBackground OverlayTitleBackground",
    "Images": "IconVariant IconVariantOnAccent",
    "Geometry": "BorderWidth CornerRadius CornerRadiusLarge",
    "Status and 3D view (used by the .cfg and the stock Sketcher tokens, not by the stylesheet)":
        "StatusError StatusWarning StatusSuccess ViewportHighlight ViewportSelection",
}
ROLES = [role for group in ROLE_GROUPS.values() for role in group.split()]
# Defaults; a pack overrides one by naming it in its roles, e.g. CornerRadius="0px".
GEOMETRY = dict(BorderWidth="1px", CornerRadius="2px", CornerRadiusLarge="3px")
COLOR_ROLES = [role for role in ROLES if not role.startswith("IconVariant") and role not in GEOMETRY]


# ----------------------------------------------------------------------- theme definitions
# Every tools/themes/<Name>.theme file becomes a pack. Format and entries are explained in tools/themes/README.md.
THEMES = Path(__file__).resolve().parent / "themes"
MODES = {"dark": True, "light": False, "system": None}
SETTINGS = ("description", "mode", "base")
PREFERENCES_SECTION = "[preferences]"   # after it, 'Group/Name = value' lines override the generated .cfg
NAME_REFERENCE = re.compile(r"(?<![#\w])([_0-9]*[A-Z]\w*)")   # a palette or role name used inside a value
CFG_TEMPLATE = {True: "OpenDark", False: "OpenLight"}   # packs whose hand-made .cfg the others start from
SYSTEM_RAMP = {"Lighten": "midlight midlight light light light light", "Darken": "mid mid mid dark dark shadow"}


def read_theme(path):
    entries, overrides = {}, {}
    section = entries
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            if line != PREFERENCES_SECTION or section is overrides:
                sys.exit(f"{path.name} line {number}: the only section is {PREFERENCES_SECTION}, once, after the colours")
            section = overrides
            continue
        name, equals, value = (part.strip() for part in line.partition("="))
        if not (equals and name and value):
            sys.exit(f"{path.name} line {number}: expected 'Name = value', found '{line}'")
        if section is overrides and "/" not in name:
            sys.exit(f"{path.name} line {number}: expected 'Group/Name = value' in {PREFERENCES_SECTION}, found '{line}'")
        if name in section:
            sys.exit(f"{path.name} line {number}: '{name}' is defined twice")
        section[name] = value
    settings = {name: entries.pop(name, None) for name in SETTINGS}
    if settings["mode"] not in MODES:
        sys.exit(f"{path.name}: 'mode' must be one of {', '.join(MODES)}")
    tokens = {name: NAME_REFERENCE.sub(r"@\1", value) for name, value in entries.items()}
    if unknown := {ref for value in tokens.values() for ref in re.findall(r"@(\w+)", value)} - set(tokens):
        sys.exit(f"{path.name}: no colour is named {', '.join(sorted(unknown))}")
    palette = {name: value for name, value in tokens.items() if name not in ROLES}
    role_map = {name: value for name, value in tokens.items() if name in ROLES}
    return (MODES[settings["mode"]], settings["description"] or path.stem, palette, role_map, settings["base"]), overrides


# name: (is_dark, description, palette, roles, base), and name: {"Group/Name": value} from [preferences]
PACKS, OVERRIDES = {}, {}


def load(path):
    """Add a .theme file to PACKS and return its name."""
    PACKS[path.stem], OVERRIDES[path.stem] = read_theme(path)
    return path.stem


# The two template packs come first so others can build on them.
for theme in sorted(THEMES.glob("*.theme"), key=lambda p: (p.stem not in CFG_TEMPLATE.values(), p.stem)):
    load(theme)

# ------------------------------------------------------------- stock FreeCAD token names
# FreeCAD core and other addons may ask for the stock theme's tokens, so each yaml also defines them.
LEGACY = dict(
    PrimaryColor="SurfaceBase", GeneralBackgroundColor="SurfaceBase",
    GeneralAlternateBackgroundColor="ViewAlternateRow",
    GeneralBackgroundHoverColor="SurfaceHover", GeneralBorderColor="BorderSubtle",
    GeneralBorderHoverColor="BorderHover",
    GeneralDisabledBackgroundColor="SurfaceDisabled", GeneralGridLinesColor="ViewGridLines",
    GeneralHeaderBackgroundColor="ViewHeaderBackground", DialogBackgroundColor="SurfaceBase",
    GroupboxBackgroundColor="SurfaceBase", GroupboxBorderColor="BorderStrong", MenuBackgroundColor="SurfaceOverlay",
    ButtonTopBackgroundColor="ControlBackground", ButtonBottomBackgroundColor="ControlBackground",
    ButtonBackgroundHooverColor="ControlBackgroundHover", ButtonBorderColor="ControlBorder",
    ButtonBorderHooverColor="BorderHover", CheckedButtonTopBackgroundColor="AccentSubtle",
    CheckedButtonBottomBackgroundColor="AccentSubtle", DefaultButtonTopBackgroundColor="ControlBackground",
    DefaultButtonBottomBackgroundColor="ControlBackground", DefaultButtonBorderColor="BorderEmphasis",
    ToolButtonCheckedBorderColor="BorderHover", ToolButtonCheckedBackground="AccentStrong",
    CheckBoxBackgroundColor="FieldBackground", CheckBoxBorderColor="IndicatorBorder",
    RadioButtonBackgroundColor="FieldBackground", RadioButtonBorderColor="IndicatorBorder",
    TextEditFieldBackgroundColor="FieldBackground", TextForegroundColor="TextPrimary",
    TextDisabledColor="TextDisabled",
    TextSelectBackgroundColor="AccentStrong", TextUrlColor="TextLink", ScrollbarBackgroundColor="ScrollbarTrack",
    TabbarBackgroundColor="SurfaceBase", ActiveTabBackgroundColor="AccentSubtle",
    InActiveTabBackgroundColor="SurfaceBase",
    AccentBackgroundColor="AccentSubtle", AccentHoverColor="AccentStrong",
    SketcherFullyConstrainedColor="StatusSuccess", SketcherUnderConstrainedColor="TextPrimary",
    SketcherEmptySketchColor="TextPrimary", SketcherConflictingConstraintsColor="StatusError",
    SketcherMalformedConstraintsColor="StatusError", SketcherSolverFailedColor="StatusError",
    SketcherRedundantConstraintsColor="StatusWarning", SketcherPartiallyRedundantConstraintsColor="TextLink",
)
LEGACY_LITERAL = {"3DViewBackgroundRefColor": "@BackgroundColor", "IconsLocationFolderName": "images_classic",
                  "InputFieldBorderRadius": "2px", "ToolbarButtonsPadding": "2px"}
LEGACY_ICON_COLOR = {True: "white", False: "black", None: "black"}
# Lighten1..6 and Darken1..6 amounts, as in the stock FreeCAD Dark / FreeCAD Light themes
LEGACY_RAMP = {True: ((20, 40, 80, 100, 300, 5890), (5, 8, 15, 20, 200, 5890)),
               False: ((2, 3, 4, 5, 6, 7), (4, 8, 10, 20, 200, 5890))}

# ------------------------------------------------------- colours a variant's .cfg takes from its roles
RGBA, RGB0, HEX = "rgba", "rgb0", "hex"   # FCUInt with opaque alpha, FCUInt with zero alpha (editor), FCText
CFG_COLORS = {
    "View": (RGBA, dict(
        BackgroundColor="SurfaceBase", BackgroundColor2="SurfaceHover", BackgroundColor3="SurfaceBase",
        BackgroundColor4="SurfaceBase", HighlightColor="ViewportHighlight", SelectionColor="ViewportSelection",
        AxisLetterColor="TextSecondary", AnnotationTextColor="TextSecondary", CbLabelColor="TextSecondary",
        DefaultShapeLineColor="TextSecondary", CursorTextColor="TextSecondary",
        SketchEdgeColor="TextPrimary", SketchVertexColor="TextPrimary", EditedEdgeColor="TextPrimary",
        CursorCrosshairColor="TextPrimary", CreateLineColor="TextPrimary", BoundingBoxColor="TextPrimary",
        BacklightColor="TextPrimary", EditedVertexColor="StatusWarning", ConstrainedIcoColor="StatusWarning",
        ConstrainedDimColor="StatusWarning", FullyConstrainedColor="StatusSuccess", ConstructionColor="TextLink",
        InternalAlignedGeoColor="TextLink", NonDrivingConstrDimColor="TextLink", InvalidSketchColor="StatusError",
        ExprBasedConstrDimColor="StatusError", ExternalColor="AccentStrong",
        DeactivatedConstrDimColor="TextDisabled")),
    "Editor": (RGB0, {
        "Text": "TextPrimary", "Operator": "TextPrimary", "Keyword": "AccentStrong", "Comment": "TextDisabled",
        "Block comment": "StatusSuccess", "String": "StatusSuccess", "Number": "StatusWarning",
        "Class name": "TextLink", "Define name": "TextLink", "Python output": "TextSecondary",
        "Python error": "StatusError", "Current line highlight": "SurfaceHover"}),
    "OutputWindow": (RGBA, dict(colorText="TextPrimary", colorLogging="TextLink", colorWarning="StatusWarning",
                                colorError="StatusError")),
    "Start": (RGBA, dict(BackgroundColor1="SurfaceBase", BackgroundTextColor="TextPrimary", PageColor="FieldBackground",
                         PageTextColor="TextPrimary", BoxColor="SurfaceHover", LinkColor="TextLink")),
    "Appearance": (RGBA, dict(DefaultTextBackgroundColor="SurfaceBase", DefaultTextColor="TextPrimary",
                              DefaultLineColor="TextPrimary")),
    "Spreadsheet": (HEX, dict(AliasedCellBackgroundColor="AccentSubtle")),
}
ACCENT_PREFS = ("ThemeAccentColor1", "ThemeAccentColor2", "ThemeAccentColor3")
PACKAGE_TAG = {True: "dark", False: "light", None: "system"}
# The system pack cannot know whether the desktop is light or dark, so its 3D view is a light mid-grey gradient
# (Gray5 edge, Gray4 centre) with the darkest Open Color steps, which stay readable on it and beside either kind of UI.
SYSTEM_VIEW = {
    "#adb5bd": "BackgroundColor BackgroundColor3 BackgroundColor4",                       # Gray5
    "#ced4da": "BackgroundColor2",                                                        # Gray4
    "#000000": "SketchEdgeColor SketchVertexColor EditedEdgeColor EditedVertexColor CreateLineColor "
               "CursorCrosshairColor CursorTextColor AxisLetterColor AnnotationTextColor CbLabelColor BoundingBoxColor",
    "#f1f3f5": "BacklightColor HeadlightColor DefaultShapeColor",                         # Gray1
    "#212529": "DefaultShapeLineColor DefaultShapeVertexColor",                           # Gray9
    "#495057": "DeactivatedConstrDimColor",                                               # Gray7
    "#1864ab": "ConstructionColor InternalAlignedGeoColor NonDrivingConstrDimColor",      # Blue9
    "#862e9c": "ExternalColor",                                                           # Grape9
    "#d9480f": "InvalidSketchColor ExprBasedConstrDimColor",                              # Orange9
    "#2b8a3e": "FullyConstrainedColor FullyConstraintElementColor",                       # Green9
    "#c92a2a": "ConstrainedIcoColor ConstrainedDimColor",                                 # Red9
    "#0b7285": "HighlightColor",                                                          # Cyan9
    "#5f3dc4": "SelectionColor",                                                          # Violet9
}
SYSTEM_VIEW_FLAGS = dict(Simple=0, Gradient=0, RadialGradient=1, UseBackgroundColorMid=0)
# The system pack's whole .cfg: the stylesheet and the 3D view; every other colour preference is left alone.
SYSTEM_CFG = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<FCParameters>
  <FCParamGroup Name="Root">
    <FCParamGroup Name="BaseApp">
      <FCParamGroup Name="Preferences">
        <FCParamGroup Name="MainWindow">
          <FCBool Name="TiledBackground" Value="0"/>
          <FCText Name="StyleSheet"></FCText>
        </FCParamGroup>
        <FCParamGroup Name="View">
{view}
        </FCParamGroup>
      </FCParamGroup>
    </FCParamGroup>
  </FCParamGroup>
</FCParameters>
"""

# ---------------------------------------------------------------- contrast pairs for --check
CONTRAST = [(fg, bg, TEXT_MIN) for fg, bgs in {
    "TextPrimary": "SurfaceBase FieldBackground SurfaceOverlay SurfaceHover ControlBackground ViewHeaderBackground",
    "TextSecondary": "SurfaceBase MenuBarBackground", "TextStrong": "SurfaceBase", "TextLink": "SurfaceBase",
    "TextOnAccentSubtle": "AccentSubtle", "TextOnAccent": "AccentStrong",
    "TooltipText": "TooltipBackground", "ProgressText": "ProgressChunk ProgressBackground",
}.items() for bg in bgs.split()] + [
    ("FieldBorder", "FieldBackground", UI_MIN), ("FieldBorder", "SurfaceBase", UI_MIN),
    ("IndicatorBorder", "SurfaceBase", UI_MIN), ("BorderFocus", "FieldBackground", UI_MIN),
    ("TextDisabled", "SurfaceBase", DISABLED_MIN),
]


# ---------------------------------------------------------------------------- evaluation
# Mirrors FreeCAD's style-parameter functions closely enough for the .cfg colours and the checks:
# lighten/darken scale HSV value like QColor::lighter/darker, blend mixes RGB by percent.
def rgb(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def to_hex(channels):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in channels)


def scale_value(hex_color, percent):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb(hex_color)))
    v *= percent / 100
    if v > 1:
        s, v = max(0.0, s - (v - 1)), 1.0
    return to_hex(c * 255 for c in colorsys.hsv_to_rgb(h, s, v))


def evaluate(expression, table):
    expression = expression.strip()
    if expression.startswith("#"):
        return expression
    if expression.startswith("@"):
        return evaluate(table[expression[1:]], table)
    name, args = re.fullmatch(r"(\w+)\((.*)\)", expression).groups()
    *colors, amount = (a.strip() for a in re.split(r",(?![^(]*\))", args))
    colors, amount = [evaluate(c, table) for c in colors], int(amount)
    if name == "blend":
        return to_hex(a + (b - a) * amount / 100 for a, b in zip(*map(rgb, colors)))
    return scale_value(colors[0], 100 + amount if name == "lighten" else 100 * 100 / (100 + amount))


def contrast(a, b):
    """WCAG 2 contrast ratio."""
    def luminance(hex_color):
        srgb = [c / 255 for c in rgb(hex_color)]
        r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# ------------------------------------------------------------------------------- output
def pack_name(key):
    return key + SUFFIX


def pack_roles(key):
    is_dark, _, palette, role_map, _ = PACKS[key]
    role_map = {"OverlayTitleBackground": "@SurfaceBase", **GEOMETRY, **role_map, "IconVariant": ICON_VARIANT[is_dark]}
    # glyphs on the selected fill follow its text: light text takes the glyphs drawn for dark surfaces
    on_accent = None if is_dark is None else evaluate("@TextOnAccent", {**palette, **role_map})
    role_map["IconVariantOnAccent"] = ICON_VARIANT[on_accent and contrast(on_accent, "#000000") > contrast(on_accent, "#ffffff")]
    if missing := set(ROLES) - set(role_map):
        sys.exit(f"{key}.theme: missing {', '.join(sorted(missing))}")
    return role_map


def resolved_roles(key):
    table = {**PACKS[key][2], **pack_roles(key)}
    return {role: evaluate("@" + role, table) for role in COLOR_ROLES}


def legacy_ramp(is_dark):
    if is_dark is None:
        return {f"PrimaryColor{name}{i}": f"palette({role})"
                for name, steps in SYSTEM_RAMP.items() for i, role in enumerate(steps.split(), 1)}
    return {f"PrimaryColor{name}{i}": f"{name.lower()}(@PrimaryColor, {amount})"
            for name, amounts in zip(("Lighten", "Darken"), LEGACY_RAMP[is_dark]) for i, amount in enumerate(amounts, 1)}


def yaml_text(key):
    is_dark, description, palette, *_ = PACKS[key]
    role_map = pack_roles(key)
    if is_dark is not None:
        title = ", ".join(map(str, rgb(resolved_roles(key)["OverlayTitleBackground"])))
        role_map["OverlayTitleBackground"] = f"rgba({title}, {OVERLAY_TITLE_ALPHA})"
    legacy = {**{name: "@" + role for name, role in LEGACY.items()}, **LEGACY_LITERAL,
              "StylesheetIconsColor": LEGACY_ICON_COLOR[is_dark], **legacy_ramp(is_dark)}
    lines = [f"# {pack_name(key)}: {description}", f"# Generated by OpenTheme's tools/make_themes.py from {key}.theme. Edit that file, not this one."]
    if palette:
        lines += ["", "# ---- Palette ----", *(f'{n}: "{v}"' for n, v in palette.items())]
    lines += ["", "# ---- Roles: the only tokens the stylesheet uses ----"]
    for group, names in ROLE_GROUPS.items():
        lines += [f"# {group}", *(f'{n}: "{role_map[n]}"' for n in names.split())]
    lines += ["", "# ---- Stock FreeCAD token names, for core widgets and other addons ----",
              *(f'{n}: "{v}"' for n, v in legacy.items())]
    return "\n".join(lines) + "\n"


def encode(hex_color, kind):
    r, g, b = rgb(hex_color)
    opaque = 0xFF if kind == RGBA else 0
    return hex_color if kind == HEX else str((r << 24) | (g << 16) | (b << 8) | opaque)


def set_text_pref(cfg, name, value):
    """Set <FCText Name=name> inside the MainWindow group, adding it if absent."""
    entry = f'<FCText Name="{name}">{value}</FCText>'
    pattern = rf'<FCText Name="{name}">[^<]*</FCText>'
    if re.search(pattern, cfg):
        return re.sub(pattern, entry, cfg)
    anchor = '<FCText Name="StyleSheet">'
    indent = re.search(rf"\n([ \t]*){anchor}", cfg).group(1)
    return cfg.replace(anchor, f"{entry}\n{indent}{anchor}", 1)


def variant_cfg(key, base_cfg):
    colors, groups, out = resolved_roles(key), [], []
    for line in base_cfg.split("\n"):
        opened = re.search(r'<FCParamGroup Name="([^"]+)"(/?)>', line)
        if opened and not opened.group(2):
            groups.append(opened.group(1))
        elif "</FCParamGroup>" in line:
            groups.pop()
        kind, names = CFG_COLORS.get(groups[-1] if groups else None, (None, {}))
        named = re.search(r'Name="([^"]+)"', line)
        if named and not opened and named.group(1) in names:
            value = encode(colors[names[named.group(1)]], kind)
            line = re.sub(r'(Value=")\d+(")|(>)#\w+(<)',
                          lambda m: (m.group(1) or m.group(3)) + value + (m.group(2) or m.group(4)), line)
        out.append(line)
    cfg = "\n".join(out)
    accent = encode(colors["AccentColor"], RGBA)
    anchor = re.search(r'\n([ \t]*)<FCParamGroup Name="MainWindow">', cfg)
    indent = anchor.group(1)
    themes = "".join(f'\n{indent}  <FCUInt Name="{n}" Value="{accent}"/>' for n in ACCENT_PREFS)
    return cfg.replace(anchor.group(0), f'\n{indent}<FCParamGroup Name="Themes">{themes}\n{indent}</FCParamGroup>{anchor.group(0)}', 1)


def recolored_cfg(key, base, base_cfg):
    """The base pack's .cfg, with every palette colour this theme redefines swapped for its own."""
    swap = {old: PACKS[key][2][name] for name, old in PACKS[base][2].items() if PACKS[key][2].get(name, old) != old}

    def one(m):
        if m.group(1):
            return swap.get(m.group(0), m.group(0))
        value = int(m.group(2))
        new = swap.get(f"#{value >> 8:06x}")
        return f'Value="{int(new[1:], 16) << 8 | value & 255}"' if new else m.group(0)
    return re.sub(r'(#[0-9a-f]{6})\b|Value="(\d{3,})"', one, base_cfg)


def system_cfg():
    colors = [f'<FCUInt Name="{name}" Value="{encode(color, RGBA)}"/>' for color, names in SYSTEM_VIEW.items() for name in names.split()]
    flags = [f'<FCBool Name="{name}" Value="{value}"/>' for name, value in SYSTEM_VIEW_FLAGS.items()]
    return SYSTEM_CFG.format(view="\n".join(" " * 10 + line for line in colors + flags))


def package_content():
    entries = []
    for key, (is_dark, description, *_) in PACKS.items():
        name = pack_name(key)
        entries.append(f"""  <preferencepack>
    <name>{name}</name>
    <description>{description}</description>
    <type>Theme</type>
    <tag>{PACKAGE_TAG[is_dark]}</tag>
    <subdirectory>./{name}/</subdirectory>
    <file>{name}.cfg</file>
  </preferencepack>""")
    return "\n".join(entries)


@functools.cache
def pack_cfg(key):
    is_dark, *_, base = PACKS[key]
    if is_dark is None:
        return system_cfg()
    if key in CFG_TEMPLATE.values():
        name = pack_name(key)
        return (ROOT / name / f"{name}.cfg").read_text(encoding="utf-8")
    return recolored_cfg(key, base, pack_cfg(base)) if base else variant_cfg(key, pack_cfg(CFG_TEMPLATE[is_dark]))


XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'
NAMED_COLOR = re.compile(r"#[0-9a-fA-F]{6}|(blend|lighten|darken)\(.*\)|[_0-9]*[A-Z]\w*")


def preference_value(key, raw, tag, old):
    """(tag, value) for one [preferences] line; tag is the existing setting's, or inferred from the value."""
    table = {**PACKS[key][2], **pack_roles(key)}
    if NAMED_COLOR.fullmatch(raw) and (raw[0] == "#" or "(" in raw or raw in table):
        try:
            color = evaluate(NAME_REFERENCE.sub(r"@\1", raw), table)
        except (KeyError, AttributeError, ValueError):
            sys.exit(f"{key}.theme: {raw} in {PREFERENCES_SECTION} is not a colour this theme can work out")
        if tag == "FCText":
            return tag, color
        alpha = int(old) & 0xFF if old is not None else 0xFF
        return "FCUInt", str(int(color[1:], 16) << 8 | alpha)
    if raw.lower() in ("true", "false"):
        return "FCBool", "1" if raw.lower() == "true" else "0"
    if tag:
        return tag, raw
    if re.fullmatch(r"-?\d+", raw):
        return "FCInt", raw
    if re.fullmatch(r"-?\d*\.\d+", raw):
        return "FCFloat", raw
    return "FCText", raw


def apply_overrides(key, cfg):
    """The .cfg with the theme's [preferences] lines written over it."""
    if not OVERRIDES[key]:
        return cfg
    root = ET.fromstring(cfg)
    preferences = root.find("FCParamGroup[@Name='Root']/FCParamGroup[@Name='BaseApp']/FCParamGroup[@Name='Preferences']")
    for path, raw in OVERRIDES[key].items():
        *groups, name = path.split("/")
        group = preferences
        for part in groups:
            found = group.find(f"FCParamGroup[@Name='{part}']")
            group = found if found is not None else ET.SubElement(group, "FCParamGroup", Name=part)
        setting = next((e for e in group if e.tag != "FCParamGroup" and e.get("Name") == name), None)
        if setting is None:
            print(f"{key}.theme: {path} is not in the generated settings, so it is added as new", file=sys.stderr)
        tag, value = preference_value(key, raw, None if setting is None else setting.tag,
                                      None if setting is None else setting.get("Value"))
        if setting is not None and setting.tag != tag:
            group.remove(setting)
            setting = None
        if setting is None:
            setting = ET.SubElement(group, tag, Name=name)
        if tag == "FCText":
            setting.text = value
        else:
            setting.set("Value", value)
    ET.indent(root, "  ")
    return XML_DECLARATION + ET.tostring(root, encoding="unicode") + "\n"


def write_pack(key, folder):
    """Write one pack's token file and .cfg into folder."""
    name = pack_name(key)
    (folder / "parameters").mkdir(parents=True, exist_ok=True)
    (folder / "parameters" / f"{name}.yaml").write_text(yaml_text(key), encoding="utf-8")
    cfg = pack_cfg(key)
    for pref, value in (("Theme", name), ("StyleSheet", STYLESHEET), ("OverlayActiveStyleSheet", OVERLAY_STYLESHEET)):
        cfg = set_text_pref(cfg, pref, value)
    (folder / f"{name}.cfg").write_text(apply_overrides(key, cfg), encoding="utf-8")


def register(package, key):
    """List the pack in package (a package.xml beside the pack folders), replacing an entry of the same name."""
    ns = "https://wiki.freecad.org/Package_Metadata"
    ET.register_namespace("", ns)
    q = lambda tag: f"{{{ns}}}{tag}"
    if package.exists():
        root = ET.parse(package).getroot()
    else:
        root = ET.Element(q("package"), format="1")
        ET.SubElement(root, q("name")).text = "User-Saved Preference Packs"
    content = root.find(q("content"))
    if content is None:
        content = ET.SubElement(root, q("content"))
    is_dark, description, *_ = PACKS[key]
    name = pack_name(key)
    for old in [p for p in content.findall(q("preferencepack")) if p.findtext(q("name")) == name]:
        content.remove(old)
    entry = ET.SubElement(content, q("preferencepack"))
    for tag, text in (("name", name), ("description", description), ("type", "Theme"), ("tag", PACKAGE_TAG[is_dark])):
        ET.SubElement(entry, q(tag)).text = text
    ET.indent(root, " ")
    package.write_text(XML_DECLARATION + ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")


def build(theme_path, target):
    """Make a pack from a .theme file in target (for example FreeCAD's SavedPreferencePacks) and list it there."""
    key = load(Path(theme_path))
    write_pack(key, Path(target) / pack_name(key))
    register(Path(target) / "package.xml", key)
    return pack_name(key)


def write_all():
    for key in PACKS:
        write_pack(key, ROOT / pack_name(key))
    package = ROOT / "package.xml"
    text = package.read_text(encoding="utf-8")
    themes = r"(<content>\n).*?(\n  <preferencepack>\n    <name>OpenPreferences)"
    package.write_text(re.sub(themes, lambda m: m.group(1) + package_content() + m.group(2), text, flags=re.S), encoding="utf-8")


def check():
    used = set()
    for sheet in (ROOT / pack_name(HOST_PACK)).rglob("*.qss"):
        used |= set(re.findall(r"@(\w+)", sheet.read_text(encoding="utf-8")))
    print("stylesheet tokens without a role:", sorted(used - set(ROLES)) or "none")
    for key in (k for k, pack in PACKS.items() if pack[0] is not None):
        colors = resolved_roles(key)
        low = [f"{fg} on {bg} {contrast(colors[fg], colors[bg]):.2f} (min {minimum})"
               for fg, bg, minimum in CONTRAST if contrast(colors[fg], colors[bg]) < minimum]
        print(f"{pack_name(key):26} {len(CONTRAST) - len(low)}/{len(CONTRAST)} contrast pairs pass")
        for item in low:
            print("    " + item)


if __name__ == "__main__":
    if "--into" in sys.argv:
        target, *themes = sys.argv[sys.argv.index("--into") + 1:]
        for theme in themes:
            print("built", build(theme, target))
    else:
        write_all()
        if "--check" in sys.argv:
            check()
