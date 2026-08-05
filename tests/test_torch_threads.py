import pytest
import torch

from godot_rl.core.utils import set_torch_threads


def test_none_leaves_torch_untouched():
    before = torch.get_num_threads()
    assert set_torch_threads(None) is None
    assert torch.get_num_threads() == before


def test_applies_the_requested_count():
    before = torch.get_num_threads()
    try:
        assert set_torch_threads(1) == 1
        assert torch.get_num_threads() == 1
    finally:
        torch.set_num_threads(before)


@pytest.mark.parametrize("num_threads", [0, -1])
def test_rejects_counts_below_one(num_threads):
    with pytest.raises(ValueError):
        set_torch_threads(num_threads)
