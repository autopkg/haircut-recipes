#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Graham Pugh
# Copyright 2019 Matthew Warren / haircut
#
# Based on the 'Slacker' PostProcessor by Graham R Pugh
# https://grahamrpugh.com/2017/12/22/slack-for-autopkg-jssimporter.html
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


import json
import os.path
import requests
import subprocess
from autopkglib import Processor, ProcessorError


# Set the webhook_url to the one provided by Hangouts Chat
# See https://developers.google.com/hangouts/chat/how-tos/webhooks
__all__ = ["HangoutsChatNotifier"]

class HangoutsChatNotifier(Processor):
    description = ("Posts a Simple Text message to a Hangouts Chat room"
                   "via webhook based on output of an autopkg run.")
    input_variables = {
        "NAME": {
            "required": False,
            "description": ("Title of the ")
        },
        "version": {
            "required": False,
            "description": ("Dictionary of added or changed values.")
        },
        "hangoutschat_webhook_url": {
            "required": False,
            "description": ("Hangouts Chat webhook url.")
        }
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):
        app_name = self.env.get("NAME")
        app_version = self.env.get("version")
        webhook_url = self.env.get("hangoutschat_webhook_url")
        msg = "✨ *{}* version _{}_ was downloaded by autopkg".format(app_name, app_version)
        hangoutschat_data = {
            "text": msg
        }
        response = requests.post(webhook_url, json=hangoutschat_data)
        if response.status_code != 200:
            raise ValueError(
                            'Request to Hangouts Chat returned an error %s, the response is:\n%s'
                            % (response.status_code, response.text)
                            )


if __name__ == "__main__":
    processor = HangoutsChatNotifier()
    processor.execute_shell()
