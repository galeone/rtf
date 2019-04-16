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

import logging
import inspect
import types
import importlib
import abc
from collections import namedtuple

Func = namedtuple("Func", "name signature private")
Class = namedtuple("Class", "name methods private")
Module = namedtuple("Module", "name modules functions classes private")


class Generator:
    """Base class for any RTF client generator."""

    @staticmethod
    def _inspect_function(element_name, element):
        return Func(
            name=element_name,
            signature=str(inspect.signature(element)),
            private=element_name.startswith("_"),
        )

    @staticmethod
    def _inspect_class(element_name, element):
        methods = [
            Generator._inspect_function(method_name, getattr(element, method_name))
            for method_name in dir(element)
            if isinstance(getattr(element, method_name), types.FunctionType)
        ]
        return Class(
            name=element_name, methods=methods, private=element_name.startswith("_")
        )

    @staticmethod
    def inspect_module(name):
        """Given a name module, returns the Module object containing its description."""
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError as exc:
            logging.warning("Unable to import module: %s - error %s", name, exc)
            return None

        functions = []
        modules = []
        classes = []
        for element_name in dir(module):
            element = getattr(module, element_name)
            fullname = name + "." + element_name
            if inspect.ismodule(element):
                submodule = Generator.inspect_module(fullname)
                if submodule:
                    modules.append(submodule)
            elif inspect.isclass(element):
                classes.append(Generator._inspect_class(fullname, element))
            elif hasattr(element, "__call__"):
                functions.append(Generator._inspect_function(fullname, element))

        return Module(
            name=name,
            modules=modules,
            functions=functions,
            classes=classes,
            private=name.split(".")[-1].startswith("_"),
        )

    @abc.abstractmethod
    def convert(self, module, dest_dir, keep_private=False):
        """The convert function, usually recursive, to use for creating the
        files in the target language. Converts the module from python.
        """

    def __call__(self, module, dest_dir, keep_private=False):
        return self.convert(module, dest_dir, keep_private)
