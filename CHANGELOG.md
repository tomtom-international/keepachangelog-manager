# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2022-05-04
### Added
- Add support Python for older versions (`>=3.7`)
- Command Line Interface allowing users to add and release changes
- Users can now create an empty `CHANGELOG.md` using the `create` command
- Support for GitHub style error messages
- Added `validate` command to verify CHANGELOG.md consistency
- Support for creating (Draft) releases on GitHub using the `github-release` command
- Workflow to update the draft release notes when new changes are pushed to \`main\`
