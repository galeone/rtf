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
"""Generator for the Python programming language."""

import os
import pathlib

import black

from ..proto.lib import api_objects_pb2 as tf_api_objects
from .base import Generator, Parser


class Python(Parser, Generator):
    """Parser and Generator from and to the Python programming language."""

    HEADER = (
        r'"""Remote {package} - machine generated."""'
        "\n"
        "# This file is machine generated. Do NOT edit unless you\n"
        "# REALLY know what are you doing.\n\n"
        "# TODO: import grpc client\n"
        "\n\n"
    )

    @staticmethod
    def build_signature(argspec):
        spec = Parser._parse_argspec(argspec)
        dp_len = len(spec["defaults"]) if spec["defaults"] else 0
        args_count = len(spec["args"])
        args = {}
        for i in range(args_count - dp_len, args_count):
            args[str(spec["args"][i])] = spec["defaults"][i - args_count]
        signature = ""
        if args_count - dp_len > 0:
            signature = ",".join(spec["args"][: args_count - dp_len])
            if args:
                signature += ","
        # The default parameteres are hard to disambiguate.
        # eg. default='[None', 'categorical_hinge'] must be parsed in two different ways.
        # 'None' -> must become the symbol None
        # 'categorial_hinge' -> must remain the string 'categorical_hinge'.
        # literal_eval just removes the string, making the defaults None, categorical_hinge.
        #
        # Thus, we have to handle these different scenarios.

        defaults = ""
        first_append = True
        for param, default in args.items():
            # Use a stupid heuristic: if the default parameter starts with an upper case
            # character, it is likely to be a language symbol (e.g None), or a class
            # static member (Variable.SOMETHING).
            # If the parameter value contains the symbols "(", ")" then it might be a
            # tuple, or a function call, and it should remain as it is.
            # Otherwise, we treat this as a string.
            if not first_append:
                defaults += ", "

            defaults += f"{param}="
            if default[0].isupper() or "(" in default or ")" in default:
                defaults += f"{default}"
            else:
                defaults += f"'{default}'"
            first_append = False

        return signature + defaults

    def _write_module_members(self, fp, members):
        if not members:
            return

        members_string_list = "[{}]".format(",".join(f"'{m.name}'" for m in members))

        # First write all the getters
        fp.write("\ndef __getattr__(name):\n")
        fp.write(
            "\tif name in {members_list}:\n"
            "\t\traise ValueError('implement grcp getter call')\n".format(
                members_list=members_string_list
            )
        )

        # Now write all the setters
        fp.write("\ndef __setattr__(name, value):\n")
        fp.write(
            "\tif name in {members_list}:\n"
            "\t\traise ValueError('implement grcp setter call')\n".format(
                members_list=members_string_list
            )
        )

    def _write_module_member_methods(self, fp, member_methods):
        if not member_methods:
            return

        for member_method in member_methods:
            # optional: name, path, argspec
            if member_method.HasField("name") and member_method.HasField("argspec"):
                fp.write(
                    "\ndef {func_name}({func_signature}):\n"
                    "\traise ValueError('implement member method grpc call')\n".format(
                        func_name=member_method.name,
                        func_signature=self.build_signature(member_method.argspec),
                    )
                )

    def _write_class_member_methods(self, fp, member_methods):
        if not member_methods:
            return
        for member_method in member_methods:
            # optional: name, path, argspec
            if member_method.HasField("name") and member_method.HasField("argspec"):
                fp.write(
                    "\n\tdef {func_name}({func_signature}):\n"
                    "\t\traise ValueError('implement member method grpc call')\n".format(
                        func_name=member_method.name,
                        func_signature=self.build_signature(member_method.argspec),
                    )
                )

    def _write_class_members(self, fp, members):
        if not members:
            return

        members_string_list = "[{}]".format(",".join(f"'{m.name}'" for m in members))

        # First write all the getters
        fp.write("\n\tdef __getattr__(self, name):\n")
        fp.write(
            "\t\tif name in {members_list}:\n"
            "\t\t\traise ValueError('implement grcp getter call')\n".format(
                members_list=members_string_list
            )
        )

        # Now write all the setters
        fp.write("\n\tdef __setattr__(self, name, value):\n")
        fp.write(
            "\t\tif name in {members_list}:\n"
            "\t\t\traise ValueError('implement grcp setter call')\n".format(
                members_list=members_string_list
            )
        )

    def _write_class(self, fp, name, tf_class):
        fp.write(f"class {name}:\n\n" f"\t#TODO: class attribute grpc client?\n\n")
        self._write_class_members(fp, tf_class.member)
        self._write_class_member_methods(fp, tf_class.member_method)

    def _write_module(self, fp, tf_module):
        self._write_module_members(fp, tf_module.member)
        self._write_module_member_methods(fp, tf_module.member_method)

    def convert(self, dest_dir, golden_proto_dict):
        for path, tf_api_object in golden_proto_dict.items():
            file_path = os.path.join(
                dest_dir, os.path.join(path.replace(".", os.path.sep))
            )

            if tf_api_object.HasField("tf_module"):
                file_basedir = file_path
                if not os.path.exists(file_basedir):
                    os.makedirs(file_basedir)
                file_path = os.path.join(file_basedir, "__init__.py")

                if not os.path.exists(file_path):
                    with open(file_path, "w") as fp:
                        fp.write(Python.HEADER.format(package=Generator.MODULE_NAME))

                with open(file_path, "a") as fp:
                    # TFAPIModule: repeated {member, member_method}
                    self._write_module(tf_api_object.tf_module)

            if tf_api_object.HasField("tf_class"):
                explode = file_path.split(os.path.sep)
                file_basedir = os.path.sep.join(explode[:-1])
                class_name = explode[-1]
                if not os.path.exists(file_basedir):
                    os.makedirs(file_basedir)
                file_path += ".py"

                if not os.path.exists(file_path):
                    with open(file_path, "w") as fp:
                        fp.write(Python.HEADER.format(package=Generator.MODULE_NAME))

                with open(file_path, "a") as fp:
                    self._write_class(fp, class_name, tf_api_object.tf_class)

            # Format the file
            black.format_file_in_place(
                pathlib.Path(file_path),
                fast=True,
                mode=black.FileMode(),
                write_back=black.WriteBack.YES,
            )
            break
