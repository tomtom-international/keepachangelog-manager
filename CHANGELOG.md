# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- The `CHANGELOG.json` file will now consist of an array of releases instead of having each release as dict-key

## [3.2.1] - 2022-08-18
### Fixed
- The `release` command is working correct again

## [3.2.0] - 2022-08-18
### Added
- The command `to-json` allows you to export the changelog contents in JSON format (useful for external automation purposes)

## [3.1.0] - 2022-07-20
### Added
- References to the Homepage and Issue Tracker in the package metadata

## [3.0.0] - 2022-05-18
### Removed
- Removed the `--apply` and `--no-apply` flags from the `add`, `release` and `github-release` command.

### Changed
- Improved user interaction for the `add` command

### Added
- The `github-release` command now supports the `--draft/--release` flags to indicate the GitHub release status

## [2.0.0] - 2022-05-18
### Fixed
- Releasing a Changelog containing no previously released version will now result in version `0.0.1` to be released

### Removed
- Removed the `keepachangelog-draft-release`, `keepachangelog-release` and `keepachangelog-validate` actions as these have only been intended for internal use.

## [1.0.3] - 2022-05-17
### Fixed
- The option `--override-version` accepts versions prefixed with v`

## [1.0.2] - 2022-05-17
### Changed
- GitHub Releases and associated tags are now both prefixed with `v` (i.e. `v1.0.0` iso `1.0.0`)

## [1.0.1] - 2022-05-04
### Changed
- Updated README.md to be compatible with PyPi

## [1.0.0] - 2022-05-04
### Added
- Add support Python for older versions (`>=3.7`)
- Command Line Interface allowing users to add and release changes
- Users can now create an empty `CHANGELOG.md` using the `create` command
- Support for GitHub style error messages
- Added `validate` command to verify CHANGELOG.md consistency
- Support for creating (Draft) releases on GitHub using the `github-release` command
- Workflow to update the draft release notes when new changes are pushed to \`main\`

