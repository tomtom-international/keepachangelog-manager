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

"""Categories of changes"""

from dataclasses import dataclass
from enum import Enum


UNRELEASED_ENTRY = "unreleased"
DEFAULT_CHANGELOG_FILE = "CHANGELOG.md"


class VersionCore(Enum):
    """SemVer Version Cores"""

    MAJOR = 3
    MINOR = 2
    PATCH = 1


@dataclass
class Category:
    """Category for a change"""

    emoji: str
    title: str
    bump: VersionCore


CATEGORIES = {
    "added": Category(emoji="rocket", title="New Features", bump=VersionCore.MINOR),
    "changed": Category(
        emoji="scissors", title="Updated Features", bump=VersionCore.PATCH
    ),
    "deprecated": Category(
        emoji="warning", title="Deprecation", bump=VersionCore.PATCH
    ),
    "removed": Category(emoji="no_entry_sign", title="Removed", bump=VersionCore.MAJOR),
    "fixed": Category(emoji="bug", title="Bug Fixes", bump=VersionCore.PATCH),
    "security": Category(
        emoji="closed_lock_with_key", title="Security Changes", bump=VersionCore.MINOR
    ),
}

TypesOfChange = list(CATEGORIES.keys())
