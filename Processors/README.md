# Processors

## AppIconExtractor

### Description

Extracts the icon from an app and saves it to disk. Optionally creates composite
icons by superimposing template images on top of the app icon to provide visual
"install", "update", and "uninstall" indicators. The .app can be specified as a
full path, and can be inside a DMG.

Extracted icons are output in PNG format, and default to 256x256 pixels in size.

### Input Variables

- **source:**
    - **required:** True
    - **description:** Path to a .app, or a .dmg or .pkg containing a .app. The app's icon filename is read from the `CFBundleIconFile` key of the app's `Info.plist`.
- **icon_output_path:**
    - **required:** False
    - **default:**
        - `%RECIPE_CACHE_DIR%/%NAME.png`
    - **description:** The output path the app icon should be written to.

### Output Variables
- **plist\_reader\_output\_variables:**
    - **description:** Output variables per 'plist\_keys' supplied as input. Note that this output variable is used as both a placeholder for documentation and for auditing purposes. One should use the actual named output variables as given as values to 'plist\_keys' to refer to the output of this processor.

### Compositing

In addition to extracting an app's icon, `AppIconExtractor` can create composite
icons by superimposing a template image on top of the app icon. This is useful
to generate icon variations for use in "update", "uninstall" or "install" Self
Service policies within an endpoint management system, to provide an additional
visual indicator of the policy's purpose.

