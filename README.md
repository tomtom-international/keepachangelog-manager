# (Keep a) Changelog Manager

Python package allowing you to manage your `CHANGELOG.md` files

![gif](https://raw.githubusercontent.com/tomtom-international/keepachangelog-manager/master/resources/usage.gif)

## Installation

In order to install the python scripts you can use the following command:

```sh
% pip install keepachangelog-manager
```

## Usage

```
Usage: changelogmanager [OPTIONS] COMMAND [ARGS]...

  (Keep a) Changelog Manager

Options:
  --config TEXT                   Configuration file
  --component TEXT                Name of the component to update
  -f, --error-format [llvm|github]
                                  Type of formatting to apply to error
                                  messages
  --help                          Show this message and exit.

Commands:
  add             Command to add a new message to the CHANGELOG.md
  create          Command to create a new (empty) CHANGELOG.md
  github-release  Deletes all releases marked as 'Draft' on GitHub and...
  release         Release changes added to [Unreleased] block
  to-json         Exports the contents of the CHANGELOG.md to a JSON file
  validate        Command to validate the CHANGELOG.md for inconsistencies
  version         Command to retrieve versions from a CHANGELOG.md
```

### Validate the layout of your CHANGELOG.md
Although every command will validate the contents of your `CHANGELOG.md`, the
command `validate` will do nothing more than this.

```sh
% changelogmanager validate
```

You can change the error messages to GitHub format by providing the `--error-format`
option:

```sh
% changelogmanager --error-format github validate
```

### Create a new CHANGELOG.md
Creating a new `CHANGELOG.md` file is as simple as running:

```sh
% changelogmanager create
```

This will create an empty changelog in the current working directory:

```md
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

### Add a change to your changelog
The `add` command can be used to add a new change to the `CHANGELOG.md`:

```
Usage: changelogmanager add [OPTIONS]

  Command to add a new message to the CHANGELOG.md

Options:
  -t, --change-type [added|changed|deprecated|removed|fixed|security]
                                  Type of the change
  -m, --message TEXT              Changelog entry
  --help                          Show this message and exit.
```

The options `--change-type` and `--message` can be omitted, providing a simple user
interface for defining the contents:

```sh
% changelogmanager add

? Specify the type of your change 
? Message of the changelog entry to add  
? Apply changes to your CHANGELOG.md  (Y/n)

```

In addition, you can provide a single command as well:

```sh
% changelogmanager add --change-type added --message "Added an example to the documentation"
```

This will create a new `[Unreleased]` entry in your `CHANGELOG.md`:

```md
## [Unreleased]
### Added
- Added an example to the documentation
```

### Retrieving versions

The `version` command can be used to retrieve versions based on the `CHANGELOG.md`:

```
Usage: changelogmanager version [OPTIONS]

  Command to retrieve versions from a CHANGELOG.md

Options:
  -r, --reference [previous|current|future]
                                  Which version to retrieve
  --help                          Show this message and exit.
```

Taking the following `CHANGELOG.md` as reference:

```md
## [Unreleased]
### Added
- Added an example to the documentation


## [2.1.0] - 2022-03-09
### Fixed
- Handle empty `CHANGELOG.md` files gracefully

## [2.0.0] - 2022-03-08
### Fixed
- No longer throw exceptions when releasing `CHANGELOG.md` containing only an `[Unreleased]` section

### Added
- Added support for creating a new `CHANGELOG.md` file, using the `create` command
```

```sh
% changelogmanager version
2.1.0

% changelogmanager version --reference previous
2.0.0

% changelogmanager version --reference future
2.2.0
```

> **NOTE**: The `future` version is based on the changes listed in the `[Unreleased]` section in your `CHANGELOG.md` (applying Semantic Versioning)

### Release a new CHANGELOG.md

The `release` command allows you to "release" any "unreleased" changes:

```
Usage: changelogmanager release [OPTIONS]

  Release changes added to [Unreleased] block

Options:
  --override-version TEXT  Version to release, defaults to auto-resolve
  --help                   Show this message and exit.
```

For example:

```sh
% changelogmanager release
```

This will rename the `[Unreleased]` section and add the current date next to it, marking
the change as "Released"

### Export your CHANGELOG.md to JSON

The `to-json` command allows you to export the `CHANGELOG.md` file into a JSON format:

```
Usage: changelogmanager to-json [OPTIONS]

  Exports the contents of the CHANGELOG.md to a JSON file

Options:
  --file-name TEXT  Filename of the JSON output
  --help            Show this message and exit.
```

For example:

```sh
% changelogmanager to-json
```

This will create a file named `CHANGELOG.json` contain content similar to:

```json
{
    "3.2.0": {
        "metadata": {
          "version": "3.2.0",
          "release_date": "2022-08-18",
          "semantic_version": {
            "major": 3,
            "minor": 2,
            "patch": 0,
            "prerelease": null,
            "buildmetadata": null
          }
        },
        "added": [
            "The command `to-json` allows you to export the changelog contents in JSON format (useful for external automation purposes)"
        ]
    }
    "3.1.0": { ... }
}
```

### Create/Update Release in GitHub

The `github-release` command will create/update a draft Release based on the contents of the
`[Unreleased]` section in your `CHANGELOG.md`:

```sh
Usage: changelogmanager github-release [OPTIONS]

  Creates a new (Draft) release in Github

Options:
  -r, --repository TEXT    Repository  [required]
  -t, --github-token TEXT  Github Token  [required]
  --draft / --release      Update/Create the GitHub Release in either Draft or
                           Release state
  --help                   Show this message and exit.
```

For example:

```sh
% changelogmanager github-release --github-token <PAT> --repository tomtom-international/keepachangelog-manager
```

Will result in something alike:

![Draft Release Example](https://raw.githubusercontent.com/tomtom-international/keepachangelog-manager/master/resources/draft_example.png)

Providing the `--release` flag will update and publish the draft Release.

### Working with multiple CHANGELOG.md files in a single repository

You can create a configuration file with the following schema:

```yml
project:
  components:
  - name: Service Component
    changelog: service/CHANGELOG.md
  - name: Client Interface
    changelog: client/CHANGELOG.md
```

You can provide the `--config` and `--component` options to select a specific
`CHANGELOG.md` file, eg.

```sh
% changelogmanager --config config.yml --component "Client Interface" version
3.7.3
```