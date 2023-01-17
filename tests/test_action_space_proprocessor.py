import pytest
from gym.spaces import Tuple, Dict, Box, Discrete
from godot_rl.core.godot_env import GodotEnv
from godot_rl.core.utils import ActionSpaceProcessor

@pytest.mark.parametrize("action_space", 
    [
        Tuple([Box(-1,1, shape=[7]), Box(-1,1, shape=[11])]),
        Tuple([Box(-1,1, shape=[7]), Discrete(2)]),
        Tuple([Discrete(2), Discrete(2)]),
        Tuple([Discrete(2), Discrete(2), Box(-1,1, shape=[11])]),
    ]



)
def test_action_space_preprocessor(action_space):

    expected_output = 0

    for space in action_space.spaces:
        if isinstance(space, Box):
            assert len(space.shape) ==1
            expected_output += space.shape[0]
        elif isinstance(space, Discrete):
            if space.n > 2:
                # for not only binary actions are supported, need to add support for the n>2 case
                raise NotImplementedError
            expected_output += 1

    preprocessor = ActionSpaceProcessor(action_space, True)

    assert expected_output == preprocessor.action_space.shape[0]

    preprocessor = ActionSpaceProcessor(action_space, False)
    for s1, s2 in zip(action_space.spaces, preprocessor.action_space.spaces):
        if isinstance(s1, Box):
            assert s1.shape == s2.shape
        elif isinstance(s2, Discrete):
            assert s1.n == s2.n
