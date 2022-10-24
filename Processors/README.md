# Processors

## Using these processors

Add this repo to AutoPkg (by running `autopkg repo-add haircut-recipes`), then
call a Processor using [Shared Processor][sharedprocessor] syntax, e.g.
`com.github.haircut.processors/AppIconExtractor`.

## AppIconExtractor

Please see my [article demonstrating AppIconExtractor][mbaie] for full
details and examples.

## DatetimeOutputter

Outputs the current datetime, optionally in a format of your choice. Optionally output future or past datetimes.

Please see my [article demonstrating DatetimeOutputter][mbdo] for full
details and additional examples.

### Input variables

- **datetime\_format:**
  - **required:** False
  - **description:** An optional Python strftime-compatible datetime format.  
    See <https://strftime.org/> for examples. Defaults to ISO 8601 format.
- **use\_utc:**
  - **required:** False
  - **description:** If set to true, datetimes are based on UTC rather than
    local time.
- **deltas:**
  - **required**: False
  - **description:** An optional array of time deltas – past or future datetimes
    – to output. Each time delta should be specified as a dictionary of keys
    defining the desired output datetime. Those keys are: `output_name` which
    defines the output variable name for the time delta, `direction` which is
    either `future` or `past`, and `interval` which is a dictionary of keys
    specifying Python timedelta-compatible intervals to add or subtract from the
    current datetime. Valid keys are: `days`, `seconds`, `microseconds`,
    `milliseconds`, `minutes`, `hours`, and `weeks`. Optionally, you may also
    include a `format` which is a Python strftime-compatible datetime format.
    See the Python docs at
    <https://docs.python.org/3/library/datetime.html#timedelta-objects> for
    specifics on `timedelta` and the README for this Processor for examples.

### Output variables

- **datetime:**
  - **description**: The current datetime.
- **datetime_deltas:**
  - **description:** Any requested datetime deltas. Note that the actual
      name of output variables depends on the input variable `output_name`
      defined within any `deltas` dictionaries.

### Examples

You can output the current datetime in ISO 8601 format by calling the processor
with no arguments

XML:

```xml
<key>Process</key>
<array>
    <dict>
        <key>Processor</key>
        <string>com.github.haircut.processors/DatetimeOutputter</string>
    </dict>
</array>
```

YAML:

```yaml
Process:
  - Processor: com.github.haircut.processors/DatetimeOutputter
```

This will output a new `datetime` variable you can use in subsequent processors.

You can optionally base the outputted datetime on UTC rather than local time,
and specify a custom Python strftime-compatible format for the outputted
datetime.

XML:

```xml
<key>Process</key>
<array>
    <dict>
        <key>Processor</key>
        <string>com.github.haircut.processors/DatetimeOutputter</string>
        <key>Arguments</key>
        <dict>
            <key>use_utc</key>
            <true/>
            <key>datetime_format</key>
            <string>%A, %B %e, %Y</string>
        </dict>
    </dict>
</array>
```

YAML:

```yaml
Process:
  - Processor: com.github.haircut.processors/DatetimeOutputter
    Arguments:
      use_utc: True
      datetime_format: "%A, %B %e, %Y"
```

Finally, this example demonstrates outputting two time deltas; 4 hours and 30 minutes in the past, and 1 week in the future, both in different formats.

XML:

```xml
<key>Process</key>
<array>
    <dict>
        <key>Processor</key>
        <string>com.github.haircut.processors/DatetimeOutputter</string>
        <key>Arguments</key>
        <dict>
            <key>deltas</key>
            <array>
                <dict>
                    <key>direction</key>
                    <string>past</string>
                    <key>interval</key>
                    <dict>
                        <key>hours</key>
                        <integer>4</integer>
                        <key>minutes</key>
                        <integer>30</integer>
                    </dict>
                    <key>output_name</key>
                    <string>past_time</string>
                </dict>
                <dict>
                    <key>datetime_format</key>
                    <string>%Y-%m-%dT%H:%M:%S</string>
                    <key>direction</key>
                    <string>future</string>
                    <key>interval</key>
                    <dict>
                        <key>weeks</key>
                        <integer>1</integer>
                    </dict>
                    <key>output_name</key>
                    <string>force_after_date</string>
                </dict>
            </array>
        </dict>
    </dict>
</array>
```

YAML:

```yaml
Process:
  - Processor: com.github.haircut.processors/DatetimeOutputter
    Arguments:
      deltas:
        - output_name: past_time
          direction: past
          interval:
            hours: 4
            minutes: 30
        - output_name: force_after_date
          direction: future
          interval:
            weeks: 1
          datetime_format: "%Y-%m-%dT%H:%M:%S"
```

This example would output the following variables:

- `datetime`: the current local datetime in the default ISO 8601 format.
- `past_time`: 4 hours and 30 minutes ago, in local time, in the default ISO
  8601 format.
- `force_after_date`: 1 week from now, in local time, in a custom format.

## StringInserter

This processor is useful for affixing strings with a prefix or suffix, or for simply inserting one string into another.
Most commonly, that destination string would be another output variable from some other AutoPkg processor.

### Input variables

- **input_string**:
  - required: True
  - description: The string to insert `insertion_string` into.
- **insertion_string**:
  - required: True
  - description: The string to insert.
- **index**:
  - required: False
  - description: The numerical index at which to insert the string, or 'suffix'.
- **output_variable_name**:
  - required: False
  - description: The name of the output variable to set. Defaults to 'output_string'.

### Output variables

- **output_string**:
  - description: The final string with the inserted string.
                 Note that`output_string` is the default value, but can be overridden by providing `output_variable_name`.

### Examples

The following example will add the text `Build ` at index 1 in a `version_regex` variable, overwriting the existing value of that variable.

```yaml
- Processor: com.github.haircut.processors/StringInserter
  Arguments:
    input_string: "%version_regex%"
    insertion_string: "Build "
    index: 1
    output_variable_name: "version_regex"
```

Results:

Before: `^(\d{5,}.*)$`

After: `^Build (\d{5,}.*)$`

The following example will add a suffix of ` beta` to the existing `version` variable and output a new variable with the default name `output_string`.
This uses the special "suffix" value for `index`.

```yaml
- Processor: com.github.haircut.processors/StringInserter
  Arguments:
    input_string: "%version%"
    insertion_string: " beta"
    index: "suffix"
```

Results:

`version`: `4.3.1`

`output_string`: `4.3.1 beta`

[sharedprocessor]: <https://github.com/autopkg/autopkg/wiki/Processor-Locations#shared-recipe-processors>
[mbaie]: <https://www.macblog.org/posts/appiconextractor/>
[mbdo]: <https://www.macblog.org/posts/output-datetime-autopkg/>
