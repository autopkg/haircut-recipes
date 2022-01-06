#!/usr/local/autopkg/python
# -*- coding: utf-8 -*-
#
# Copyright 2022 Matthew Warren
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
AppIconExtractor

This is a processor for AutoPkg.

Important! You *must* install the Pillow library to AutoPkg's Python framework.
You can do this by running:

/usr/local/autopkg/python -m pip install --upgrade Pillow


"""

import plistlib
import base64
import io
import os
import shutil
from glob import glob

from autopkglib import Processor, ProcessorError
from autopkglib.FlatPkgUnpacker import FlatPkgUnpacker
from autopkglib.PkgPayloadUnpacker import PkgPayloadUnpacker

try:
    from PIL import Image
except (ImportError, ModuleNotFoundError):
    raise ProcessorError(
        "The Pillow library is required, but was not found. "
        "Please run the following command to install the library: "
        "/usr/local/autopkg/python -m pip install --upgrade Pillow"
    )

__all__ = ["AppIconExtractor.py"]


# Default icon strings
DEFAULT_ICON_UPDATE = "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAEt2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjEwMCIKICAgZXhpZjpQaXhlbFlEaW1lbnNpb249IjEwMCIKICAgZXhpZjpDb2xvclNwYWNlPSIxIgogICB0aWZmOkltYWdlV2lkdGg9IjEwMCIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMTAwIgogICB0aWZmOlJlc29sdXRpb25Vbml0PSIyIgogICB0aWZmOlhSZXNvbHV0aW9uPSI3Mi8xIgogICB0aWZmOllSZXNvbHV0aW9uPSI3Mi8xIgogICBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIgogICBwaG90b3Nob3A6SUNDUHJvZmlsZT0ic1JHQiBJRUM2MTk2Ni0yLjEiCiAgIHhtcDpNb2RpZnlEYXRlPSIyMDIx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"
DEFAULT_ICON_INSTALL = "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAFXWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjEwMCIKICAgZXhpZjpQaXhlbFlEaW1lbnNpb249IjEwMCIKICAgZXhpZjpDb2xvclNwYWNlPSIxIgogICB0aWZmOkltYWdlV2lkdGg9IjEwMCIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMTAwIgogICB0aWZmOlJlc29sdXRpb25Vbml0PSIyIgogICB0aWZmOlhSZXNvbHV0aW9uPSI3Mi8xIgogICB0aWZmOllSZXNvbHV0aW9uPSI3Mi8xIgogICBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIgogICBwaG90b3Nob3A6SUNDUHJv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"
DEFAULT_ICON_UNINSTALL = "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAFX2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjEwMCIKICAgZXhpZjpQaXhlbFlEaW1lbnNpb249IjEwMCIKICAgZXhpZjpDb2xvclNwYWNlPSIxIgogICB0aWZmOkltYWdlV2lkdGg9IjEwMCIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMTAwIgogICB0aWZmOlJlc29sdXRpb25Vbml0PSIyIgogICB0aWZmOlhSZXNvbHV0aW9uPSI3Mi8xIgogICB0aWZmOllSZXNvbHV0aW9uPSI3Mi8xIgogICBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIgogICBwaG90b3Nob3A6SUNDUHJv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"


class AppIconExtractor(PkgPayloadUnpacker, FlatPkgUnpacker):
    description = (
        "Extracts an app icon and saves it to disk. Optionally creates "
        "composite images."
    )
    input_variables = {
        "source": {
            "required": True,
            "description": "Path to a .app, DMG, or flat package from which to "
            "extract an icon.",
        },
        "icon_output_path": {
            "required": False,
            "description": "The output path to write the .png icon. If not "
            "set, defaults to %RECIPE_CACHE_DIR%/%NAME%.png",
        },
        "composite_install_path": {
            "required": False,
            "description": "The output path to write the composited 'install' "
            "icon .png, where `composite_install_template` is superimposed on "
            "top of the app icon. If not set, not 'install' composite icon will "
            "be created.",
        },
        "composite_install_template": {
            "required": False,
            "description": "Path to a template icon to composite on top of the "
            "app's icon to create an 'install' icon version. If not set, a "
            "default template icon is used.",
        },
        "composite_update_path": {
            "required": False,
            "description": "The output path to write the composited 'update' "
            "icon .png, where `composite_update_template` is superimposed on "
            "top of the app icon. If not set, not 'update' composite icon will "
            "be created.",
        },
        "composite_update_template": {
            "required": False,
            "description": "Path to a template icon to composite on top of the "
            "app's icon to create an 'update' icon version. If not set, a "
            "default template icon is used.",
        },
        "composite_uninstall_path": {
            "required": False,
            "description": "The output path to write the composited 'uninstall' "
            "icon .png, where `composite_uninstall_template` is superimposed on "
            "top of the app icon. If not set, not 'uninstall' composite icon will "
            "be created.",
        },
        "composite_uninstall_template": {
            "required": False,
            "description": "Path to a template icon to composite on top of the "
            "app's icon to create an 'uninstall' icon version. If not set, a "
            "default template icon is used.",
        },
        "composite_position": {
            "required": False,
            "description": "The anchor position at which to add the composited "
            "template icons. One of: `br` (bottom right), `bl` (bottom left), "
            "`ur` (upper right), or ul (upper left). Defaults to `br`.",
        },
        "composite_padding": {
            "required": False,
            "description": "The number of both horizontal and vertical pixels "
            "to add as padding from the edge of the app icon when compositing "
            "a template icon on top. Defaults to `10`.",
        },
    }
    output_variables = {
        "app_icon_path": {
            "description": "The path on disk to the plain, uncomposited app icon."
        },
        "install_icon_path": {
            "description": "The path on disk to the 'install' composited icon "
            "variation, if requested."
        },
        "update_icon_path": {
            "description": "The path on disk to the 'update' composited icon "
            "variation, if requested."
        },
        "uninstall_icon_path": {
            "description": "The path on disk to the 'uninstall' composited icon "
            "variation, if requested."
        },
    }
    description = __doc__

    # Initialize for FlatPkgUnpacker
    source_path = None
    # Initialize for package unpacking cleanup
    pkg_cleanup = []

    def is_base64(self, s: str) -> bool:
        """Returns boolean whether the passed string is a base64-endcoded value.

        Arguments:
            s: string to check

        Returns:
            boolean if string is base64 encoded
        """
        try:
            # Raise an exception if the passed string cannot be decoded as ascii
            s_bytes = bytes(s, encoding="ascii")
            # Test and return the equality of attempting to re-encode the
            # decoded bytes against the original passed string
            return base64.b64encode(base64.b64decode(s_bytes)) == s_bytes
        except Exception:
            return False

    def find_app_in_payload(self, payload_path: str) -> tuple:
        """Finds .app paths inside a package payload by globbing and returns
        those paths.

        Arguments:
            payload_path: string path to the unpacked package payload on disk

        Returns:
            tuple of a list of matches and the path
        """
        self.env["destination_path"] = os.path.join(
            self.env["RECIPE_CACHE_DIR"], "AppIconExtractorUnpackedPayload"
        )
        self.pkg_cleanup.append(self.env["destination_path"])
        self.unpack_pkg_payload()
        # Find *.app in the unpacked 'Applications' folder first
        app_glob_path = os.path.join(
            self.env["destination_path"], "Applications", "*.app"
        )
        matches = glob(app_glob_path)
        if len(matches) > 0:
            return matches, app_glob_path
        else:
            # Try to find *.app in the parent dir – fix for Virtualbox
            app_glob_path = os.path.join(self.env["destination_path"], "*.app")
            return glob(app_glob_path), app_glob_path

    def unpack_pkg(self, pkg_path: str) -> str:
        """Unpacks a flat package and returns the string path to the unpacked
        file directory on disk.

        Arguments:
            pkg_path: string path to the flat pkg

        Returns:
            string path to unpacked file directory
        """
        # Unpack the package to a temporary directory witihn the recipe cache like FlatPkgUnpacker
        self.env["destination_path"] = os.path.join(
            self.env["RECIPE_CACHE_DIR"], "AppIconExtractorUnpackedPkg"
        )
        self.pkg_cleanup.append(self.env["destination_path"])
        self.source_path = pkg_path
        self.unpack_flat_pkg()
        # Unpack the payload like PkgPayloadUnpacker
        self.env["pkg_payload_path"] = os.path.join(
            self.env["destination_path"], "Payload"
        )
        # Unpack the payload if it exists
        if os.path.isfile(self.env["pkg_payload_path"]):
            matches, app_glob_path = self.find_app_in_payload(
                self.env["pkg_payload_path"]
            )
        else:
            pkgs = os.path.join(self.env["destination_path"], "*.pkg", "Payload")
            payload_matches = glob(pkgs)
            if len(payload_matches) == 0:
                raise ProcessorError(f"No subpackages found by globbing {pkgs}.")
            else:
                # Iterate through subpackages until a .app match is found
                for path in payload_matches:
                    matches, app_glob_path = self.find_app_in_payload(path)
                    if len(matches) > 0:
                        break
        if len(matches) == 0:
            raise ProcessorError(f"No match found by globbing {app_glob_path}")
        elif len(matches) > 1:
            raise ProcessorError(f"Multiple matches found by globbing {app_glob_path}")
        else:
            return matches[0]

    def get_app_icon_path(self, app_path: str) -> str:
        """Returns the full path to the app icon specified in an app's
        Info.plist file if possible.

        Arguments:
            app_path: path to the .app

        Returns:
            string path to the app icon, or None if unable to find it
        """
        if not os.path.exists(app_path):
            return None
        try:
            info = plistlib.readPlist(os.path.join(app_path, "Contents/Info.plist"))
        except plistlib.PlistReadError:
            return None
        # Read the CFBundleIconFile property, or try using the app's name if
        # that property doesn't exist. This won't catch every case of poor app
        # construction but it will catch some.
        app_name = os.path.basename(app_path)
        icon_filename = info.get("CFBundleIconFile", app_name)
        icon_path = os.path.join(app_path, "Contents/Resources", icon_filename)
        # Add .icns if missing
        if not os.path.splitext(icon_path)[1]:
            icon_path += ".icns"
        if os.path.exists(icon_path):
            return icon_path
        return None

    def save_icon_to_destination(self, input_path: str, output_path: str) -> str:
        """Copies the input icns file path to the output file path as a png.

        Arguments:
            input_path: string path to the icns file
            output_path: string path to the destination

        Returns:
            full path to the output file, or None if the operation failed
        """
        try:
            icon = Image.open(input_path)
            icon.size = (128, 128, 2)
            icon.convert("RGBA")
            icon.load()
            icon.save(output_path, format="png")
            return output_path
        except PermissionError:
            raise ProcessorError(
                f"Unable to save app icon to {output_path} due to permissions."
            )
        except IOError:
            raise ProcessorError(f"Unable to save app icon to path {output_path}.")
        except ValueError:
            raise ProcessorError(
                f"Unable to open a 256px representation of the icon at {input_path}."
            )
        except FileNotFoundError:
            raise ProcessorError(
                f"Unable to open the source icon at path {input_path}."
            )

    def composite_icon(self, icon_path: str, foreground: str, output_path: str) -> str:
        """Creates a composite icon at `output_path` where `foreground` is
        pasted on top of `icon_path` starting at `position` with `padding`
        pixels of padding.

        If the passed `foreground` string is a path that exists, that path is
        used as the source of the foreground image. Otherwise, the `foreground`
        string is assumed to be a base64-encoded string representing an zimage.

        Arguments:
            icon_path: file path to the app icon
            foreground: file path to, or base64 string representation of, a
                template icon to composite on top of the app icon
            output_path: file path to write composited icon

        Returns:
            path to written output composited icon
        """
        # Retrieve or set defaults for position and padding
        position = self.env.get("composite_position", "br")
        padding = self.env.get("composite_padding", 10)

        # If the passed `foreground` doesn't appear to be a local path, but is a
        # base64-encoded string, decode that string so that it can be used by
        # PIL as an image source.
        if not os.path.exists(foreground) and self.is_base64(foreground):
            foreground = io.BytesIO(base64.b64decode(foreground))

        # Open the background image
        bg = Image.open(icon_path)
        # Set the size to the 256px representation (128px square @2x resolution)
        # Note: this is hardcoded as a default for several reasons:
        #   1. This is the default representation size for most first-party
        #      Apple apps.
        #   2. Allowing the recipe to set custom sizes would balloon the number
        #      of input variables to manage.
        #   3. It might be confusing and complicate error handling if a recipe
        #      passed a larger representation that may not be available.
        #   4. PRs accepted for improvements :)
        bg.size = (128, 128, 2)
        bg.convert("RGBA")
        bg.load()
        # Open the foreground template
        fg = Image.open(foreground).convert("RGBA")

        # Determine the coordinates to anchor the pasted image
        if position == "ul":
            coords = (0 + padding, 0 + padding)
        elif position == "ur":
            coords = (bg.size[0] - (fg.size[0] + padding), 0 + padding)
        elif position == "bl":
            coords = (0 + padding, bg.size[1] - (fg.size[1] + padding))
        # This handles the default case of br (bottom right) or any other
        # invalid input
        else:
            coords = (
                bg.size[0] - (fg.size[0] + padding),
                bg.size[1] - (fg.size[1] + padding),
            )

        # Pastes the foreground onto the background. The third parameter
        # re-specifies the foreground as the paste mask to preserve
        # transparency.
        composite = bg.copy()
        composite.paste(fg, coords, fg)
        try:
            composite.save(output_path, format="png")
        except IOError:
            raise ProcessorError(f"Unable to save output to {output_path}")

        # Close the images
        bg.close()
        fg.close()

        return output_path

    def main(self):
        """Main"""
        # Retrieve or set a default output path for the app icon
        if self.env.get("icon_output_path"):
            app_icon_output_path = self.env.get("icon_output_path")
        else:
            recipe_dir = self.env["RECIPE_CACHE_DIR"]
            icon_name = self.env["NAME"]
            app_icon_output_path = os.path.join(recipe_dir, icon_name + ".png")

        # Retrieve the app path
        source = self.env.get("source")

        # Determine if the app path is within a dmg, pkg, or neither
        (dmg_path, dmg, dmg_app_path) = self.parsePathForDMG(source)
        if dmg:
            # Mount dmg and return app path inside
            mount_point = self.mount(dmg_path)
            app_path = os.path.join(mount_point, dmg_app_path)
        elif os.path.splitext(source)[1] == ".pkg":
            # Unpack the package to a temporary directory within the recipe cache
            app_path = self.unpack_pkg(source)
        else:
            # Use the source path as-is, assuming it's a full path to a .app
            app_path = source

        # Extract the app icon to the destination path
        app_icon_path = self.get_app_icon_path(app_path)
        if not app_icon_path:
            raise ProcessorError(
                f"Unable to determine app icon path for app at {app_path}."
            )
        icon_path = self.save_icon_to_destination(app_icon_path, app_icon_output_path)
        self.env["app_icon_path"] = icon_path

        # Create an 'install' version if requested
        if self.env.get("composite_install_path"):
            install_path = self.env.get("composite_install_path")
            install_template = self.env.get(
                "composite_install_template", DEFAULT_ICON_INSTALL
            )
            install_icon = self.composite_icon(
                app_icon_path, install_template, install_path
            )
            self.env["install_icon_path"] = install_icon

        # Create an 'uninstall' version if requested
        if self.env.get("composite_uninstall_path"):
            uninstall_path = self.env.get("composite_uninstall_path")
            uninstall_template = self.env.get(
                "composite_uninstall_template", DEFAULT_ICON_UNINSTALL
            )
            uninstall_icon = self.composite_icon(
                app_icon_path, uninstall_template, uninstall_path
            )
            self.env["uninstall_icon_path"] = uninstall_icon

        # Create an 'update' version if requested
        if self.env.get("composite_update_path"):
            update_path = self.env.get("composite_update_path")
            update_template = self.env.get(
                "composite_update_template", DEFAULT_ICON_UPDATE
            )
            update_icon = self.composite_icon(
                app_icon_path, update_template, update_path
            )
            self.env["update_icon_path"] = update_icon

        # If we mounted a dmg, unmount it
        if dmg:
            self.unmount(dmg_path)

        # If we unpacked a package, delete the temp dir
        if len(self.pkg_cleanup) > 0:
            for directory in self.pkg_cleanup:
                if os.path.isdir(directory):
                    shutil.rmtree(directory)


if __name__ == "__main__":
    processor = AppIconExtractor()
    processor.execute_shell()
