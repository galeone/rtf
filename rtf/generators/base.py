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

"""Base structures for any RTF client generator."""

import abc
import ast
import logging
import os
import re
from glob import glob

from google.protobuf import text_format

from ..proto.lib import api_objects_pb2


class Generator:
    """Base class for any RTF client generator."""

    MODULE_NAME = "tensorflow"

    @staticmethod
    def snake_to_camel(name):
        """Convert a sname_name to a CamelName."""
        return name.replace("_", " ").title().replace(" ", "")

    @staticmethod
    def camel_to_snake(name):
        """Convert a CamelName to a snake_name."""
        sub = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", sub).lower()

    @staticmethod
    def _filename_to_key(filename):
        """From a given filename, construct a key we use for api objects."""

        def _replace_dash_with_caps(matchobj):
            match = matchobj.group(0)
            return match[1].upper()

        base_filename = os.path.basename(filename)
        base_filename_without_ext = os.path.splitext(base_filename)[0]
        api_object_key = re.sub(
            "((-[a-z]){1})", _replace_dash_with_caps, base_filename_without_ext
        )
        return api_object_key

    @staticmethod
    def _read_file_to_proto(filename):
        """Read a filename, create a protobuf from its contents."""

        ret_val = api_objects_pb2.TFAPIObject()
        with open(filename, "r") as fp_pbtxt:
            pbtxt = fp_pbtxt.read()
        text_format.Merge(pbtxt, ret_val)
        return ret_val

    @staticmethod
    def _filter_golden_proto_dict(golden_proto_dict, omit_golden_symbols_map):
        """Filter out golden proto dict symbols that should be omitted."""

        if not omit_golden_symbols_map:
            return golden_proto_dict
        filtered_proto_dict = dict(golden_proto_dict)
        for key, symbol_list in omit_golden_symbols_map.items():
            api_object = api_objects_pb2.TFAPIObject()
            api_object.CopyFrom(filtered_proto_dict[key])
            filtered_proto_dict[key] = api_object
            module_or_class = None
            if api_object.HasField("tf_module"):
                module_or_class = api_object.tf_module
            elif api_object.HasField("tf_class"):
                module_or_class = api_object.tf_class
            if module_or_class is not None:
                for members in (module_or_class.member, module_or_class.member_method):
                    filtered_members = [m for m in members if m.name not in symbol_list]
                    # Two steps because protobuf repeated fields disallow slice assignment.
                    del members[:]
                    members.extend(filtered_members)
        return filtered_proto_dict

    @staticmethod
    def get_golden_proto_dict(tensorflow_version):
        """
        Get the GOLDEN proto dictionary of the TensorFlow API at
        the specified version (if available).
        """

        proto_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.path.pardir,
            "proto",
            "r" + str(tensorflow_version),
            "*.pbtxt",
        )
        golden_file_list = glob(proto_path)
        golden_proto_dict = {
            Generator._filename_to_key(filename): Generator._read_file_to_proto(
                filename
            )
            for filename in golden_file_list
        }
        omit_golden_symbols_map = {}
        golden_proto_dict = Generator._filter_golden_proto_dict(
            golden_proto_dict, omit_golden_symbols_map
        )
        return golden_proto_dict

    @abc.abstractmethod
    def convert(self, dest_dir, golden_proto_dict):
        """
        The convert function to use for creating the
        files in the target language.
        Use the golden_proto_dict to create the client.

        Args:
            dest_dir: the destination dir of the package
            golden_proto_dict: the dictionary of the TensorFlow API
                               (obtained via get_golden_proto_dict).
        """

    def __call__(self, dest_dir, tensorflow_version):
        base_dir = os.path.join(dest_dir, Generator.MODULE_NAME)
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        self.convert(dest_dir, Generator.get_golden_proto_dict(tensorflow_version))


class Parser:
    @staticmethod
    def _parse_argspec(argspec):
        # Argspec needs to be "corrected" in order to be correctly parsed.
        # Eg. The argspect of certain methods could be: args=['something'], varargs=args
        # but since args is not a variable, this will throw an error when parsed using
        # literal eval.
        args = f"f({argspec})"
        args = args.replace("varargs=args", "varargs='args'").replace(
            "keywords=kwargs", "keywords='kwargs'"
        )

        tree = ast.parse(args)
        funccall = tree.body[0].value
        # { 'args': [], 'varargs': [], 'keywords': [], 'defaults': [] }
        return {arg.arg: ast.literal_eval(arg.value) for arg in funccall.keywords}

    @abc.abstractstaticmethod
    def build_signature(argspec):
        """Given an input argspec (obtained via _parse_argspec), builds
        the signature for the function, in the target language.
        """
