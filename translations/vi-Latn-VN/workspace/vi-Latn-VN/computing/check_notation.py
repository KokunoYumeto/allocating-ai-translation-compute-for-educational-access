"""Original finite checks for the U002 explanations, not a source solution donor."""


def tests():
    # The domain is month names in a non-leap year, not a set of years.
    months = ("January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December")
    days = dict(zip(months, [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]))
    assert len(days) == 12 and set(days) == set(months)
    assert days["January"] == 31
    assert days["March"] == 31
    assert days["February"] == 28
    assert sum(days.values()) == 365
    # Reader's explicitly new counterexample: generally f(a+b) != f(a)+f(b).
    def f(x):
        return x * x
    assert f(2 + 3) == 25
    assert f(2) + f(3) == 13
    assert f(2 + 3) != f(2) + f(3)
    # A finite record can express the hypothetical source datum; not a real census.
    police_count = {2005: 300}
    assert police_count[2005] == 300
    return 9


if __name__ == "__main__":
    print(f"PASS: {tests()} notation checks")
