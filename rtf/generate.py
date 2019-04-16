# Copyright 2019 Paolo Galeone <nessuno@nerdz.eu>. All Rights Reserved.
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

"""CLI application to generate rtf clients."""

import os
from argparse import ArgumentParser
from .generators.base import Generator
from .generators.go import Go


def make_generator(lang):
    """Given a taret language, creates the correct Generator object.
    Args:
        lang: the target language as a string.
    Returns:
        generator
    """
    lang = lang.strip().lower()
    generator = None
    if lang == "go":
        generator = Go
    else:
        raise ValueError(f"Language {lang} not supported")

    return generator()


def main():
    """Main, parses CLI, builds and runs the generator."""
    parser = ArgumentParser(
        description="Convert a Python module to a <target language> package"
    )
    parser.add_argument("--dest_dir", default=os.getcwd())
    parser.add_argument("--module", default="tensorflow")
    parser.add_argument("--keep_private", default=False)
    parser.add_argument("--target", default="Go")
    args = parser.parse_args()
    module = Generator.inspect_module(args.module)
    generator = make_generator(args.target)
    return generator(module, args.dest_dir, args.keep_private)


if __name__ == "__main__":
    main()
