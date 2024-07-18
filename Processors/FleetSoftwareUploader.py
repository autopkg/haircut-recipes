# -*- coding: utf-8 -*-
#
# Copyright 2024 Matthew Warren
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
FleetSoftwareUploader

Uploads a software package to FleetDM. This is a minimal implementation.
"""

import json

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["FleetSoftwareUploader"]


class FleetSoftwareUploader(URLGetter):
    description = "Uploads software to a Fleet instance."
    input_variables = {
        "FLEET_API_KEY": {
            "required": True,
            "description": "API key for Fleet instance."
        },
        "FLEET_BASE_URL": {
            "required": True,
            "description": (
                "The base URL of the Fleet instance."
            )
        },
        "pkg_path": {
            "required": True,
            "description": (
                "Installer package file. Supported packages are PKG, MSI,"
                "EXE, and DEB."
            )
        },
        "team_id": {
            "required": True,
            "description": (
                "The team ID. Adds a software package to the specified team."
            )
        },
        "install_script": {
            "required": False,
            "description": (
                "Command that Fleet runs to install software. If not"
                "specified Fleet runs default install command for each"
                "package type."
            )
        },
        "pre_install_query": {
            "required": False,
            "description": (
                "Query that is pre-install condition. If the query doesn't"
                "return any result, Fleet won't proceed to install."
            )
        },
        "post_install_script": {
            "required": False,
            "description": (
                "The contents of the script to run after install. If the"
                "specified script fails (exit code non-zero) software install"
                "will be marked as failed and rolled back."
            )
        },
        "self_service": {
            "required": False,
            "description": (
                "Boolean. Self-service software is optional and can be"
                "installed by the end user."
            )
        }
    }
    output_variables = {}
    description = __doc__

    def post_software(self, software_path):
        """Posts software to Fleet."""
        endpoint = f"{self.env.get('FLEET_BASE_URL')}/api/v1/fleet/software/package"

        curl_cmd = [
            "/usr/bin/curl",
            "--header",
            f"Authorization: Bearer {self.env.get('FLEET_API_KEY')}",
            "-F",
            f"team_id={self.env.get('team_id')}",
            "-F",
            f"software=@{software_path}",
            endpoint
        ]

        # Directly append optional fields if they exist
        optional_fields = ["install_script", "pre_install_query", "post_install_script", "self_service"]

        for field in optional_fields:
            if self.env.get(field):
                curl_cmd.extend(["-F", f"{field}={self.env.get(field)}"])

        result = self.download_with_curl(curl_cmd)
        return result
    
    def main(self):
        """Main"""
        result = self.post_software(self.env.get("pkg_path"))
        res = json.loads(result)
        message = res.get("message")

        if message == "Resource Already Exists":
            self.output("Software already exists in Fleet.")
        elif message == "Bad request":
            reason = res.get('errors', [{}])[0].get('reason', 'Unknown error')
            raise ProcessorError(f"Failure: {reason}")
        elif message is None:
            self.output("Uploaded package to Fleet successfully.")
        else:
            raise ProcessorError(f"Unexpected response: {message}")

if __name__ == "__main__":
    processor = FleetSoftwareUploader()
    processor.execute_shell()
