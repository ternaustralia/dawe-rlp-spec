# EMSA profile

Class-level SHACL shapes for the Ecological Monitoring System - Australia (EMSA), declared as a
profile of the [TERN Ontology](https://w3id.org/tern/profiles/tern).

| File | Contents |
|---|---|
| `emsa.profile.ttl` | The `prof:Profile` declaration and its resource descriptors |
| `emsa-shapes.ttl` | The EMSA shapes graph: the exceptions to the TERN Ontology shapes, and the constraints EMSA adds |
| `valid.ttl` | Data that must conform |
| `invalid.ttl` | Data that must fail, one case per rule |

## How the validator is assembled

EMSA data is validated against three sets of shapes merged into one graph:

1. the TERN Ontology shapes (`tern.shapes.ttl`, maintained in the `ontology_tern` repository),
2. this profile (`emsa-shapes.ttl`),
3. the shapes of the survey protocol the data was collected under (the other directories under `shapes/`).

Two things to note:

- **The profile is not optional.** Validating EMSA data against the TERN Ontology shapes alone
  reports the EMSA exceptions as errors.
- **SHACL Advanced Features must be enabled.** The protocol shapes select their targets with
  `sh:SPARQLTarget`. A validator running SHACL Core skips those shapes silently, without warning.
  In pySHACL this is `advanced=True`, or `-a` on the command line.

```bash
pyshacl -s <merged-shapes.ttl> -a <data.ttl>
```

## What the profile adds

`tern:Procedure` must give its method with `tern:hasMethod`. The TERN Ontology accepts either
`tern:hasMethod` or `rdf:value`; EMSA always uses `tern:hasMethod`.

## Tests

`shapes/emsa-profile/valid.ttl` and `invalid.ttl` run as part of the repository test suite via
`tests/manifests.py`. `tests/test_emsa_profile.py` additionally checks the profile against the real
TERN Ontology shapes, including that every deactivated shape is restated. Those tests are skipped
unless the TERN shapes are available locally, either at `../ontology_tern/docs/tern.shapes.ttl` or
at the path in the `TERN_SHAPES` environment variable.
