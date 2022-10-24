#!/usr/local/autopkg/python

from autopkglib import Processor  # noqa: F401

import json
import time

__all__ = ["StringInserter"]


class StringInserter(Processor):
    description = "Inserts a string into another string at a specified index."
    input_variables = {
        "input_string": {
            "required": True,
            "description": "The string to insert `insertion_string` into.",
        },
        "insertion_string": {
            "required": True,
            "description": "The string to insert.",
        },
        "index": {
            "required": True,
            "description": "The index at which to insert the string.",
        },
        "output_variable_name": {
            "required": False,
            "description": "The name of the output variable to set. Defaults to 'output_string'.",
        },
    }
    output_variables = {
        "output_string": {
            "description": (
                "The final string with the inserted string. Note that "
                "`output_string` is the default value, but can be overridden "
                "by providing `output_variable_name`."
            )
        },
    }
    description = __doc__

    def main(self):
        """Main"""
        input_string = self.env["input_string"]
        insertion_string = self.env["insertion_string"]
        index = self.env.get("index", 0)
        output_variable_name = self.env.get("output_variable_name", "output_string")

        if index == "suffix":
            output_string = input_string + insertion_string
        else:
            output_string = input_string[:index] + insertion_string + input_string[index:]

        self.env[output_variable_name] = output_string
        self.output(
            f"Inserted '{insertion_string}' into '{input_string}' at index {index} to output '{output_string}'."
        )


if __name__ == "__main__":
    processor = StringInserter()
    processor.execute_shell()
