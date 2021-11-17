#!/usr/bin/python

from autopkglib import Processor, ProcessorError

import requests
import time

__all__ = ["DatadogEventPoster"]


class DatadogEventPoster(Processor):
    description = "Sends an Event to Datadog when a new package is available."
    input_variables = {
        "DD_API_KEY": {
            "required": True,
            "description": "API key used to post Events to your tenant.",
        },
        "DD_AGGREGATION_KEY": {
            "required": False,
            "description": (
                "An arbitrary string to use for aggregation."
                "Limited to 100 characters. If you specify a key,"
                "all events using that key are grouped together in"
                "the Event Stream."
            ),
        },
        "DD_TAGS": {
            "required": False,
            "description": (
                "A list of tags to apply to the Event. Provide as a single"
                "string, or as an array of multiple strings."
            ),
        },
        "DD_DEVICE_NAME": {
            "required": False,
            "description": "A device name, if applicable. Defaults to none.",
        },
        "DD_HOST": {
            "required": False,
            "description": (
                "Host name to associate with the event. Any tags associated"
                "with the host are also applied to this event. Defaults to"
                "none."
            ),
        },
        "NAME": {
            "required": True,
            "description": "Name of the product.",
        },
        "version": {
            "required": True,
            "description": "Version of the product.",
        },
        "IGNORE_UNCHANGED_DOWNLOAD": {
            "required": False,
            "description": (
                "Boolean. Whether to ignore unchanged downloads and send post "
                "an event unconditionally."
            ),
        },
    }
    output_variables = {
        "datadog_event_id": {"description": "The ID of the posted Event."},
        "datadog_event_url": {"description": "The URL of the posted Event."},
    }
    description = __doc__

    def post_event(self, event):
        """Posts an Event to Datadog."""
        endpoint = "https://api.datadoghq.com/api/v1/events"
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.env.get("DD_API_KEY"),
        }
        response = requests.post(url=endpoint, json=event, headers=headers)
        if 200 <= response.status_code <= 202:
            return response.json()
        else:
            raise ProcessorError(
                f"Unable to post Event. Response code: {response.status_code}. "
                "Full response: {response.text}"
            )

    def main(self):
        """Main"""
        ignore_unchanged = self.env.get("IGNORE_UNCHANGED_DOWNLOAD", False)
        # If the download has not changed, don't send an Event unless the recipe
        # specifies to ignore unchanged downloads.
        if not self.env.get("download_changed") and not ignore_unchanged:
            exit()
        # If the recipe provided DD_TAGS, and provided a single string instead
        # of a list of strings, convert to a list.
        if isinstance(self.env.get("DD_TAGS"), str):
            self.env["DD_TAGS"] = [self.env["DD_TAGS"]]
        # Assemble the JSON payload for the Event.
        event = {
            "alert_type": "success",
            "date_happened": int(time.time()),
            "device_name": self.env.get("DD_DEVICE_NAME"),
            "host": self.env.get("DD_HOST"),
            "priority": "normal",
            "tags": self.env.get("DD_TAGS"),
            "text": (
                f"{self.env.get('NAME')} version {self.env.get('version')} "
                "downloaded and packaged."
            ),
            "title": (
                f"{self.env.get('NAME')} version {self.env.get('version')} "
                "downloaded and packaged."
            ),
        }
        response = self.post_event(event)
        self.env["datadog_event_id"] = response["event"]["id"]
        self.env["datadog_event_url"] = response["event"]["url"]


if __name__ == "__main__":
    processor = DatadogEventPoster()
    processor.execute_shell()
