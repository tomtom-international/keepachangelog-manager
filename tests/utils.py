# Copyright (c) 2022 - 2022 TomTom N.V.
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

from collections import OrderedDict
import pytest


@pytest.fixture(scope="session")
def empty_changelog_file(tmpdir_factory):
    """Initial Changelog file"""
    changelog = tmpdir_factory.mktemp("data").join("CHANGELOG.md")
    changelog.write_text("# Changelog", encoding="UTF-8")
    return changelog


@pytest.fixture(scope="session")
def unreleased_changelog_file(tmpdir_factory):
    """Changelog file containing only an unreleased version"""
    changelog = tmpdir_factory.mktemp("data").join("CHANGELOG.md")
    changelog.write_text(
        """\
# Changelog

## [Unreleased]
### Added
- New feature

### Changed
- Changed another feature
""",
        encoding="UTF-8",
    )
    return changelog

@pytest.fixture(scope="session")
def changelog_file(tmpdir_factory):
    """Changelog file containing both released and unreleased versions"""
    changelog = tmpdir_factory.mktemp("data").join("CHANGELOG.md")
    changelog.write_text(
        """\
# Changelog

## [Unreleased]
### Added
- New feature

### Changed
- Changed another feature

## [1.0.0] - 2022-03-14
### Removed
- Removed deprecated API call

### Fixed
- Fixed some bug

## [0.9.4] - 2022-03-13
### Deprecated
- Deprecated public API call
""",
        encoding="UTF-8",
    )
    return changelog


@pytest.fixture(scope="session")
def released_only_changelog_file(tmpdir_factory):
    """Changelog file containing released versions"""
    changelog = tmpdir_factory.mktemp("data").join("CHANGELOG.md")
    changelog.write_text(
        """\
# Changelog

## [1.0.0] - 2022-03-14
### Removed
- Removed deprecated API call

### Fixed
- Fixed some bug

## [0.9.4] - 2022-03-13
### Deprecated
- Deprecated public API call
""",
        encoding="UTF-8",
    )
    return changelog


def get_changelog_expectations(released: bool = False, initial = False):
    """Check expectations"""

    initial_version = {}

    if released:
        if initial:
            initial_version = {
                "0.0.1": {
                    "metadata": {
                        "version": "0.0.1",
                        "release_date": "2100-12-03",
                        "semantic_version": {
                            "major": 0,
                            "minor": 0,
                            "patch": 1,
                            "prerelease": None,
                            "buildmetadata": None,
                        },
                    },
                    "added": ["New feature"],
                    "changed": ["Changed another feature"],
                }
            }
        else:
            initial_version = {
                "1.1.0": {
                    "metadata": {
                        "version": "1.1.0",
                        "release_date": "2100-12-03",
                        "semantic_version": {
                            "major": 1,
                            "minor": 1,
                            "patch": 0,
                            "prerelease": None,
                            "buildmetadata": None,
                        },
                    },
                    "added": ["New feature"],
                    "changed": ["Changed another feature"],
                }
            }
    else:
        initial_version = {
            "unreleased": {
                "metadata": {"version": "unreleased", "release_date": None},
                "added": ["New feature"],
                "changed": ["Changed another feature"],
            }
        }

    if initial:
        return OrderedDict(
            **initial_version
        )

    return OrderedDict(
        {
            **initial_version,
            "1.0.0": {
                "metadata": {
                    "version": "1.0.0",
                    "release_date": "2022-03-14",
                    "semantic_version": {
                        "major": 1,
                        "minor": 0,
                        "patch": 0,
                        "prerelease": None,
                        "buildmetadata": None,
                    },
                },
                "removed": ["Removed deprecated API call"],
                "fixed": ["Fixed some bug"],
            },
            "0.9.4": {
                "metadata": {
                    "version": "0.9.4",
                    "release_date": "2022-03-13",
                    "semantic_version": {
                        "major": 0,
                        "minor": 9,
                        "patch": 4,
                        "prerelease": None,
                        "buildmetadata": None,
                    },
                },
                "deprecated": ["Deprecated public API call"],
            },
        }
    )
