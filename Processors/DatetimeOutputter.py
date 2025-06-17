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

from datetime import datetime, timedelta, timezone
import re

from autopkglib import Processor, ProcessorError  # noqa: F401

__all__ = ["DatetimeOutputter"]


class DatetimeOutputter(Processor):
    """This processor outputs the date and time it was run within a recipe. It
    can also format that datetimestamp, and output past and future datetimes."""

    description = (
        "Outputs the current datetime, optionally in a format of your choice. "
        "Optionally output future or past datetimes."
    )
    input_variables = {
        "datetime_format": {
            "required": False,
            "description": "An optional Python strftime-compatible datetime "
            "format. See <https://strftime.org/> for examples. Defaults to ISO "
            "8601 format.",
        },
        "use_utc": {
            "required": False,
            "description": "If set to true, datetimes are based on UTC rather "
            "than local time.",
        },
        "deltas": {
            "required": False,
            "description": "An optional array of time deltas – past or future "
            "datetimes – to output. Each time delta should be specified as a "
            "dictionary of keys defining the desired output datetime. Those "
            "keys are: `output_name` which defines the output variable name "
            "for the time delta, `direction` which is either `future` or "
            "`past`, and `interval` which is a dictionary of keys specifying "
            "Python timedelta-compatible intervals to add or subtract from the "
            "current datetime. Valid keys are: `days`, `seconds`, "
            "`microseconds`, `milliseconds`, `minutes`, `hours`, and `weeks`. "
            "Optionally, you may also include a `format` which is a Python "
            "strftime-compatible datetime format. See the Python docs at "
            "<https://docs.python.org/3/library/datetime.html#timedelta-objects> "
            "for specifics on `timedelta` and the README for this Processor "
            "for examples.",
        },
    }
    output_variables = {
        "datetime": {"description": "The current datetime."},
        "datetime_deltas": {
            "description": "Any requested datetime deltas. "
            "Note the actual name of output variables depends on the input "
            "variable `output_name` defined within any `deltas` dictionaries."
        },
    }
    description = __doc__

    def main(self):
        # Store the current datetime, based on UTC if requested.
        current_datetime = datetime.now()
        if self.env.get("use_utc", False):
            self.output("Using UTC instead of local time.", verbose_level=2)
            current_datetime = current_datetime.now(timezone.utc)

        # Format and output the datetime using the specified format, or the
        # default format ISO 8601 format.
        output_format = self.env.get("datetime_format", "%Y-%m-%dT%H:%M:%S.%f%z")
        try:
            self.env["datetime"] = current_datetime.strftime(output_format)
        except (TypeError, NameError) as e:
            raise ProcessorError(f"Unable to format dateime: {e}")

        # Create and output any requested datetime deltas.
        deltas = self.env.get("deltas")
        if deltas:
            self.output("Calculating time deltas.", verbose_level=2)
            for delta_index, delta in enumerate(deltas):
                try:
                    diff = timedelta(**delta["interval"])
                    if delta["direction"] == "past":
                        base_datetime = current_datetime - diff
                    else:
                        base_datetime = current_datetime + diff
                    format_string = delta.get("format", "%Y-%m-%dT%H:%M:%S.%f%z")
                    # Check if the format string hardcodes a time (e.g., ends with 'T17:55:00Z')
                    # This regex looks for a literal time at the end of the format string, e.g. T17:55:00Z
                    hardcoded_time_regex = r".*T(\d{2}):(\d{2}):(\d{2})Z$"
                    hardcoded_time_match = re.match(hardcoded_time_regex, format_string)
                    if hardcoded_time_match:
                        # If a hardcoded time is found, set the base_datetime to that time
                        hour, minute, second = map(int, hardcoded_time_match.groups())
                        base_datetime = base_datetime.replace(hour=hour, minute=minute, second=second, microsecond=0)
                    formatted_datetime = base_datetime.strftime(format_string)
                    output_var_name = delta["output_name"]
                    self.env[output_var_name] = formatted_datetime
                    # Print the output variable and value to stdout for recipe visibility
                    self.output(f"Done setting {output_var_name} to: {formatted_datetime}")
                except (TypeError, NameError, ValueError) as delta_err:
                    self.output(f"Error processing delta #{delta_index + 1}: {str(delta_err)}")
                    continue


if __name__ == "__main__":
    processor = DatetimeOutputter()
    processor.execute_shell()
