"""
An example that shows how to use SampleFactory with a Gym env.
Example command line for CartPole-v1:
python -m sample_factory_examples.train_gym_env --algo=APPO --use_rnn=False --num_envs_per_worker=20 --policy_workers_per_policy=2 --recurrence=1 --with_vtrace=False --batch_size=512 --hidden_size=256 --encoder_type=mlp --encoder_subtype=mlp_mujoco --reward_scale=0.1 --save_every_sec=10 --experiment_summaries_interval=10 --experiment=example_gym_cartpole-v1 --env=gym_CartPole-v1
python -m sample_factory_examples.enjoy_gym_env --algo=APPO --experiment=example_gym_cartpole-v1 --env=gym_CartPole-v1
"""

import sys

import gym
from godot_rl_agents.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv


from sample_factory.algorithms.utils.arguments import arg_parser, parse_args
from sample_factory.envs.env_registry import global_env_registry
from sample_factory.run_algorithm import run_algorithm


def custom_parse_args(argv=None, evaluation=False):
    """
    Parse default SampleFactory arguments and add user-defined arguments on top.
    Setting the evaluation flag to True adds additional CLI arguments for evaluating the policy (see the enjoy_ scripts)
    """
    parser = arg_parser(argv, evaluation=evaluation)

    # insert additional parameters here if needed

    cfg = parse_args(argv=argv, evaluation=evaluation, parser=parser)
    return cfg


def make_godot_env_func(full_env_name, cfg=None, env_config=None):

    seed = 0
    port = 21008
    if env_config:
        port += 1 + env_config.env_id
        seed += 1 + env_config.env_id

    return StableBaselinesGodotEnv(env_path="envs/builds/BallChase/ball_chase_opt.x86_64", port=port, seed=seed)


def add_extra_params_func(env, parser):
    """Specify any additional command line arguments for this family of custom environments."""
    pass


def override_default_params_func(env, parser):
    """Override default argument values for this family of environments."""
    pass


def register_custom_components():
    global_env_registry().register_env(
        env_name_prefix='godot',
        make_env_func=make_godot_env_func,
        add_extra_params_func=add_extra_params_func,
        override_default_params_func=override_default_params_func,
    )


def main():
    """Script entry point."""
    register_custom_components()
    cfg = custom_parse_args()
    status = run_algorithm(cfg)
    return status


if __name__ == '__main__':
    sys.exit(main())