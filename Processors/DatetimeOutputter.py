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

from datetime import datetime, timedelta

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
            current_datetime = current_datetime.utcnow()

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
            for delta in deltas:
                try:
                    # Calculate the final datetime.
                    diff = timedelta(**delta["interval"])
                    if delta["direction"] == "past":
                        final = current_datetime - diff
                    else:
                        final = current_datetime + diff
                    # Output using the supplied output_name and dattime_format,
                    # or the default ISO 8601 format.
                    output_format = delta.get(
                        "datetime_format", "%Y-%m-%dT%H:%M:%S.%f%z"
                    )
                    self.env[delta["output_name"]] = final.strftime(output_format)
                except (TypeError, NameError) as e:
                    raise ProcessorError(
                        f"Missing or incorrectly-named required keys in time delta: {e}"
                    )


if __name__ == "__main__":
    processor = DatetimeOutputter()
    processor.execute_shell()
