import pytest
import wichtel


@pytest.mark.parametrize(
    "source, image, result",
    [
        ([], [], True),
        ([1], [1], False),
        ([1, 2], [2, 1], True),
        ([1, 2, 3], [2, 3, 1], True),
        ([1, 2], [1, 2], False),
        ([1, 2, 3], [3, 2, 1], False),
        (["Alice", "Bob", "Caroline"], ["Bob", "Caroline", "Alice"], True),
        (["Alice", "Bob", "Caroline"], ["Caroline", "Bob", "Alice"], False),
    ],
)
def test_all_different(source, image, result):
    assert wichtel.all_different(source, image) == result


@pytest.mark.parametrize(
    "source, image, result",
    [
        ([1, 2], [2, 1], True),
        ([1, 2, 3], [2, 3, 1], False),
        ([1, 2, 3, 4], [2, 1, 4, 3], True),
    ],
)
def test_has_isolated_transposition(source, image, result):
    assert wichtel.has_isolated_transposition(source, image) == result


@pytest.mark.parametrize(
    "source, image, tabus, result",
    [
        ([1, 2], [2, 1], {1: [], 2: []}, False),
        ([1, 2], [2, 1], {1: [1], 2: [2]}, False),
        ([1, 2], [2, 1], {1: [2], 2: []}, True),
        ([1, 2], [2, 1], {1: [1, 2], 2: [1, 2]}, True),
    ],
)
def test_matches_tabus(source, image, tabus, result):
    assert wichtel.matches_tabus(source, image, tabus) == result


@pytest.mark.parametrize(
    "tabus",
    [
        {1: [], 2: [], 3: []},
    ],
)
def test_matching(tabus):
    match = wichtel.matching(tabus)
    source = list(match.keys())
    image = [match[s] for s in source]

    assert wichtel.all_different(source, image)
    assert not wichtel.has_isolated_transposition(source, image)
    assert not wichtel.matches_tabus(source, image, tabus)
    assert wichtel.good_matching(source, image, tabus)
