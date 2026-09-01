"""Cầu nối A30–B80: quan hệ hữu hạn. Original code, MIT; see notices."""


def is_function(pairs):
    outputs = {}
    for x, y in pairs:
        if x in outputs and outputs[x] != y:
            return False
        outputs[x] = y
    return True


def tests():
    cases = [
        ([(-1, -1), (-2, -2), (-3, -3)], True),
        ([(3, 4), (4, 5), (5, 6)], True),
        ([(2, 5), (7, 11), (15, 8), (7, 9)], False),
        ([("plain", 149), ("jelly", 199), ("chocolate", 199)], True),
        ([(149, "plain"), (199, "jelly"), (199, "chocolate")], False),
        ([(1, 2), (1, 2)], True),
        ([], True),
        ([("odd", 1), ("even", 2), ("odd", 3), ("even", 4), ("odd", 5)], False),
        ([(1, 2), (2, 4), (3, 6), (4, 8), (5, 10)], True),
    ]
    for pairs, expected in cases:
        assert is_function(pairs) is expected, (pairs, expected)
    names = ["Babe Ruth", "Willie Mays", "Ty Cobb", "Walter Johnson", "Hank Aaron"]
    ranks = list(zip(names, range(1, 6)))
    assert is_function(ranks)
    assert is_function([(rank, name) for name, rank in ranks])
    assert not is_function([(1, "Babe Ruth"), (4, "Walter Johnson"), (4, "Hank Aaron")])
    intervals = [(0, 56, 0.0), (57, 61, 1.0), (62, 66, 1.5), (67, 71, 2.0),
                 (72, 77, 2.5), (78, 86, 3.0), (87, 91, 3.5), (92, 100, 4.0)]
    grading = [(score, grade) for low, high, grade in intervals for score in range(low, high + 1)]
    assert len(grading) == 101
    assert is_function(grading)
    assert not is_function([(grade, score) for score, grade in grading])
    return 15


if __name__ == "__main__":
    print(f"PASS: {tests()} mathematical checks")
