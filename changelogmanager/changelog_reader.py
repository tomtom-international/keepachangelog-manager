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

"""Changelog Reader"""

import datetime
import os
import re

from typing import Mapping

import keepachangelog
import llvm_diagnostics as logging
from semantic_version import Version

from changelogmanager.change_types import (
    DEFAULT_CHANGELOG_FILE,
    TypesOfChange,
    UNRELEASED_ENTRY,
)


class ChangelogReader:
    """Changelog Reader"""

    def __init__(
        self,
        file_path: str = DEFAULT_CHANGELOG_FILE,
    ):
        """Constructor"""

        self.__file_path = file_path

    def read(self):
        """Reads the CHANGELOG.md file and checks for validity"""

        if not os.path.isfile(self.__file_path):
            return {}

        errors = self.validate_layout()

        if errors:
            raise logging.Error(
                file_path=self.__file_path,
                message=f"{errors} errors detected in the layout",
            )

        changelog = keepachangelog.to_dict(self.__file_path, show_unreleased=True)

        self.validate_contents(changelog)

        return changelog

    def __validate_change_heading(self, line_number, line, depth, content):
        """Check if acceptable keywords are present"""

        accepted_types = [change_type.title() for change_type in TypesOfChange]

        if content not in accepted_types:
            friendly_types = ", ".join(accepted_types)

            yield logging.Error(
                file_path=self.__file_path,
                line=line,
                line_number=logging.Range(start=line_number),
                column_number=logging.Range(start=depth + 2, range=len(content)),
                message=(
                    f"Incompatible change type provided, MUST be one of: {friendly_types}"
                ),
            )

    def __validate_version_heading(self, line_number, line, depth, content):
        # Check if version tag ([x.y.z]) is present
        match = re.compile(r"\[(.*)\](.*)").match(content)

        if not match:
            yield logging.Error(
                file_path=self.__file_path,
                line=line,
                line_number=logging.Range(start=line_number),
                column_number=logging.Range(start=depth + 2, range=len(content)),
                message="Missing version tag",
            )
            return

        version = match.group(1)

        if version == UNRELEASED_ENTRY.title():
            return

        # Verify that the version is valid SemVer syntax
        try:
            version = Version(version)
        except ValueError:
            yield logging.Error(
                file_path=self.__file_path,
                line=line,
                line_number=logging.Range(start=line_number),
                column_number=logging.Range(
                    start=line.find("[") + 2, range=len(version)
                ),
                message=f"Incompatible version '{version}' specified, MUST be SemVer compliant",
            )

        # Validate the availability of meta data (' - ')
        match = re.compile(r" - (.*)").match(match.group(2))

        if not match:
            yield logging.Error(
                file_path=self.__file_path,
                line=line,
                line_number=logging.Range(start=line_number),
                column_number=logging.Range(
                    start=line.find("]") + 3,
                ),
                message=f"Missing metadata ('-') for release version '{version}'",
            )
            return

        release_date = match.group(1)

        # Verify that a date is present ('####-##-##')
        match = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}").match(release_date)

        if not match:
            yield logging.Error(
                file_path=self.__file_path,
                line=line,
                line_number=logging.Range(start=line_number),
                column_number=logging.Range(
                    start=line.find(" - ") + 4,
                ),
                message=(
                    f"Incompatible release date for release version '{version}', MUST be 'yyyy-mm-dd'"  # pylint: disable=C0301
                ),
            )
            return

        # Verify that the date is according to ISO standard
        try:
            datetime.datetime.strptime(release_date, "%Y-%m-%d")
        except ValueError:
            yield logging.Error(
                file_path=self.__file_path,
                line=line,
                line_number=logging.Range(start=line_number),
                column_number=logging.Range(
                    start=line.find(" - ") + 4, range=len(release_date)
                ),
                message=(
                    f"Incompatible release date for release version '{version}', MUST be 'yyyy-mm-dd'"  # pylint: disable=C0301
                ),
            )

    def __validate_heading(self, line_number, line):
        match = re.compile(r"^(#{1,6}) (.*)").match(line)

        if not match:
            # Not a header, no validation required.
            return

        depth = len(match.group(1))
        content = match.group(2)

        # KeepaChangelog only allows for three levels of depth
        if depth > 3:
            yield logging.Error(
                file_path=self.__file_path,
                line=line,
                line_number=logging.Range(start=line_number),
                column_number=logging.Range(start=line.find("#") + 4, range=depth - 3),
                message="Heading depth is too high, MUST be less or equal to 3",
            )
            return

        # Validate the format: ## [1.2.3] - 2022-12-31
        if depth == 2:
            yield from self.__validate_version_heading(
                line_number=line_number, line=line, depth=depth, content=content
            )

        # Validate the format: ### Added
        if depth == 3:
            yield from self.__validate_change_heading(
                line_number=line_number, line=line, depth=depth, content=content
            )

    def __validate_entry(self, line_number, line):
        match = re.compile(r"[-+*] (.*)").match(line)

        if not match:
            # Not an entry, no validation required.
            return

        entry = match.group(1)

        rules = [
            {
                "pattern": r"^(#{1,6}) .*",
                "error": "Block quotes are not permitted in changelog entries",
            },
            {
                "pattern": r"^([0-9]+\.) .*",
                "error": "Numbered lists are not permitted in changelog entries",
            },
            {
                "pattern": r"^([+*-]) .*",
                "error": "Sub-lists are not permitted in changelog entries",
            },
            {
                "pattern": r"^([>]+) .*",
                "error": "Block quotes are not permitted in changelog entries",
            },
        ]

        for rule in rules:
            match = re.compile(rule["pattern"]).match(entry)
            if match:
                yield logging.Error(
                    file_path=self.__file_path,
                    line=line,
                    line_number=logging.Range(start=line_number),
                    column_number=logging.Range(start=3, range=len(match.group(1))),
                    message=rule["error"],
                )

    def validate_layout(self):
        """Validates the changelog file according to KeepAChangelog conventions"""

        line_number = 1
        errors = []
        with open(self.__file_path, "r", encoding="UTF-8") as file_handle:
            for line in file_handle:
                errors.extend(list(self.__validate_heading(line_number, line)))
                errors.extend(list(self.__validate_entry(line_number, line)))
                line_number += 1

        for error in errors:
            error.report()

        return len(errors)

    def validate_contents(self, changelog: Mapping):
        """Validates the contents of the CHANGELOG.md file"""

        is_first_entry = True
        prev_version = None
        message = logging.Warning(
            file_path=self.__file_path,
            message="Unknown warning",
        )

        for version in changelog.keys():
            if version == UNRELEASED_ENTRY:
                if not is_first_entry:
                    message.message = (
                        "Unreleased version should be on top of the CHANGELOG.md file"
                    )
                    message.report()
            else:
                new_version = Version(version)
                if prev_version and prev_version <= new_version:
                    message.message = f"Versions are incorrectly ordered: {prev_version} -> {new_version}"  # pylint: disable=C0301
                    message.report()

                prev_version = new_version

            is_first_entry = False
