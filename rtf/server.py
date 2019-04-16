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

"""Remote Tensorflow Execution, gRCP server."""

import time
from concurrent import futures
import grpc
from .proto import rtf_pb2_grpc
from .service import RTFServicer


def main():
    """Serving function."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rtf_pb2_grpc.add_RTFServicer_to_server(RTFServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    while True:
        time.sleep(1)
    return 1


if __name__ == "__main__":
    main()
