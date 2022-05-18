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

from typing import Sequence
import pytest

import llvm_diagnostics as logging
from semantic_version import Version

from changelogmanager.changelog_reader import ChangelogReader
from changelogmanager.change_types import CATEGORIES, VersionCore
from changelogmanager.changelog import (
    DEFAULT_CHANGELOG_FILE,
    UNRELEASED_ENTRY,
    Changelog,
)

from .utils import empty_changelog_file, changelog_file, unreleased_changelog_file, get_changelog_expectations


def test_default_changelog(mocker):
    """Verfies that, by default, a `README.md` file is used as input."""

    mocker.patch("keepachangelog.to_dict", return_value={})

    changelog = Changelog()
    assert changelog.get_file_path() == DEFAULT_CHANGELOG_FILE
    assert changelog.get() == {}


def test_changelog_from_file(empty_changelog_file):
    """Verifies custom changelog path"""

    changelog = Changelog(
        file_path=empty_changelog_file,
        changelog=ChangelogReader(file_path=empty_changelog_file).read(),
    )
    assert changelog.get_file_path() == empty_changelog_file
    assert changelog.get() == {}


def test_add_change(empty_changelog_file):
    """Verifies that all compatible categories can be added"""

    changelog = Changelog(
        file_path=empty_changelog_file,
        changelog=ChangelogReader(file_path=empty_changelog_file).read(),
    )

    for change_type in CATEGORIES.keys():
        changelog.add(change_type=change_type, message=f"Validating {change_type}")

    assert changelog.get(UNRELEASED_ENTRY) == {
        "metadata": {"release_date": None, "version": "unreleased"},
        "added": ["Validating added"],
        "removed": ["Validating removed"],
        "deprecated": ["Validating deprecated"],
        "security": ["Validating security"],
        "changed": ["Validating changed"],
        "fixed": ["Validating fixed"],
    }


def test_add_second_change(changelog_file):
    """Verifies that additinal changes are appended."""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )

    changelog.add(change_type="added", message="Test 1")
    changelog.add(change_type="added", message="Test 2")
    assert changelog.get(UNRELEASED_ENTRY) == {
        "metadata": {"release_date": None, "version": "unreleased"},
        "added": ["New feature", "Test 1", "Test 2"],
        "changed": ["Changed another feature"],
    }


def test_exists(changelog_file):
    """Verifies changelog file existance"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    assert changelog.exists() == True

    changelog = Changelog(file_path="does-not-exist.md")
    assert changelog.exists() == False


def test_get_all_versions(changelog_file):
    """Verifies that we can retrieve all versions from a changelog"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    assert changelog.get() == get_changelog_expectations()


def test_get_specific_version(changelog_file):
    """Verifies that we can retrieve all versions from a changelog"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    for version in get_changelog_expectations().keys():
        assert changelog.get(version) == get_changelog_expectations().get(version)


def test_get_invalid_version(changelog_file):
    """Verifies that an Exception is raised when retrieving an invalid version"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )

    with pytest.raises(logging.Warning) as exc_info:
        changelog.get("123.456.789")

    assert (
        str(exc_info.value.message)
        == "Version '123.456.789' not available in the Changelog"
    )


@pytest.mark.freeze_time("2100-12-03 12:34:56")
def test_release(changelog_file):
    """Verifies that unreleased changes get released"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    changelog.release()
    assert changelog.get() == get_changelog_expectations(released=True)

@pytest.mark.freeze_time("2100-12-03 12:34:56")
def test_initial_release(unreleased_changelog_file):
    """Verifies that the initial unreleasd version can be released"""

    changelog = Changelog(
        file_path=unreleased_changelog_file,
        changelog=ChangelogReader(file_path=unreleased_changelog_file).read()
    )

    changelog.release()
    assert changelog.get() == get_changelog_expectations(released=True, initial=True)

@pytest.mark.freeze_time("2100-12-03 12:34:56")
def test_release_override_version(changelog_file):
    """Verifies that unreleased changes get released with specified version"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    changelog.release(override_version="1.1.0")
    assert changelog.get() == get_changelog_expectations(released=True)

@pytest.mark.freeze_time("2100-12-03 12:34:56")
def test_release_override_prefixed_version(changelog_file):
    """Verifies that unreleased changes get released with specified version"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    changelog.release(override_version="v1.1.0")
    assert changelog.get() == get_changelog_expectations(released=True)

def test_release_override_invalid_version(changelog_file):
    """Verifies that an Exception is raised when an invalid version is attempted to be released"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    with pytest.raises(logging.Error) as exc_info:
        changelog.release(override_version="a.b.c")

    assert str(exc_info.value.message) == "Version 'a.b.c' is not SemVer compliant"


def test_release_override_duplicate_version(changelog_file):
    """Verifies that an Exception is raised when attempting to release an already released version"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    with pytest.raises(logging.Error) as exc_info:
        changelog.release(override_version="1.0.0")

    assert (
        str(exc_info.value.message) == "Unable release already released version '1.0.0'"
    )


def test_release_override_older_version(changelog_file):
    """Verifies that and Exception is raised when attempting to release and older version"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    with pytest.raises(logging.Error) as exc_info:
        changelog.release(override_version="0.0.1")

    assert (
        str(exc_info.value.message)
        == "Unable release versions older than last release '1.0.0'"
    )


def test_version(changelog_file):
    """Verifies that the last release version is returned"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    assert changelog.version() == Version("1.0.0")


def test_version_no_release_versions(empty_changelog_file):
    """Verifies that an Exception is raised when there are no released versions"""

    changelog = Changelog(
        file_path=empty_changelog_file,
        changelog=ChangelogReader(file_path=empty_changelog_file).read(),
    )

    with pytest.raises(logging.Warning) as exc_info:
        changelog.version()

    assert str(exc_info.value.message) == "No versions available"


def test_version_only_unreleased(empty_changelog_file):
    """Verifies that an Exception is raised when there are no released versions"""

    changelog = Changelog(
        file_path=empty_changelog_file,
        changelog=ChangelogReader(file_path=empty_changelog_file).read(),
    )
    changelog.add("added", "Test")

    with pytest.raises(logging.Warning) as exc_info:
        changelog.version()

    assert str(exc_info.value.message) == "Only an Unreleased version is available"


def test_previous_version(changelog_file):
    """Verifies that the previous released version is returned"""

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    assert changelog.previous_version() == Version("0.9.4")


def test_previous_version_no_release_versions(empty_changelog_file):
    """Verifies that an Exception is raised when there are no released versions"""

    changelog = Changelog(
        file_path=empty_changelog_file,
        changelog=ChangelogReader(file_path=empty_changelog_file).read(),
    )

    with pytest.raises(logging.Warning) as exc_info:
        changelog.previous_version()

    assert str(exc_info.value.message) == "No previous versions available"


def test_previous_version_only_unreleased(empty_changelog_file):
    """Verifies that an Exception is raised when there are no released versions"""

    changelog = Changelog(
        file_path=empty_changelog_file,
        changelog=ChangelogReader(file_path=empty_changelog_file).read(),
    )
    changelog.add("added", "Test")

    with pytest.raises(logging.Warning) as exc_info:
        changelog.previous_version()

    assert str(exc_info.value.message) == "No previous versions available"


def test_suggest_future_version(changelog_file):
    """Verifies that the next version is returned"""

    for change_type, config in CATEGORIES.items():
        expected_version = Version("1.1.1")

        if config.bump == VersionCore.MAJOR:
            expected_version = Version("2.0.0")

        if config.bump == VersionCore.MINOR:
            expected_version = Version("1.2.0")

        changelog = Changelog(
            file_path=changelog_file,
            changelog=ChangelogReader(file_path=changelog_file).read(),
        )
        changelog.release()  # Ensure there are no unreleased changes!

        changelog.add(change_type, "Some message")

        assert changelog.suggest_future_version() == expected_version


def test_suggest_future_version_cascade(changelog_file):
    """Verifies that the next version is returned"""

    _patch_types = [
        key for key, value in CATEGORIES.items() if value.bump == VersionCore.PATCH
    ]
    _minor_types = [
        key for key, value in CATEGORIES.items() if value.bump == VersionCore.MINOR
    ]
    _major_types = [
        key for key, value in CATEGORIES.items() if value.bump == VersionCore.MAJOR
    ]

    changelog = Changelog(
        file_path=changelog_file,
        changelog=ChangelogReader(file_path=changelog_file).read(),
    )
    changelog.release()  # Ensure there are no unreleased changes!

    def validate_version(version: str, data: Sequence):
        for change_type in data:
            expected_version = Version(version)
            changelog.add(change_type, "")
            assert changelog.suggest_future_version() == expected_version

    validate_version("1.1.1", _patch_types)
    validate_version("1.2.0", _minor_types)
    validate_version("2.0.0", _major_types)
