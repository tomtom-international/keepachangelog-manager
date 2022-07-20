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


from setuptools import find_packages, setup
import re

with open('README.md', encoding='UTF-8') as fh:
    long_description = fh.read()

# Extract first paragraph
description = re.sub(r'^\s*(?:#+[^\n]*\s*)*', r'', long_description, count=1, flags=re.DOTALL|re.MULTILINE)
description = re.sub(r'\n\n.*', r'', description, flags=re.DOTALL|re.MULTILINE)
# Eliminate link annotation
description = re.sub(r'\[([^\]]+)\]', r'\1', description)
# Convert line breaks into spaces
description = description.replace('\n', ' ')

setup(
    name="keepachangelog-manager",
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=(
        "Click>=8,<9",
        "pyyaml>=6,<7",
        "semantic_version>=2.9.0,<3",
        "keepachangelog==2.0.0.dev2",
        "urllib3>=1.25.11,<2",
        "llvm-diagnostics>=3.0.0,<4",
        'inquirer2==1.0.0',
    ),
    setup_requires=(
        "setuptools_scm",
        "setuptools_scm_git_archive",
    ),
    use_scm_version={"relative_to": __file__},
    entry_points={
        "console_scripts": [
            "changelogmanager=changelogmanager.__main__:main",
        ],
    },
    zip_safe=True,
    license='Apache License 2.0',
    license_file='LICENSE.md',
    classifiers=(
      'License :: OSI Approved :: Apache Software License',
    ),
    url='https://github.com/tomtom-international/keepachangelog-manager',
    project_urls={
      'Bug Tracker': 'https://github.com/tomtom-international/keepachangelog-manager/issues',
      'Source Code': 'https://github.com/tomtom-international/keepachangelog-manager',
    },
)
