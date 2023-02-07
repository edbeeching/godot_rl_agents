import argparse
import sys
from functools import partial
import random
import numpy as np
from gym import spaces
from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
from sample_factory.envs.env_utils import register_env
from sample_factory.train import run_rl
from sample_factory.enjoy import enjoy

from godot_rl.core.godot_env import GodotEnv
from godot_rl.core.utils import lod_to_dol


class SampleFactoryEnvWrapperBatched(GodotEnv):
    @property
    def unwrapped(self):
        return self

    @property
    def num_agents(self):
        return self.num_envs

    def reset(self, seed=None):
        obs, info = super().reset(seed=seed)
        obs = lod_to_dol(obs)
        return {k: np.array(v) for k, v in obs.items()}, info

    def step(self, action):
        obs, reward, term, trunc, info = super().step(action, order_ij=False)
        obs = lod_to_dol(obs)
        return {k: np.array(v) for k, v in obs.items()}, np.array(reward), np.array(term), np.array(trunc) * 0, info

    @staticmethod
    def to_numpy(lod):

        for d in lod:
            for k, v in d.items():
                d[k] = np.array(v)

        return lod

    def render():
        return

class SampleFactoryEnvWrapperNonBatched(GodotEnv):
    @property
    def unwrapped(self):
        return self

    @property
    def num_agents(self):
        return self.num_envs

    def reset(self, seed=None):
        obs, info = super().reset(seed=seed)
        return self.to_numpy(obs), info

    def step(self, action):
        obs, reward, term, trunc, info = super().step(action, order_ij=True)
        
        return self.to_numpy(obs), np.array(reward), np.array(term), np.array(trunc) * 0, info

    @staticmethod
    def to_numpy(lod):

        for d in lod:
            for k, v in d.items():
                d[k] = np.array(v)

        return lod

    def render():
        return


def make_godot_env_func(env_path,full_env_name, cfg=None, env_config=None, render_mode=None, speedup=1):
    seed = 0
    port = 21008 + cfg.base_port
    print("BASE PORT ", cfg.base_port)
    show_window = False
    if env_config:
        port += 1 + env_config.env_id
        seed += 1 + env_config.env_id
        print("env id", env_config.env_id)
        if cfg.viz:#
            print("creating viz env")
            show_window = env_config.env_id == 0
    if cfg.batched_sampling:
        env = SampleFactoryEnvWrapperBatched(env_path=env_path, port=port, seed=seed, show_window=show_window, speedup=speedup)
    else:
        env = SampleFactoryEnvWrapperNonBatched(env_path=env_path, port=port, seed=seed, show_window=show_window, speedup=speedup)

    return env


def register_gdrl_env(args):
    make_env = partial(make_godot_env_func, args.env_path, speedup=args.speedup)
    register_env("gdrl", make_env)


def gdrl_override_defaults(_env, parser):
    """RL params specific to Atari envs."""
    parser.set_defaults(
        # let's set this to True by default so it's consistent with how we report results for other envs
        # (i.e. VizDoom or DMLab). When running evaluations for reports or to compare with other frameworks we can
        # set this to false in command line
        summaries_use_frameskip=True,
        use_record_episode_statistics=True,
        gamma=0.99,
        env_frameskip=1,
        env_framestack=4,
        num_workers=1,
        num_envs_per_worker=2,
        worker_num_splits=2,
        env_agents=16,
        train_for_env_steps=1000000,
        nonlinearity="relu",
        kl_loss_coeff=0.0,
        use_rnn=False,
        adaptive_stddev=True,
        reward_scale=1.0,
        with_vtrace=False,
        recurrence=1,
        batch_size=2048,
        rollout=32,
        max_grad_norm=0.5,
        num_epochs=2,
        num_batches_per_epoch=4,
        ppo_clip_ratio=0.2,
        value_loss_coeff=0.5,
        exploration_loss="entropy",
        exploration_loss_coeff=0.000,
        learning_rate=0.00025,
        lr_schedule="linear_decay",
        shuffle_minibatches=False,
        gae_lambda=0.95,
        batched_sampling=False,
        normalize_input=True,
        normalize_returns=True,
        serial_mode=False,
        async_rl=True,
        experiment_summaries_interval=3,
        adam_eps=1e-5,
    )


def add_gdrl_env_args(_env, p: argparse.ArgumentParser, evaluation=False):
    if evaluation:
        # apparently env.render(mode="human") is not supported anymore and we need to specify the render mode in
        # the env ctor
        p.add_argument("--render_mode", default="human", type=str, help="")
    p.add_argument("--base_port", default=0, type=int, help="")

    p.add_argument(
        "--env_agents",
        default=2,
        type=int,
        help="Num agents in each envpool (if used)",
    )
    p.add_argument(
        "--viz",
        default=False,
        action="store_true",
        help="Whether to visualize one process",
    )


def parse_gdrl_args(argv=None, evaluation=False):
    parser, partial_cfg = parse_sf_args(argv=argv, evaluation=evaluation)
    add_gdrl_env_args(partial_cfg.env, parser, evaluation=evaluation)
    gdrl_override_defaults(partial_cfg.env, parser)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg


def sample_factory_training(args, extras):
    register_gdrl_env(args)
    cfg = parse_gdrl_args(argv=extras, evaluation=args.eval)
    cfg.base_port = random.randint(20000,22000)
    status = run_rl(cfg)
    return status

def sample_factory_enjoy(args, extras):
    register_gdrl_env(args)
    cfg = parse_gdrl_args(argv=extras, evaluation=args.eval)
    
    status = enjoy(cfg)
    return status
