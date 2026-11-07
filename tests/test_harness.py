"""Hand-wired boards (tools/boards.py): layouts that need the fewest assembly operations."""
import pytest

import boards    # tools/, on the path through conftest.py

PENDING = {'s3'}  # a single move still lowers its score: optimised layout waits for review
BASELINE = {'s3': 28, 'p1': 2, 'p2': 4, 'power': 20}  # scores before TECH-HARNESS-BOARDS-001


@pytest.mark.req('TECH-HARNESS-BOARDS-001')
@pytest.mark.parametrize('board', [pytest.param(b, marks=pytest.mark.xfail(strict=True, reason='proposed layout not applied yet'))
                                   if b['key'] in PENDING else b for b in boards.BOARDS], ids=lambda b: b['key'])
def test_board_layout_is_a_local_minimum_of_the_assembly_score(board):
    # Given a board as committed: it passes its checks and scores no worse than before the requirement
    assert boards.check(board)[0] == []
    assert boards.score(board) <= BASELINE[board['key']]
    # When one part or one wire end moves to a free hole and the links are laid again
    cheaper = [m for m in boards.neighbours(board) if boards.score(m) < boards.score(board)]
    # Then no such layout is cheaper
    assert cheaper == []
