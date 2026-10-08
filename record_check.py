"""Small, local JSON record checker. Reads one input; writes only to stdout."""
import argparse
import json
from pathlib import Path
import sys

MAX_BYTES = 32768


def check(data):
    """Report missing fields and repeated nonblank IDs without changing records."""
    if not isinstance(data, dict) or set(data) != {"required", "records"}:
        raise ValueError("Expected required and records keys")
    required, records = data["required"], data["records"]
    if (not isinstance(required, list) or not 1 <= len(required) <= 10
            or not all(isinstance(x, str) and 1 <= len(x) <= 40 for x in required)):
        raise ValueError("Expected 1-10 nonempty required field names, at most 40 characters each")
    if len(set(required)) != len(required) or "id" not in required:
        raise ValueError("Required fields must be unique and include id")
    if not isinstance(records, list) or not 1 <= len(records) <= 100:
        raise ValueError("Expected 1-100 records")
    for record in records:
        if (not isinstance(record, dict) or len(record) > 10
                or not all(isinstance(k, str) and 1 <= len(k) <= 40
                           and isinstance(v, str) and len(v) <= 256
                           for k, v in record.items())):
            raise ValueError("Records must have at most 10 named string fields; values at most 256 characters")
    seen = {}
    rows = []
    for number, record in enumerate(records, 1):
        missing = [name for name in required if not record.get(name, "").strip()]
        identifier = record.get("id", "")
        first = seen.get(identifier) if identifier.strip() else None
        rows.append({"row": number, "missing_fields": missing, "duplicate_of_row": first})
        if identifier.strip() and identifier not in seen:
            seen[identifier] = number
    flagged = sum(bool(row["missing_fields"]) or row["duplicate_of_row"] is not None for row in rows)
    return {"total_rows": len(rows), "flagged_rows": flagged, "rows": rows}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        if not args.input.is_file():
            raise ValueError("Input must be a regular file")
        with args.input.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Input exceeds 32 KiB")
        data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object)
        report = check(data)
    except (OSError, ValueError, RecursionError):
        print("Input rejected: expected bounded UTF-8 JSON with string-valued records and unique keys.", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
