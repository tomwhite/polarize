from functools import cache
from hypothesis import strategies as st

from polarize.encode import all_boards, decode_board

@cache
def _all_board_vals(num_pieces):
    return all_boards(num_pieces)[0]

@st.composite
def boards(draw, max_num_pieces=4):
    """A hypothesis strategy for generating Polarize boards"""
    num_pieces = draw(st.integers(1, max_num_pieces))
    val = draw(st.sampled_from(_all_board_vals(num_pieces)))
    return decode_board(val)
