# Record check demo

A small Python example that locates missing required values and repeated IDs
before a data import. The report points back to the affected input rows so a
person can resolve ambiguous records without silently losing data.

This is an AI-assisted, synthetic portfolio demonstration. It contains no client
data and does not represent paid customer work. It performs no network requests
and uses only Python's standard library.

## Try it

Use Python 3.9 or newer, from this folder:

```text
python -B record_check.py sample.json
python -B -m unittest -v
```

The first command prints the report; it does not create or overwrite a file.
Its output should match `expected.json`. The second runs five tests.

## What the example finds

The six invented records contain four flagged rows. Row 2 repeats row 1's ID
and lacks a name. Row 3 lacks an ID. Row 5 repeats row 4's ID. Row 6 has a
whitespace-only name. The input stays unchanged.

Duplicate IDs are compared exactly: `001`, `1` and ` 1` are different. Leading
zeros, case and whitespace are preserved. Blank IDs are reported as missing,
not grouped together as duplicates. Duplicate references point to the first row
with that exact ID. Row numbers start at 1 within the records array.

## Scope and limits

Input is UTF-8 JSON with `required` and `records` keys. The CLI accepts at most
32 KiB, 100 records, 10 fields per record, and 256 characters per value. All
values must be strings; ambiguous duplicate JSON object keys are rejected.
Exit 0 means a report was produced, including when issues were found. Exit 2
means the input or invocation was rejected.

This example does not read CSV/Excel directly, remove duplicates, merge records,
validate business rules, or prove a file is ready for a production import. Those
decisions require agreed input examples and acceptance criteria. It is a local
demonstration, not a sandbox for untrusted scripts or a hosted service.

## Possible paid pilot

A bounded first batch could produce a row-linked exception report, agreed
corrections, and a reconciliation of input/output counts. File formats, matching
rules, authorized data, price, payment, deadline and acceptance checks must be
agreed before work begins. This sample is evidence of these specific checks,
not a claim of professional credentials or production deployment experience.
