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

"""GitHub"""

import json
import os

from enum import Enum
from textwrap import dedent
from typing import Mapping, Optional, Sequence
from urllib.error import URLError
from urllib.request import Request, urlopen

import llvm_diagnostics as logging
from changelogmanager.change_types import CATEGORIES, UNRELEASED_ENTRY
from changelogmanager.changelog import Changelog

RELEASES_CHUNK_SIZE = 100


class HttpMethods(Enum):
    """Http Methods"""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


class GitHub:
    """GitHub"""

    def __init__(self, repository: str, token: str):
        """Constructor"""

        self.__repository = repository
        self.__headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
        }

    def __github_request(
        self, api: str, method: HttpMethods, data: Optional[Mapping] = None
    ):
        url = f"https://api.github.com/repos/{self.__repository}/{api}"

        request = Request(
            method=method.value,
            url=url,
            data=json.dumps(data).encode(),
            headers=self.__headers,
        )

        response = []
        try:
            with urlopen(request) as resp:  # nosec
                response = resp.read().decode()

            if not response:
                return None

            return json.loads(response)
        except URLError as url_error:
            raise logging.Error(
                message=dedent(
                    f"""
                Failure during GitHub request:
                  URL:    {url}
                  Method: {method.value}
                  Data:   {data}"""
                )
            ) from url_error

    def get_releases(self) -> Sequence:
        """Retrieves available releases"""
        releases = []
        index = 1

        while True:
            data = self.__github_request(
                method=HttpMethods.GET,
                api="releases",
                data={
                    "per_page": RELEASES_CHUNK_SIZE,
                    "page": index,
                },
            )

            releases.extend(data)

            if len(data) < RELEASES_CHUNK_SIZE:
                break

            index = index + 1

        return releases

    def delete_draft_releases(self) -> None:
        """Deletes all releases marked as 'Draft'"""

        releases = self.get_releases()

        for rel in releases:
            if rel.get("draft"):
                self.delete_release(rel)

    def delete_release(self, release: Mapping) -> None:
        """Deletes a release"""

        self.__github_request(
            method=HttpMethods.DELETE, api=f"releases/{release.get('id')}"
        )

    def create_release(self, changelog: Changelog, draft: bool):
        """Creates a new release on GitHub"""

        def generate_release_notes(release: Mapping):
            body = "## What's changed" + os.linesep + os.linesep
            body += os.linesep.join(
                [
                    f"### :{category.emoji}: {category.title}"
                    + os.linesep
                    + os.linesep.join(
                        [f"* {message}" for message in release[identifier]]
                    )
                    for identifier, category in CATEGORIES.items()
                    if identifier in release
                ]
            )
            return body

        version = f"v{changelog.suggest_future_version()}"
        self.__github_request(
            method=HttpMethods.POST,
            api="releases",
            data={
                "tag_name": version,
                "name": f"Release {version}",
                "draft": draft,
                "body": generate_release_notes(changelog.get(UNRELEASED_ENTRY)),
            },
        )
