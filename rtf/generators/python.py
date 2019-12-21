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
from .base import Generator


class Python(Generator):
    """Generator for the Python programming language."""

    def convert(self, dest_dir, golden_proto_dict):
        # test: Keras models
        keras_proto_dict = {
            key: value for key, value in golden_proto_dict.items() if "keras" in key
        }
        print(keras_proto_dict)
