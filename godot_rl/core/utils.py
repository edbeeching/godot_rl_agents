import gym
import numpy as np


def lod_to_dol(lod):
    return {k: [dic[k] for dic in lod] for k in lod[0]}


def dol_to_lod(dol):
    return [dict(zip(dol, t)) for t in zip(*dol.values())]


class ActionSpaceProcessor:
    # can convert tuple action dists to a single continuous action distribution
    # eg (Box(a), Box(b)) -> Box(a+b)
    # (Box(a), Discrete(2)) -> Box(a+2)
    # etc
    # does not yet work with discrete dists of n>2
    def __init__(self, action_space: gym.spaces.Tuple, convert) -> None:

        self._original_action_space = action_space
        self._convert = convert

        space_size = 0
        if isinstance(action_space, gym.spaces.Tuple):

            for space in action_space.spaces:
                if isinstance(space, gym.spaces.Box):
                    assert len(space.shape) == 1
                    space_size += space.shape[0]
                elif isinstance(space, gym.spaces.Discrete):
                    if space.n > 2:
                        # for not only binary actions are supported, need to add support for the n>2 case
                        raise NotImplementedError
                    space_size += 1
                else:
                    raise NotImplementedError
        elif isinstance(action_space, gym.spaces.Dict):
            raise NotImplementedError
        else:
            assert isinstance(space, [gym.spaces.Box, gym.spaces.Discrete])
            return

        self.converted_action_space = gym.spaces.Box(-1, 1, shape=[space_size])

    @property
    def action_space(self):
        if not self._convert:
            return self._original_action_space

        return self.converted_action_space

    def to_original_dist(self, action):
        if not self._convert:
            return action

        original_action = []
        counter = 0

        for space in self._original_action_space.spaces:
            if isinstance(space, gym.spaces.Box):
                assert len(space.shape) == 1
                original_action.append(action[:, counter : counter + space.shape[0]])
                counter += space.shape[0]

            elif isinstance(space, gym.spaces.Discrete):

                discrete_actions = np.greater(action[:, counter], 0.0)
                discrete_actions = discrete_actions.astype(np.float32)
                original_action.append(discrete_actions)

            else:
                raise NotImplementedError

        return original_action
