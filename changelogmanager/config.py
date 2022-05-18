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

"""Configuration Management"""

from typing import Mapping, Sequence

import yaml
import llvm_diagnostics as logging


def validate_configuration(file_path: str, config: Mapping):
    """Verifies if the provided configuration file is accoriding to expectations"""
    if not config.get("project") or not config["project"].get("components"):
        raise logging.Error(
            file_path=file_path, message="Incorrect Project configuration format!"
        )

    for component in config["project"]["components"]:
        if not component.get("name") or not component.get("changelog"):
            raise logging.Error(
                file_path=file_path, message="Incorrect Component configuration format!"
            )


def get_component_from_config(config: str, component: str):
    """Retrieves a specific component from the configuration file"""
    with open(config, "r", encoding="UTF-8") as file_handle:
        configuration = yaml.safe_load(file_handle)

    validate_configuration(config, configuration)

    project = configuration.get("project")

    def filter_component(components: Sequence, name: str) -> Mapping:
        for component in components:
            if component.get("name") == name:
                return component

        raise logging.Error(file_path=config, message=f"Unknown component name: {name}")

    return filter_component(project.get("components"), component)
