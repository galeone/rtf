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

    def convert(self, module, dest_dir, keep_private=False):
        if not module:
            return
        base_dir = os.path.join(dest_dir, module.name.split(".")[-1])
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        for submodule in module.modules:
            if not keep_private and submodule.private:
                continue
            modname = submodule.name.split(".")[-1]
            self.convert(submodule, base_dir, keep_private)
