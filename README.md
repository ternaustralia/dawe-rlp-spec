# DAWE RLP Specification

This repository contains the specification requirements and validators for the DAWE RLP field survey protocols developed by TERN.

## SHACL shapes

SHACL shapes reside in the `shapes/` directory. The `shapes/` directory contains subdirectories to each of the protocol modules. Each protocol module contains a directory named after an observable property. This observable property directory contains 3 RDF Turtle files:

- `shapes.ttl` - the shapes for the observable property
- `valid.ttl` - valid examples
- `invalid.ttl` - invalid examples

## Editing

We use ontotools, a Python command line application to normalize the source files.

Ensure the following instructions are performed whenever edits are made to files before committing to git.

### Create a Python 3 virtual environment

```bash
python3 -m venv venv
```

### Activate the virtual environment

```bash
source venv/bin/activate
```

### Install the required packages

```bash
pip install -r requirements.txt
```

### Run ontotools to normalize Turtle files

```bash
ontotools file normalize <file-path>
```

## Run validator

Build the docker container
```
make build
```
Validate the invalid and valid examples with `shapes.ttl`
```
make validate shape=shape_path data=data_file_path
```

## Contact

Edmond Chuc  
e.chuc@uq.edu.au

Junrong Yu  
junrong.yu@uq.edu.au
