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

"""Changelog Manager module"""

import sys
from click import ClickException
import llvm_diagnostics as logging
from changelogmanager import cli


def main():
    """Entrypoint"""
    try:
        cli.main(None, None, None, None)
    # Exit gracefully in case an Warning or Information exception was raised
    except (logging.Info, logging.Warning) as exc_info:
        exc_info.report()
        sys.exit(0)

    # Failure
    except logging.Error as exc_info:
        exc_info.report()
        sys.exit(1)

    # Failure
    except ClickException as exc_info:
        exc_info.show()
        sys.exit(1)


if __name__ == "__main__":
    main()
