"""Host-side expected values. Never mounted in the candidate container."""
CASES = {
    "intervals": {
        "public": [([1, 4, 2], True), ([1, 4, 0], False)],
        "hidden": [([1, 4, 4], False), ([2, 2, 2], False), ([-3, 0, -1], True)],
        "function": "contains",
    },
    "unique": {
        "public": [([[1, 1]], [1]), ([[]], [])],
        "hidden": [([[[2], [1], [2]]], [[2], [1]]), ([[3, 1, 3, 2]], [3, 1, 2])],
        "function": "unique",
    },
    "chunks": {
        "public": [([[1, 2, 3, 4], 2], [[1, 2], [3, 4]])],
        "hidden": [([[1, 2, 3], 2], [[1, 2], [3]]), ([[], 2], []),
                   ([[1], -1], {"raises": "ValueError"}), ([[1], 0], {"raises": "ValueError"})],
        "function": "chunks",
    },
    "merge": {
        "public": [([{"x": 1}, {"x": 2}], {"x": 2})],
        "hidden": [([{"x": {"a": 1, "b": 2}, "z": []}, {"x": {"a": 3}, "q": []}],
                    {"x": {"a": 3, "b": 2}, "z": [], "q": []})],
        "function": "merge",
    },
    "ledger": {
        "public": [([10, 3], 7)],
        "hidden": [([10, 10], 0), ([0, 0], 0), ([10, -1], {"raises": "ValueError"}),
                   ([10, 11], {"raises": "ValueError"})],
        "function": "debit",
    },
    "csv": {
        "public": [(["a,b"], ["a", "b"])],
        "hidden": [(['"a,b",c'], ["a,b", "c"]), (["a,,c"], ["a", "", "c"]),
                   (['"a""b",c'], ['a"b', "c"])],
        "function": "parse_row",
    },
}
