# About the AnacondaCustom recipe

The `AnacondaCustom` pkg recipe allows you to create package that will do a
customizable installation of Anaconda.

The standard .pkg provided by Continuum does not allow you to specify an 
installation directory, skip attempts to modify the logged-in-user's Bash path, 
etc. Their shell script installation, however, does provide this flexibility.

This recipe builds off hansen-m's excellent and flexible [Anaconda download 
recipe](https://github.com/autopkg/hansen-m-recipes/blob/master/Continuum/Anaconda.download.recipe)
by adding a postinstall script to run the Anaconda installer shell script with
custom options. It also symlinks all the Anaconda binaries to locations under
`/usr/local/bin` so that they're automatically available to all current and
future users on the system without needing to edit any Bash profiles.

## Input keys

This recipe supports all the input keys available in its parent recipe, plus
a few additional keys.

- `NAME`
    The name of your package, which will be output in the format of `%NAME%-%version%.pkg`

    Default: `AnacondaCustom`
- `INSTALLER_TYPE`
    Whether to download the `pkg` installer or the `sh` shell script. You must
    use the `sh` option for this recipe to work correctly!

    Default: `sh`
- `PYTHON_MAJOR_VERSION`
    The major version of Python for which to download a compatible version of
    Anaconda. Use `2` or `3`

    Default: `2`
- `PREFIX_DIR`
    The target directory to which you want to install Anaconda, or as Continuum
    calls it, the "prefix directory."

    Default: `/usr/local/anaconda`
- `CONDARC_CONTENTS`
    Contents of the top-level or "admin" `.condarc` file. This file is placed
    in the "prefix directory" and automatically loaded for all users. See the
    Continuum documentation for [using an admin .condarc file](https://conda.io/docs/user-guide/configuration/admin-multi-user-install.html)

    **Important**: Make very sure this input key is valid YAML syntax, paying 
    special attention to indentation. The multiline string you place in your
    recipe override might look funny; be sure to use 2 spaces instead of tabs
    for indentation, and do not unnecessarily indent lines in this string; they
    should be flush with the left side of your text editor ignoring any other
    XML-specific indentation!

    Leave this input key blank if you do not wish to use an admin `.condarc`.

    Example:
```
        <string># Add default channels
channels:
  - defaults
  - https://example.com</string>
```

## postinstall script

This recipe's postinstall script does the following:

- Runs the Anaconda installer shell script with these options:
    - `-b` run in batch mode so no manual intervention is required
    - `-f` ignore errors if prefix dir already exists
    - `-s` skip attempts to edit the logged-in-user's default Bash path
    - `-p` specify the prefix dir
- Symlinks all Anaconda binaries from `<PREFIX_DIR>/bin` to `/usr/local/bin` so
they're availbe for all users without having to edit their Bash path
- Writes the contents of `CONDARC_CONTENTS` to `<PREFIX_DIR>/.condarc` for use
as an admin config file
