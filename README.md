# Remote Tensorflow Execution (RTF)

Bring the power of the Tensorflow Python API to any language, using gRPC.

This repository contains the code of the RTF server and client generator.

**WARNING**: experimental, unstable, WIP.

## Server

The gRPC server implements the server-side protocol. It accepts the requests of function definitions and executes them.
The execution is left to the Python interpreter and the output is streamed back to the client.

### Usage

The server waits for messages and sends back the responses.

#### Requirements

Compile the proto definition is required, however the `setup.py` script takes care of everything. There are 2 options

1. `pip install -e .` to work in edit mode, with the compiled protobufs
2. `pip install .` to install the package (it compiles the proto too)
3. (future) `pip install rtf` | `pip install rtf-gpu`

#### 1. Start the gRPC server

```
python -m rtf.server
```

## Client stub generation

To generate the stub of a client in `DEST_DIR` use the `rtf.generate` module.

```
python -m rtf.generate  --dest_dir DEST_DIR --module tensorflow --target Go

```

Right now the only generator that is going to be developed is Go.
