#!/usr/bin/env python3
"""One-off: make the _onsystem glyph set, a mid grey that reads on light and dark backgrounds.

Each glyph is the _ondark file with the colours that differ from its _onlight twin replaced.
Usage: system_glyphs.py <addon folder>
"""
import re, sys
from collections import Counter
from pathlib import Path

GLYPH, HOVER, DISABLED = "#868e96", "#339af0", "#adb5bd"
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
images = Path(sys.argv[1]) / "OpenDark" / "opentheme_images"
for dark in sorted(images.glob("*_ondark.svg")):
    text = dark.read_text(encoding="utf-8")
    light = (images / dark.name.replace("_ondark", "_onlight")).read_text(encoding="utf-8")
    differing = set((Counter(c.lower() for c in HEX.findall(text)) - Counter(c.lower() for c in HEX.findall(light)))) - {"#000000"}
    tone = HOVER if "hover" in dark.name else DISABLED if "disabled" in dark.name else GLYPH
    out = HEX.sub(lambda m: tone if m.group(0).lower() in differing else m.group(0), text)
    (images / dark.name.replace("_ondark", "_onsystem")).write_text(out, encoding="utf-8")
print(len(list(images.glob("*_onsystem.svg"))), "system glyphs")
