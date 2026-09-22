"""Untrusted process: expose candidate outputs only, never decide pass/fail."""
import copy
import importlib
import json
import sys


def mutable_ids(value):
    if isinstance(value, dict):
        return {id(value)}.union(*(mutable_ids(v) for v in value.values()))
    if isinstance(value, list):
        return {id(value)}.union(*(mutable_ids(v) for v in value))
    return set()


def main():
    request = json.load(sys.stdin)
    module = importlib.import_module("solution")
    function = getattr(module, request["function"])
    rows = []
    for args in request["inputs"]:
        original = copy.deepcopy(args)
        try:
            output = function(*args)
            rows.append({"value": output, "mutated": args != original,
                         "alias": bool(mutable_ids(output) & mutable_ids(args))})
        except Exception as error:
            rows.append({"raises": type(error).__name__, "mutated": args != original})
    print(json.dumps(rows, allow_nan=False))


if __name__ == "__main__":
    main()
