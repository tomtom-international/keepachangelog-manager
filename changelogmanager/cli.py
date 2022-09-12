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

""" Changelog Manager """

from typing import Mapping, Optional

from click import group, option, pass_context, Choice, File
import inquirer2.prompt
import llvm_diagnostics as logging

from changelogmanager.change_types import TypesOfChange
from changelogmanager.changelog import Changelog
from changelogmanager.changelog_reader import ChangelogReader
from changelogmanager.config import get_component_from_config
from changelogmanager.github import GitHub

VERSION_REFERENCES = ["previous", "current", "future"]


@group()
@option("--config", default=None, help="Configuration file")
@option("--component", default="default", help="Name of the component to update")
@option(
    "-f",
    "--error-format",
    type=Choice(["llvm", "github"]),
    default="llvm",
    help="Type of formatting to apply to error messages",
)
@option("--input-file", default="CHANGELOG.md", help="Changelog file to work with")
@pass_context
def main(
    ctx: Mapping,
    config: Optional[File],
    component: str,
    error_format: bool,
    input_file: str,
) -> int:
    """(Keep a) Changelog Manager"""

    # Pass changelog configuration to sub-commands
    ctx.ensure_object(dict)

    logging.config(
        logging.formatters.Llvm()
        if error_format == "llvm"
        else logging.formatters.GitHub()
    )

    if config:
        component = get_component_from_config(config=config, component=component)
        changelog = ChangelogReader(file_path=component.get("changelog")).read()
        ctx.obj["changelog"] = Changelog(
            file_path=component.get("changelog"), changelog=changelog
        )
    else:
        changelog = ChangelogReader(file_path=input_file).read()
        ctx.obj["changelog"] = Changelog(file_path=input_file, changelog=changelog)


@main.command()
@pass_context
def create(ctx: Mapping) -> None:
    """Command to create a new (empty) CHANGELOG.md"""
    changelog = ctx.obj["changelog"]

    if changelog.exists():
        raise logging.Info(
            file_path=changelog.get_file_path(), message="File already exists"
        )

    changelog.write_to_file()


@main.command()
@option(
    "-r",
    "--reference",
    type=Choice(VERSION_REFERENCES),
    default="current",
    help="Which version to retrieve",
)
@pass_context
def version(ctx: Mapping, reference: str) -> None:
    """Command to retrieve versions from a CHANGELOG.md"""

    changelog = ctx.obj["changelog"]

    if reference == "current":
        print(changelog.version())

    if reference == "previous":
        print(changelog.previous_version())

    if reference == "future":
        print(changelog.suggest_future_version())


@main.command()
@pass_context
def validate(_: Mapping) -> None:
    """Command to validate the CHANGELOG.md for inconsistencies"""


@main.command()
@option(
    "--override-version",
    default=None,
    help="Version to release, defaults to auto-resolve",
)
@pass_context
def release(ctx: Mapping, override_version: Optional[str]) -> None:
    """Release changes added to [Unreleased] block"""

    changelog = ctx.obj["changelog"]
    changelog.release(override_version)

    changelog.write_to_file()


@main.command()
@option(
    "--file-name",
    default="CHANGELOG.json",
    help="Filename of the JSON output",
)
@pass_context
def to_json(ctx: Mapping, file_name: str) -> None:
    """Exports the contents of the CHANGELOG.md to a JSON file"""
    changelog = ctx.obj["changelog"]
    changelog.write_to_json(file=file_name)


@main.command()
@option(
    "-t",
    "--change-type",
    type=Choice(TypesOfChange),
    help="Type of the change",
)
@option(
    "-m",
    "--message",
    help="Changelog entry",
)
@pass_context
def add(ctx: Mapping, change_type: str, message: str) -> None:
    """Command to add a new message to the CHANGELOG.md"""
    apply = True
    changelog_entry = {}

    prompts = []
    if not change_type:
        prompts.append(
            {
                "type": "list",
                "name": "change_type",
                "message": "Specify the type of your change",
                "choices": TypesOfChange,
            }
        )

    if not message:
        prompts.append(
            {
                "type": "input",
                "name": "message",
                "message": "Message of the changelog entry to add",
            }
        )

    if len(prompts) > 0:
        changelog_entry = inquirer2.prompt.prompt(prompts)
        apply = inquirer2.prompt.prompt(
            [
                {
                    "type": "confirm",
                    "name": "confirmation",
                    "message": "Apply changes to your CHANGELOG.md",
                    "default": True,
                }
            ]
        ).get("confirmation")

    changelog_entry.setdefault("change_type", change_type)
    changelog_entry.setdefault("message", message)

    changelog = ctx.obj["changelog"]
    changelog.add(**changelog_entry)

    if apply:
        changelog.write_to_file()


@main.command()
@option("-r", "--repository", required=True, help="Repository")
@option("-t", "--github-token", required=True, help="Github Token")
@option(
    "--draft/--release",
    default=True,
    help="Update/Create the GitHub Release in either Draft or Release state",
)
@pass_context
def github_release(ctx, repository: str, github_token: str, draft: bool) -> None:
    """Deletes all releases marked as 'Draft' on GitHub and creates a new 'Draft'-release"""

    changelog = ctx.obj["changelog"]

    github = GitHub(repository=repository, token=github_token)
    github.delete_draft_releases()
    github.create_release(changelog=changelog, draft=draft)
