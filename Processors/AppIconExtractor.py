# -*- coding: utf-8 -*-
#
# Copyright 2022 Matthew Warren
#
# Extended to work with Windows icons. 2022, Nick Heim
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
And on Windows:
pip install icoextract
"""

import plistlib
import base64
import io
import os
import sys


from autopkglib import Processor, ProcessorError
from autopkglib.DmgMounter import DmgMounter
from autopkglib import is_mac, is_windows

if is_windows():
    import msilib
    try:
        import icoextract
        import magic
        import warnings
    except (ImportError, ModuleNotFoundError):
        raise ProcessorError(
            "The icoextract and magic libraries are required, but where not found. "
            "Please run the following command to install the libraries: "
            "pip install python-magic"
            "pip install python-magic-bin"
            "pip install icoextract"
        )
    warnings.simplefilter('ignore')
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
DEFAULT_ICON_UPDATE = "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"
DEFAULT_ICON_INSTALL = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAFZElEQVR4nO2be0yVdRjHn3O0mXlHwEslgjeWt3nJYSoe0azV1lZbdy8laho1tVx3t/7IZTfmCNRKliOzjdXWVqtFgICURc1MMiJuGiMF0RSIFeE5fZ73BIcXMGid8xbnPR/22fP8zplyfl/e83vf97zvcUgvSCy643JKHI7F0X85BrWq2odhr/4/P+DBJmzEBmyrNXgI89PnZZZRe+SSL5hJ63MLcRXejsOwL3EK8zGNMAqp3eLALjD5CMp+XI59HTem4pME0Uw10SUAJr+YcgB1cw8mKnANIRRQ2zEFwOQTKFnYD4MRDy4jhFyqQXsATF4Xs6M4CoOZKpxOCL9SvQEweSclG5egHUglgIep7QEsp3yCdsGDLkIoaAsgg7IS7UQmAdzpYPKDGNSiVjtxmgDGaAB22/w7MkUDWE2zT+zJOg3gcZodaEcyNIBkmi1oR7I1gAM0d6MdKdIAcmgS0I6UaADHaa5BS4kaFCMLw13i9rilsD5PqptPyH9AjQZQTzMSLeOqgePk2Wkv0Xnx8PNM8Rap/U1P4S2lQQNw0xhHhFZxb1SiLIlcTucj6/SHkln9Fp2luDUAD42lbJ2yTWKHTqPzcez8EUkpe4HOWkIBhAIIBRAKIBQA1VJCAYQCCAUQCiAUQCiAIAxg0pBYuXnMrRI+IEJya7Ok4Ey2tHpaecbMPwmgv+MycUVeb5w96unyR6fel/KmUp7xD34LwMHP9hk7JXKAXmL0cuSXItlTsZMPPS4y8tHbAPo5+knSxK0yY/hsRl40BP3sQD9D8Ad+C0D/6jtm6GV4M1+eLZS9lam8XN+v2TL5KZk6bCadDw1rV/krdF6cDqc8MGGTzBkRx8jMY98mybmWerp/j98CULZN3SFRV0TTmTl0JlcyTrxOBN5f9eDER2X2iHl0Pg6fLZD0yjQ6XhQ/iTFJEjdyESMzFU0/yvMl2+j8g18D0M168+QnjPdtZ3JqP5Z3ftonyproJLkuPJ7OR17dp7L/5F46LlKOXyeLI5bRmWlx/y7Jpdv/n2tAG9OHzZKkSVsJoT8jM2+fTJeDdVmygo/EXCxqHWn7SGzZqJvkrnGrecRMi7vFWCN+aPiOkf/wewDKzOFzjM1cF7GOXGQxTC59TqYPnyU3jr6FR3x88PO7UtpYIo+wPjg7/btWzx/yatmLcvzCMUb+JSABKPoe3zBhc5fJNLY2GCv+gnCXdCSPLWNu2HwZ3H8IIx+6G00re1mKL3zDyP8ELABlblicrI/ZRAhORj50MdSFriPdPaZbzO7yZDl6/mtGgSGgASjzwhbI2piHuoTQE3rsoMcQunsMJAEPQNHdme7WOv+FL4VeLXqjMkW+OneYUWCxJABF3/P3RW8ggr8PQd8K6Rw4fcEBlBVYFoCyKCJBVo1fTwTdh6CTf7Nqt3xen8/IGjQAt1a0BD2xWRG1ls6MTl6PFvWo0UKMS2MNNOZ9T4BZEnmD3BN1P6l7c9fJ60GSHg1ajHFxtIZmLFpK7NCpEh++lKl7OG3O4SDoex61HOPyeAlNLNoR4wYJ3dFei3bEuEUmm2Yp2hHjJqkMmpVoR4zb5NbTvIZ2ZJ0GoAugLoR2ZIqxIyaEOkoE2gnvzdI0GsB7lNvQTnhvl6fRAFwiosegxtgG6PmP7wsTCiHsomxEO2D+yoxCAIMpxThegpsqNH9pqg1CSKDogZHp8SDCg0uZ/EGqQZeJEkI8JR0nYjBRjolMvoDaTpcAFEIYSNmOm9CJfRk3puDTTL6ZaqLbANogiPmUjegSkauxL1GN+biHiX9G7RYH9grCiKYsxni8Eod2UhdRJ1qBG5uwoZM1WID69fkqao/8Ce/EU3dObVaHAAAAAElFTkSuQmCC"
DEFAULT_ICON_UNINSTALL = "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"


class AppIconExtractor(DmgMounter):
    description = (
        "Extracts an app icon and saves it to disk. Optionally creates "
        "composite images."
    )
    input_variables = {
        "source_app": {
            "required": True,
            "description": "Path to the .app from which to extract an icon. "
            "Can point to a path inside a .dmg which will be mounted. This "
            "path may also contain basic globbing characters such as the "
            "wildcard '*', but only the first result will be returned.",
        },
        "icon_file_number": {
            "required": False,
            "default": 0,
            "description": "Numbered index of the icon to get.",
        },
        "msi_icon_name": {
            "required": False,
            "default": "*",
            "description": "Name of the icon entry in the icon table.",
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

    def get_filetype(self, full_file_path: str) -> str:
        """Returns the file type as 3 char string (exe, dll, msi, png, ico).

        Arguments:
            full_file_path: full path to the file to check.

        Returns:
            file type as 3 char string.
        """
        if not os.path.exists(full_file_path):
            return None

        if is_mac():
            return None
            # If the need arises to use this on OSX too, 
            # implement it here...

        if is_windows():
            filetype_raw = magic.from_file(full_file_path)
            if filetype_raw.find("MSI Installer") >= 0:
                filetype_def = "msi"
                self.output("Inside get_filetype msi")
            # elif filetype_raw.find("executable (DLL)") >= 0:
            elif ("executable" in filetype_raw and "(DLL)" in filetype_raw):
                filetype_def = "dll"
            # elif filetype_raw.find("executable (GUI)") >= 0:
            elif ("executable" in filetype_raw and "(GUI)" in filetype_raw):
                filetype_def = "exe"
            # elif filetype_raw.find("executable (console)") >= 0:
            elif ("executable" in filetype_raw and "(console)" in filetype_raw):            
                filetype_def = "exe"
            elif filetype_raw.find("Windows icon resource") >= 0:
                filetype_def = "ico"
            elif filetype_raw.find("PNG image") >= 0:
                filetype_def = "png"
            else:
                self.output("Could not determine file type. Exiting")
                return None
        self.output("Inside get_filetype")
        self.output(filetype_def)
        full_file_path = ""
        return filetype_def

    def get_app_icon_path(self, app_path: str, icon_number: int) -> str:
        """Returns the full path to the app icon specified in an app's
        Info.plist file if possible.

        Arguments:
            app_path: path to the .app

        Returns:
            string path to the app icon, or None if unable to find it
        
        Windows:
            Extracts the icon-group from a PE-file to ICO-file.
            Returns the path to the extracted ICO-file.
            An ICO-file can be red by the following (PIL-) functions.
        """
        if not os.path.exists(app_path):
            return None
        if is_mac():                                                                                        
            try:
                with open(os.path.join(app_path, "Contents/Info.plist"), "rb") as app_plist:
                    info = plistlib.load(app_plist)
            except plistlib.InvalidFileException:
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

        if is_windows():
            # if app_path and os.path.isfile(app_path):
            # if app_path:
            self.output(app_path)
            file_name, file_ext = os.path.splitext(app_path)
            icon_path = file_name + ".ico"
            try:
                icoExtInst = icoextract.IconExtractor(app_path)
            except RuntimeError:
                f"Unable to open {app_path} icon extraction."
            icoExtInst.export_icon(icon_path, num=icon_number)
            self.output(icon_path)

        if os.path.exists(icon_path):
            return icon_path
        return None

    def save_icon_to_destination(self, input_path: str, output_path: str) -> str:
    # def save_icon_to_destination(self, input_path: str, output_path: str, icon_number: int) -> str:
        """Copies the input icns file path to the output file path as a png.

        Arguments:
            input_path: string path to the icns file
            output_path: string path to the destination

        Returns:
            full path to the output file, or None if the operation failed
        """

        try:
            icon = Image.open(input_path)
            # self.output(icon.info["sizes"])
            if is_mac():
                if (128, 128, 2) in icon.info["sizes"]:
                    icon.size = (128, 128, 2)
                    self.output("128")
                elif (256, 256) in icon.info["sizes"]:
                    icon.size = (256, 256)
                else:
                    self.output("Resizing icon to 256px.")
                    icon = icon.resize((256, 256))

            if is_windows():
                if icon.format == 'ICO':
                    if (1024, 1024) in icon.info["sizes"]:
                        self.output("Resizing 1024 icon to 256px.")
                        icon = icon.resize((256, 256))
                    elif (512, 512) in icon.info["sizes"]:
                        self.output("Resizing 512 icon to 256px.")
                        icon = icon.resize((256, 256))
                    elif (256, 256) in icon.info["sizes"]:
                        icon.size = (256, 256)
                    else:
                        self.output("Resizing icon to 256px.")
                        icon = icon.resize((256, 256))
                elif icon.format == 'PNG':
                    if icon.size == (1024, 1024):
                        self.output("Resizing 1024 icon to 256px.")
                        icon = icon.resize((256, 256))
                    elif icon.size == (512, 512):
                        self.output("Resizing 512 icon to 256px.")
                        icon = icon.resize((256, 256))
                    elif icon.size == (256, 256):
                        # icon.size = (256, 256)
                        self.output("No resize, already 256px.")
                    else:
                        self.output("Resizing icon to 256px.")
                        icon = icon.resize((256, 256))
                else:
                    self.output("Unrecognizeable im<age format! Not ICO or PNG.")

            self.output(icon.size)
            # icon.ico.getimage(icon.size)
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
        # Reset invalid position input to the default of "br" and output a
        # Processor message
        if position not in ["ul", "ur", "br", "bl"]:
            self.output(
                f"Reset invalid composite_position input '{position}' to the default value 'br'."
            )
            position = "br"
        padding = self.env.get("composite_padding", 10)
        # Reset invalid padding input to the default value '10' and output a
        # Processor message
        if not isinstance(padding, int) and padding >= 0:
            self.output(
                f"Reset invalid composite_padding input '{padding}' to the default value '10'."
            )
            padding = 10

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
        if is_mac():
            if (128, 128, 2) in bg.info["sizes"]:
                bg.size = (128, 128, 2)
            elif (256, 256) in bg.info["sizes"]:
                bg.size = (256, 256)
            else:
                self.output("Resizing icon to 256px.")
                bg = bg.resize((256, 256))
        # Could not figure out so far, how to extract embedded icons from the file.
        # So we take the head image and resize it to 256px.
        # Improvements are welcome.
        if is_windows():
            if bg.format == 'ICO':
                if (1024, 1024) in bg.info["sizes"]:
                    self.output("Resizing 1024 icon to 256px.")
                    bg = bg.resize((256, 256))
                elif (512, 512) in bg.info["sizes"]:
                    self.output("Resizing 512 icon to 256px.")
                    bg = bg.resize((256, 256))
                elif (256, 256) in bg.info["sizes"]:
                    bg.size = (256, 256)
                else:
                    self.output("Resizing icon to 256px.")
                    bg = bg.resize((256, 256))
            elif bg.format == 'PNG':
                if bg.size == (1024, 1024):
                    self.output("Resizing 1024 icon to 256px.")
                    bg = bg.resize((256, 256))
                elif bg.size == (512, 512):
                    self.output("Resizing 512 icon to 256px.")
                    bg = bg.resize((256, 256))
                elif bg.size == (256, 256):
                    # bg.size = (256, 256)
                    self.output("No resize, already 256px.")
                else:
                    self.output("Resizing icon to 256px.")
                    bg = bg.resize((256, 256))
            else:
                self.output("Unrecognizeable image format! Not ICO or PNG.")
        bg.convert("RGBA")
        # Check the file mode. If it was not changed to "RBGA",
        # the source is most likeley grayscale.
        # So we create an new empty color image and copy the background image to it.
        # Otherwise, we can not stamp a color forground image to it.
        # It would end up in grayscale too.
        if not bg.mode == "RGBA":
            img = Image.new("RGBA", (256,256), color=(0,0,0))
            img.paste(bg, (0,0))
            bg = img.copy()
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
        # composite.paste(fg, coords, fg)
        composite.paste(fg, coords)
        try:
            composite.save(output_path, format="png")
        except IOError:
            raise ProcessorError(f"Unable to save output to {output_path}")

        # Close the images
        bg.close()
        fg.close()

        return output_path

    def get_msi_icon_lib(self, app_path: str, icon_name: str) -> str:
        """Windows: Extracts the icon library from the msi-file.
        It returns the full path to the msi icon library in the cache folder.

        Arguments:
            app_path: path to the msi file

        Returns:
            string path to the icon library, or None if unable to find it
        
        """
        if not os.path.exists(app_path):
            return None

        if is_mac():
            return None

        if is_windows():
            self.output(app_path)
            self.output("Inside_Get_MSI_Icon_Lib")
            file_name, file_ext = os.path.splitext(app_path)
            icon_path = file_name + ".ico"
            sys.path.append(self.env['DTF_PATH'])
            self.output(icon_name)
            icon_path = self.env["RECIPE_CACHE_DIR"] + "\downloads\MSI_ICON_LIB.exe"
            import clr
            clr.AddReference("Microsoft.Deployment.WindowsInstaller")
            from Microsoft.Deployment.WindowsInstaller import Database
            from Microsoft.Deployment.WindowsInstaller import DatabaseOpenMode
            tmode = DatabaseOpenMode.ReadOnly
            win_inst_db = Database(app_path, tmode)
            if icon_name == "*":
                win_inst_view = win_inst_db.OpenView("SELECT `Name`,`Data` FROM Icon",None)
            else:
                win_inst_view = win_inst_db.OpenView("SELECT `Name`,`Data` FROM Icon WHERE `Name`= '" + icon_name +"'",None)
            win_inst_view.Execute()
            win_inst_rec = win_inst_view.Fetch()
            if not win_inst_rec == None:
                win_inst_rec.GetStream(2, icon_path)
                if icon_name == "*":
                    icon_name = win_inst_rec.GetString(1)
            else:
                self.output("Unable to extract icon from MSI")

            win_inst_rec.Dispose()
            win_inst_view.Dispose()
            win_inst_db.Dispose()
            
            # try:
                # icoExtInst = icoextract.IconExtractor(app_path)
            # except RuntimeError:
                # f"Unable to open {app_path} icon extraction."
            # icoExtInst.export_icon(icon_path, num=icon_number)
            self.output(icon_path)

        if os.path.exists(icon_path):
            return icon_path
        return None

    def main(self):
        """Main"""
        # Retrieve the app path
        source_app = self.env.get("source_app")

        # Read the icon number from the input var.
        icon_file_number = int(self.env.get("icon_file_number", 0))
        # Determine if the app path is within a dmg
        (dmg_path, dmg, dmg_app_path) = self.parsePathForDMG(source_app)
        if dmg:
            # Mount dmg and return app path inside
            mount_point = self.mount(dmg_path)
            app_path = os.path.join(mount_point, dmg_app_path)
        else:
            # Use the source path as-is, assuming it's a full path to a .app
            app_path = source_app

        if is_windows():
            src_app_file, src_file_ext = os.path.splitext(source_app)
            file_type_ext = self.get_filetype(source_app)
            self.output("Main_Win")
            self.output(src_file_ext)
            # if src_file_ext == ".msi":
            if file_type_ext == "msi":
                msi_icon_name = self.env.get("msi_icon_name")
                self.output("MainWinMSI")
                app_icon_path_temp = self.get_msi_icon_lib(source_app, msi_icon_name)
                file_type_ext = self.get_filetype(app_icon_path_temp)
                self.output(app_icon_path_temp)
                self.output("MainWinMSI")
                self.output(file_type_ext)
                if file_type_ext == "exe" or file_type_ext == "dll":
                    app_icon_path = self.get_app_icon_path(app_icon_path_temp, icon_file_number)
                    self.output(app_icon_path_temp)
                elif file_type_ext == "ico":
                    app_icon_path = app_icon_path_temp
                else:
                    self.output("Could not determine file type from MSI. Exiting")
                    return None
            elif file_type_ext == "exe":
                app_icon_path = self.get_app_icon_path(source_app, icon_file_number)
            elif file_type_ext == "png":
                app_icon_path = source_app
            elif file_type_ext == "ico":
                app_icon_path = source_app
            else:
                self.output("Could not determine input file type. Exiting")
                return None
        else:
            # Extract the app icon to the destination path
            app_icon_path = self.get_app_icon_path(app_path, icon_file_number)
            if not app_icon_path:
                raise ProcessorError(
                    f"Unable to determine app icon path for app at {app_path}."
                )
            
        # Retrieve or set a default output path for the app icon
        if self.env.get("icon_output_path"):
            app_icon_output_path = self.env.get("icon_output_path")
            if not os.path.isdir(os.path.dirname(app_icon_output_path)):
                os.makedirs(os.path.dirname(app_icon_output_path))
        else:
            recipe_dir = self.env["RECIPE_CACHE_DIR"]
            icon_name = self.env["NAME"]
            app_icon_output_path = os.path.join(recipe_dir, icon_name + ".png")
        
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


if __name__ == "__main__":
    processor = AppIconExtractor()
    processor.execute_shell()
