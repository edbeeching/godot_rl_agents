import importlib
import re

import gymnasium as gym
import numpy as np


def lod_to_dol(lod):
    return {k: [dic[k] for dic in lod] for k in lod[0]}


def dol_to_lod(dol):
    return [dict(zip(dol, t)) for t in zip(*dol.values())]


def convert_macos_path(env_path):
    """
    On MacOs the user is supposed to provide a application.app file to env_path.
    However the actual binary is in application.app/Contents/Macos/application.
    This helper function converts the path to the path of the actual binary.

    Example input: ./Demo.app
    Example output: ./Demo.app/Contents/Macos/Demo
    """

    filenames = re.findall(r"[^\/]+(?=\.)", env_path)
    assert len(filenames) == 1, "An error occured while converting the env path for MacOS."
    return env_path + "/Contents/MacOS/" + filenames[0]


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

        if convert:
            use_multi_discrete_spaces = False
            multi_discrete_spaces = np.array([])
            if isinstance(action_space, gym.spaces.Tuple):
                if all(isinstance(space, gym.spaces.Discrete) for space in action_space.spaces):
                    use_multi_discrete_spaces = True
                    for space in action_space.spaces:
                        multi_discrete_spaces = np.append(multi_discrete_spaces, space.n)
                else:
                    for space in action_space.spaces:
                        if isinstance(space, gym.spaces.Box):
                            assert len(space.shape) == 1
                            space_size += space.shape[0]
                        elif isinstance(space, gym.spaces.Discrete):
                            if space.n > 2:
                                # for now only binary actions are supported if you mix different spaces
                                raise NotImplementedError(
                                    "Discrete actions with size larger than 2 "
                                    "are currently not supported if used together with continuous actions."
                                )
                            space_size += 1
                        else:
                            raise NotImplementedError
            elif isinstance(action_space, gym.spaces.Dict):
                raise NotImplementedError
            else:
                assert isinstance(action_space, (gym.spaces.Box, gym.spaces.Discrete))
                return

            if use_multi_discrete_spaces:
                self.converted_action_space = gym.spaces.MultiDiscrete(multi_discrete_spaces)
            else:
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

        # If only discrete actions are used in the environment:
        # - SB3 will send int actions containing the discrete action,
        # - CleanRL example script (continuous PPO) will only send float actions, which we convert to binary discrete,
        # - If mixed actions are used, both will send float actions.
        integer_actions: bool = action.dtype == np.int64

        for space in self._original_action_space.spaces:
            if isinstance(space, gym.spaces.Box):
                assert len(space.shape) == 1
                original_action.append(action[:, counter : counter + space.shape[0]])
                counter += space.shape[0]

            elif isinstance(space, gym.spaces.Discrete):
                discrete_actions = None

                if integer_actions:
                    discrete_actions = action[:, counter]
                else:
                    if space.n > 2:
                        raise NotImplementedError(
                            "Discrete actions with size larger than "
                            "2 are currently not implemented for this algorithm."
                        )
                    # If the action is not an integer, convert it to a binary discrete action
                    discrete_actions = np.greater(action[:, counter], 0.0)
                    discrete_actions = discrete_actions.astype(np.float32)

                original_action.append(discrete_actions)
                counter += 1

            else:
                raise NotImplementedError

        return original_action


def can_import(module_name):
    return not cant_import(module_name)


def cant_import(module_name):
    try:
        importlib.import_module(module_name)
        return False
    except ImportError:
        return True
