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

"""Generator for the Go programming language."""
import os

from .base import Generator


class Go(Generator):
    """Generator for the Go programming language."""

    HEADER = (
        "/**\n"
        " * This file is machine generated. Do NOT edit unless you\n"
        " * REALLY know what are you doing.\n"
        " */\n\n"
        "package {package}\n\n"
    )

    RTF_CLIENT = "type Sender struct {\n" "\tsend(*RTFMessage)\n" "}\n\n"

    FUNCTION = 'func {func_name}{func_signature} {{\n\tclient.Send("TODO")\n}}\n\n'

    CLASS = "type {type_name} struct {{\n\tSender\n}}\n\n"

    METHOD = (
        "func (me *{type_name}) {func_name}{func_signature} {{\n"
        '\tme.send("TODO")\n'
        "}}\n\n"
    )

    def _create_commons(self, module, dest_dir):
        module_name = module.name.split(".")[-1]
        base_dir = os.path.join(dest_dir, Generator.MODULE_NAME)
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)

        # TODO: Compile the .proto to .go

        common_file = os.path.join(base_dir, "_" + Generator.MODULE_NAME + ".go")
        with open(common_file, "w") as fp:
            # The header puts the file into the same package
            fp.write(Go.HEADER.format(package=Generator.MODULE_NAME))
            fp.write("import (\n")
            for package in ["context", "google.golang.org/grpc"]:
                fp.write('\t"{}"\n'.format(package))
            fp.write(")\n\n")
            fp.write(
                "var opts []grpc.DialOption\n"
                "opts = append(opts, grpc.WithInsecure())\n"
                'conn, err := grpc.Dial("127.0.0.1:5001", opts...)\n'
                "if err != nil {\n"
                '\tpanic("failed to dial client")\n'
                "}\n"
                "defer conn.Close()\n"
                "client := rtf.NewRTFClient(conn)\n"
            )

    def convert(self, dest_dir, golden_proto_dict):
        base_dir = os.path.join(dest_dir, Generator.MODULE_NAME)
        package_file = os.path.join(base_dir, Generator.MODULE_NAME + ".go")
        with open(package_file, "w") as fp:
            # Main package: contains only the converted functions
            # + some Go utilities.
            fp.write(Go.HEADER.format(package=Generator.MODULE_NAME))
            for func in module.functions:
                if not func.private or keep_private:
                    name = func.name.split(".")[-1]
                    name = Generator.snake_to_camel(name)
                    line = Go.FUNCTION.format(
                        func_name=name, func_signature=func.signature
                    )
                    fp.write(line)
        raise ValueError("TODO: refactor me - using the GOLDEN dict proto information")

        # Every class is a new file. Every new file is memmber of the package.
        for cls in module.classes:
            py_name = cls.name.split(".")[-1]
            file_path = os.path.join(
                base_dir, Generator.camel_to_snake(py_name) + ".go"
            )
            with open(file_path, "w") as fp:
                type_name = Generator.snake_to_camel(py_name)
                fp.write(Go.HEADER.format(package=Generator.MODULE_NAME))
                fp.write(Go.CLASS.format(type_name=type_name))

                fp.write(
                    "func New{func_name}{func_signature} *{func_name} {{\n"
                    "\treturn &{func_name}{{}}\n"
                    "}}\n\n".format(
                        func_name=type_name,
                        func_signature=cls.init.signature.replace("self", "").replace(
                            "(, ", "("
                        )
                        if cls.init
                        else "()",
                    )
                )

                if cls.call:
                    fp.write(
                        Go.METHOD.format(
                            type_name=type_name,
                            func_name="Call",
                            func_signature=cls.call.signature.replace(
                                "self", ""
                            ).replace("(, ", "("),
                        )
                    )

                for method in cls.methods:
                    if not method.private or keep_private:
                        fp.write(
                            Go.METHOD.format(
                                type_name=type_name,
                                func_name=Generator.snake_to_camel(
                                    method.name.split(".")[-1]
                                ),
                                func_signature=method.signature.replace(
                                    "self", ""
                                ).replace("(, ", "("),
                            )
                        )

        for submodule in module.modules:
            if not keep_private and submodule.private:
                continue
            modname = submodule.name.split(".")[-1]
            # self.convert(submodule, base_dir, keep_private)
