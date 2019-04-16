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

"""Remote Tensorflow Execution (rtf): gRPC server and clients generators."""

import re
import os
from glob import glob
import pkg_resources
from setuptools import find_packages, setup, Command
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop


class CompileProto(Command):
    """Command to compile the protobuf files to Python."""

    def initialize_options(self):
        """Set default values for options."""
        # pylint: disable=attribute-defined-outside-init
        self._proto_files = ["rtf/proto/rtf.proto"]
        self._proto_include = "rtf/proto/"
        self._proto_out = "rtf/proto/"
        self._pb_re = re.compile(r"^(import.*_pb2) as", re.MULTILINE)

    def finalize_options(self):
        """Post-process options."""

    def run(self):
        """Run the compilation when invoked."""
        import grpc_tools.protoc

        proto_include = pkg_resources.resource_filename("grpc_tools", "_proto")
        for proto in self._proto_files:
            grpc_tools.protoc.main(
                [
                    "grpc_tools.protoc",
                    f"-I{proto_include}",
                    f"-I{self._proto_include}",
                    f"--python_out={self._proto_out}",
                    f"--grpc_python_out={self._proto_out}",
                    proto,
                ]
            )

        for pb_path in glob(os.path.join(self._proto_out, "*_pb2*.py"), recursive=True):
            with open(pb_path, "r+") as fp:  # pylint: disable=invalid-name
                pb2 = fp.read()
                pb2 = self._pb_re.sub(r"from . \1 as", pb2)
                fp.seek(0)
                fp.write(pb2)
                fp.truncate()


class Build(build_py):
    """Custom build_py; executes the protobuf compilation and fix before doing
    the standard stuff."""

    def run(self):
        """Rune the commands."""
        self.run_command("proto")
        super().run()


class Develop(develop):
    """Custom develop; executes the protobuf compilation and fix before doing
    the standard stuff."""

    def run(self):
        """Rune the commands."""
        self.run_command("proto")
        super().run()


if __name__ == "__main__":
    with open("README.md", "r", encoding="utf-8") as FP:
        README = FP.read()

    with open("requirements.txt") as FP:
        REQUIREMENTS = FP.read().splitlines()

    setup(
        cmdclass={"proto": CompileProto, "build_py": Build, "develop": Develop},
        author="Paolo Galeone",
        author_email="nessuno@nerdz.eu",
        description="Remote Tensorflow Execution (rtf): gRPC server and clients generators",
        install_requires=REQUIREMENTS,
        license="Apache License Version 2.0",
        long_description=README,
        long_description_content_type="text/markdown",
        include_package_data=True,
        name="rtf",
        packages=find_packages(),
        setup_requires=["better-setuptools-git-version"],
        tests_require=REQUIREMENTS,
        url="https://github.com/galeone/rtf",
        version_config={
            "version_format": "{tag}.dev{sha}",
            "starting_version": "0.0.1",
        },
    )
