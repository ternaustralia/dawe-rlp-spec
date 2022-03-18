# DAWE RLP Specification

This repository contains the specification requirements and validators for the DAWE RLP field survey protocols developed by TERN.

View the specification:
- Web document: https://ternaustralia.github.io/dawe-rlp-spec

- PDF document: https://ternaustralia.github.io/dawe-rlp-spec/spec.pdf

## Repository structure

- Specification source files (asciidoc) are located within the `docs/` directory.
- SHACL shapes are defined in the `shapes/` directory.

## Specification document

Please see [docs/README.md](docs/README.md) for more information.

## SHACL shapes directory structure

SHACL shapes reside in the `shapes/` directory. The `shapes/` directory contains subdirectories to each of the protocol modules. Each protocol module contains a directory named after an observable property. This observable property directory contains 3 RDF Turtle files:

- `shapes.ttl` - the shapes for the observable property
- `valid.ttl` - valid examples
- `invalid.ttl` - invalid examples

## Development

This project is developed within Visual Studio Code devcontainers. 

To ensure all the tools required for this project are available and installed correctly, please use VS Code and Docker, and open the project inside a container using the extension `ms-vscode-remote.remote-containers`.

### SHACL shapes

Any additions or modifications to RDF Turtle files must use the supplied `Makefile` to normalize the content for better version control diffing. 

Run the command:

```
make normalize
```

This will find all files that end in `.ttl` in the `shapes/` directory and apply [RDFLib's](https://github.com/RDFLib/rdflib) `longturtle` serialization method.

### Run tests

These tests ensure the shapes do what they are supposed to do by testing against valid and invalid data.

Tests use [pySHACL](https://github.com/RDFLib/pySHACL) to ensure the shapes defined with SHACL do what they are supposed to do by testing against valid and invalid data.

Tests also check to ensure shapes are in the RDF Turtle syntax and there is no syntax issues.

To run the tests, run the following command:

```
pytest
```

### Run validator

The VS Code devcontainer provides SHACL processors, pySHACL and [TopQuadrant/shacl](https://github.com/TopQuadrant/shacl).

Makefile targets have been provided for your convenience.

| Target          | Description                                                               |
|-----------------|---------------------------------------------------------------------------|
| `pyshacl-af`    | pySHACL with SHACL Advanced Features                                      |
| `pyshacl`       | pySHACL basic                                                             |
| `validate`      | Validate with `TopQuadrant/shacl`                                         |
| `validate-meta` | Validate with `TopQuadrant/shacl` with the meta shapes validation enabled |

Example:

```
make validate shape=path/to/shape.ttl data=path/to/data.ttl
```

Alternatively, you can run the SHACL processors directly.

```
pyshacl --help
```

```
shaclvalidate.sh --help
```

## Contact

Edmond Chuc  
e.chuc@uq.edu.au

Junrong Yu  
junrong.yu@uq.edu.au
