# Public example

`structures/example_complex.pdb` is a two-chain toy complex containing one
target chain (`A`) and one binder chain (`B`). It is synthetic and contains no
project data. Run:

```bash
phbinder --input examples/structures --output /tmp/phbinder_example.csv
```

The expected output schema is recorded in `expected_columns.txt`; numeric scores
can change with software versions and pH settings.
