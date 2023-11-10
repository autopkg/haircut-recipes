#!/usr/local/autopkg/python

import json

from autopkglib.URLGetter import URLGetter

__all__ = ["JSONWebhookSender"]


class JSONWebhookSender(URLGetter):
    description = "Sends a JSON webhook payload to a URL."
    input_variables = {
        "json_webhook_url": {
            "required": True,
            "description": "URL of the webhook.",
        },
        "json_webhook_request_method": {
            "required": False,
            "description": "HTTP method to use. Defaults to POST.",
            "default": "POST",
        },
        "json_webhook_request_headers": {
            "required": False,
            "description": (
                "Optional dictionary of headers to include with the webhook "
                "request."
            ),
        },
        "NAME": {
            "required": True,
            "description": "Name of the product.",
        },
        "version": {
            "required": False,
            "description": "Version of the product.",
        },
        "json_webhook_include_autopkg_variables": {
            "required": False,
            "description": (
                "Optional list of existing AutoPkg parameters - including "
                "input parameters and output parameters from previous "
                "processors - to include in the webhook."
            ),
        },
        "json_webhook_additional_fields": {
            "required": False,
            "description": (
                "Optional dict (key/value pairs) of additional (static) "
                "fields to include in the webhook payload."
            ),
        },
    }
    output_variables = {
        "json_webhook_response": {
            "description": "Response returned by the webhook.",
        },
    }
    description = __doc__

    def send_webhook(self, payload):
        """Sends the payload to the specified URL

        Args:
            payload (dict): Dictionary representing the payload contents.

        Returns
            dict: server response
        """
        endpoint = self.env.get("json_webhook_url")
        # Read any custom request headers, then explicity set the
        # Content-Type header to application/json.
        headers = self.env.get("json_webhook_request_headers", {})
        headers["Content-Type"] = "application/json"
        # Set curl options.
        curl_opts = [
            "--url",
            endpoint,
            "--request",
            self.env.get("json_webhook_request_method"),
            "--data",
            json.dumps(payload),
        ]
        # Assemble the curl command.
        curl_cmd = self.prepare_curl_cmd()
        self.add_curl_headers(curl_cmd, headers)
        curl_cmd.extend(curl_opts)
        # Send the webhook.
        response = self.download_with_curl(curl_cmd)
        result = json.loads(response)
        return result

    def main(self):
        """Main"""
        # Create a webhook payload and populate the NAME field.
        payload = {
            "name": self.env.get("NAME"),
        }
        # If version is included, add it to the payload.
        if self.env.get("version"):
            payload["version"] = self.env.get("version")
        # Add any additional fields provided in
        # json_webhook_include_autopkg_variables.
        included_vars = self.env.get(
            "json_webhook_include_autopkg_variables",
            [],
        )
        for field in included_vars:
            payload[field] = self.env.get(field)
        # Add any additional fields provided in json_webhook_additional_fields.
        if self.env.get("json_webhook_additional_fields"):
            payload.update(self.env.get("json_webhook_additional_fields"))
        # Send the webhook.
        try:
            response = self.send_webhook(payload)
            self.env["json_webhook_response"] = response
        except Exception as e:
            self.output(f"JSONWebhookSender error: {e}")


if __name__ == "__main__":
    processor = JSONWebhookSender()
    processor.execute_shell()
