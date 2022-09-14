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

"""Changelog"""

import json
import os

from collections import OrderedDict
from datetime import datetime
from typing import Mapping, Optional

import keepachangelog
import llvm_diagnostics as logging
from semantic_version import Version

from changelogmanager.change_types import (
    CATEGORIES,
    DEFAULT_CHANGELOG_FILE,
    UNRELEASED_ENTRY,
    VersionCore,
)


INITIAL_VERSION = Version("0.0.1")


class Changelog:
    """Changelog"""

    def __init__(
        self, file_path: str = DEFAULT_CHANGELOG_FILE, changelog: Optional[str] = None
    ):
        """Constructor"""
        self.__changelog_file_path = file_path
        self.__changelog = changelog if changelog else {}

    def get_file_path(self):
        """Returns the path to the changelog file"""
        return self.__changelog_file_path

    def add(self, change_type: str, message: str) -> None:
        """Adds a new message to the specified change identifier in the Changelog"""

        changelog = OrderedDict(self.__changelog.copy())

        changelog.setdefault(
            UNRELEASED_ENTRY,
            {
                "metadata": {
                    "version": UNRELEASED_ENTRY,
                    "release_date": None,
                }
            },
        )
        changelog[UNRELEASED_ENTRY].setdefault(change_type, [])
        changelog[UNRELEASED_ENTRY][change_type].append(message)

        # Ensure that the new entry is on top
        changelog.move_to_end(UNRELEASED_ENTRY, last=False)

        self.__changelog = changelog.copy()

    def exists(self):
        """Verifies if the Changelog file exists"""
        return os.path.isfile(self.__changelog_file_path)

    def get(self, version: Optional[str] = None) -> Mapping:
        """Returns the specified version"""

        if not version:
            return self.__changelog

        if str(version) not in self.__changelog:
            raise logging.Warning(
                file_path=self.get_file_path(),
                message=f"Version '{version}' not available in the Changelog",
            )

        return self.__changelog[str(version)]

    def release(self, override_version: Optional[str] = None) -> None:
        """Releases the Unreleased version"""

        if UNRELEASED_ENTRY not in self.__changelog:
            raise logging.Error(
                file_path=self.get_file_path(),
                message="Unable to release without [Unreleased] section",
            )

        # Strip `v` from the provided version tag
        if override_version and override_version.startswith("v"):
            override_version = override_version[1:]

        try:
            _version = (
                Version(override_version)
                if override_version
                else self.suggest_future_version()
            )
        except ValueError as exc_info:
            _message = f"Version '{override_version}' is not SemVer compliant"
            raise logging.Error(message=_message) from exc_info

        if str(_version) in self.get().keys():
            raise logging.Error(
                file_path=self.get_file_path(),
                message=f"Unable to release an already released version '{_version}'",
            )

        if not self.__has_only_unreleased_version() and _version < self.version():
            raise logging.Error(
                file_path=self.get_file_path(),
                message=f"Unable to release a version older than the last release '{self.version()}'",
            )

        def update_unreleased_version(changelog: Mapping, new_version: Version):
            changelog = OrderedDict(changelog.copy())
            changelog[str(new_version)] = changelog.pop(UNRELEASED_ENTRY)
            changelog[str(new_version)]["metadata"] = {
                "version": str(new_version),
                "release_date": datetime.now().strftime("%Y-%m-%d"),
                "semantic_version": {
                    "buildmetadata": None,
                    "major": new_version.major,
                    "minor": new_version.minor,
                    "patch": new_version.patch,
                    "prerelease": None,
                },
            }

            # Ensure that the new entry is on top
            changelog.move_to_end(str(new_version), last=False)

            return changelog

        self.__changelog = update_unreleased_version(self.__changelog, _version)

    def version(self) -> Version:
        """Returns the last released version"""
        if len(self.__changelog) == 0:
            raise logging.Warning(
                file_path=self.get_file_path(), message="No versions available"
            )

        if UNRELEASED_ENTRY in self.__changelog:
            if len(self.__changelog) <= 1:
                raise logging.Warning(
                    file_path=self.get_file_path(),
                    message="Only an Unreleased version is available",
                )

            return Version(list(self.__changelog)[1])

        return Version(list(self.__changelog)[0])

    def previous_version(self) -> Version:
        """Returns the previously released version"""

        if len(self.__changelog) <= 1:
            raise logging.Warning(
                file_path=self.get_file_path(), message="No previous versions available"
            )

        if UNRELEASED_ENTRY in self.__changelog:
            if len(self.__changelog) <= 2:
                raise logging.Warning(
                    file_path=self.get_file_path(),
                    message="No previous versions available",
                )

            return Version(list(self.__changelog)[2])

        return Version(list(self.__changelog)[1])

    def suggest_future_version(self) -> Version:
        """Suggests a future version based on the [Unreleased]-changes"""

        if self.__has_only_unreleased_version():
            return INITIAL_VERSION

        def determine_version(unreleased: Mapping, prev_version: Version):
            bump_type = VersionCore.PATCH
            for identifier, category in CATEGORIES.items():
                if identifier in unreleased and category.bump.value > bump_type.value:
                    bump_type = category.bump

            if bump_type == VersionCore.MAJOR:
                return prev_version.next_major()

            if bump_type == VersionCore.MINOR:
                return prev_version.next_minor()

            return prev_version.next_patch()

        return determine_version(self.get(UNRELEASED_ENTRY), self.version())

    def write_to_json(self, file: str, version: Optional[str] = None) -> None:
        """Stores the Changelog file in JSON format"""

        content = self.get(version=version)
        json_data = [value for _, value in content.items()]

        with open(file, "w", encoding="UTF-8") as file_handle:
            file_handle.write(json.dumps(json_data, indent=4))

    def write_to_file(self) -> None:
        """Updates CHANGELOG.md based on the Keep a Changelog standard"""

        with open(self.__changelog_file_path, "w", encoding="UTF-8") as file_handle:
            file_handle.write(self.__str__())

    def __has_only_unreleased_version(self):
        """Returns True when the changelog only contains an Unreleased version"""
        return UNRELEASED_ENTRY in self.__changelog and len(self.__changelog) == 1

    def __str__(self):
        """String representation"""

        return keepachangelog.from_dict(self.__changelog)
