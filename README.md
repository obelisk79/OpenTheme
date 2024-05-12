![Colours](resources/icons/openthemes.png)

# THIS THEME ADDON IS IN A BETA STATE!
# PLEASE REPORT BUGS/PROBLEMS ON [GITHUB](https://github.com/obelisk79/OpenTheme/issues)

OpenLight/OpenDark Theme Preference Pack for [FreeCAD](https://www.freecad.org)

This is a set of light and dark color-impaired accessible aesthetically pleasing themes (OpenLight and OpenDark) for FreeCAD based on the [Open-Color Palette](https://github.com/yeun/open-color) that is WCAG/APCA compliant.

I have refactored this theme for improved maintainability using SCSS. New color variants can be created easily without having to re-style the entire spreadsheet. I compile the stylesheets using [QTSASS](https://github.com/spyder-ide/qtsass).

## Installation

Using [Preference Packs](https://wiki.freecad.org/Preference_Packs) requires FreeCAD 0.20 or higher.

Preference Packs should be installed via the [Addon Manager](https://github.com/FreeCAD/FreeCAD-addons), but can be [installed manually](https://wiki.freecad.org/Preference_Packs#Distributing_a_pack) if required.

## Screenshots

![Screenshots](resources/images/OpenDark_sketcher.png)
![Screenshots](resources/images/text_panels.png)


## Contributing
To build SCSS sources into QSS files you will need to have qtsass installed: [spyder-ide/qtsass](https://github.com/spyder-ide/qtsass).

Once you have it you should modify ONLY `.scss` files and rebuild them using `build.sh` script. 

To watch files for changes and rebuild stylesheets automatically you can use `--watch` flag:
```bash
./build.sh --watch
```

This will make sure that your qss files are always up-to-date.

## License
 [LGPLv2](https://en.m.wikipedia.org/wiki/GNU_Lesser_General_Public_License)
