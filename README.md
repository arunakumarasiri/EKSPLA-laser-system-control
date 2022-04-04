# EKSPLA Remote Control

Python wrapper around EKSPLA's `REMOTECONTROL.dll`.

## Build

Building requires [`build`](//pypi.org/project/build) and can be done by executing:

```sh
python -m build
```

## Install

To install the package remotely from the Git repository:

```sh
pip install git+https://github.com/arunakumarasiri/EKSPLA
```

For development purposes, you can locally install the package using:

```sh
pip install --editable .
```

## Usage

Please refer to the [examples directory](examples/) for examples on how to use.

The library requires `REMOTECONTROL.csv` to be present in the current working directory.

Note that a 32-bit version of Python is also required because of the underlying DLLs.
