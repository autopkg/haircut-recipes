#!/usr/local/autopkg/python

from autopkglib import Processor, ProcessorError, URLGetter

import json
import time

__all__ = ["DatadogEventPoster"]


class DatadogEventPoster(URLGetter):
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
        "DD_ENDPOINT": {
            "required": False,
            "description": (
                "The API endpoint to which the event is posted. Defaults to "
                "https://api.datadoghq.com/api/v1/events."
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
        endpoint = self.env.get(
            "DD_ENDPOINT", "https://api.datadoghq.com/api/v1/events"
        )
        # Required headers
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.env.get("DD_API_KEY"),
        }
        # curl options
        curl_opts = [
            "--url",
            endpoint,
            "--request",
            "POST",
            "--data",
            json.dumps(event),
        ]
        # Assemble the curl command
        curl_cmd = self.prepare_curl_cmd()
        self.add_curl_headers(curl_cmd, headers)
        curl_cmd.extend(curl_opts)
        # Post the Event
        response = self.download_with_curl(curl_cmd)
        result = json.loads(response)
        return result

    def main(self):
        """Main"""
        # If the download has not changed, don't send an Event unless the recipe
        # specifies to ignore unchanged downloads.
        ignore_unchanged = self.env.get("IGNORE_UNCHANGED_DOWNLOAD", False)
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
        try:
            response = self.post_event(event)
            self.env["datadog_event_id"] = response["event"]["id"]
            self.env["datadog_event_url"] = response["event"]["url"]
            self.output(f"Posted Datadog Event {response['event']['url']}")
        except Exception as e:
            self.output(f"DatadogEventPoster error: {e}")


if __name__ == "__main__":
    processor = DatadogEventPoster()
    processor.execute_shell()
