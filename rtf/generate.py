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
import sys
from argparse import ArgumentParser

from .generators.go import Go
from .generators.python import Python


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
    elif lang == "python":
        generator = Python
    else:
        raise ValueError(f"Language {lang} not supported")

    return generator()


def main():
    """Main, parses CLI, builds and runs the generator."""
    parser = ArgumentParser(
        description="Convert the TensorFlow Python API to a gRPC client for the <target language>"
    )
    parser.add_argument(
        "--dest_dir", default=os.getcwd(), help="where to put the generated client"
    )
    parser.add_argument(
        "--target", default="Go", help="the target language", choices=["Go", "Python"]
    )
    parser.add_argument(
        "--tensorflow_version",
        default=2.1,
        help="The tensorflow version to use",
        choices=["2.1"],
    )
    args = parser.parse_args()
    return make_generator(args.target)(args.dest_dir, args.tensorflow_version)


if __name__ == "__main__":
    sys.exit(main())
