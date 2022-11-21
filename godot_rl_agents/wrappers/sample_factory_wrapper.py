import sys

from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
from sample_factory.envs.env_utils import register_env
from sample_factory.train import run_rl

import argparse



def register_env():
    register_env("gdrl", )

def make_env_fn():
    pass


def gdrl_override_defaults(_env, parser):
    """RL params specific to Atari envs."""
    parser.set_defaults(
        # let's set this to True by default so it's consistent with how we report results for other envs
        # (i.e. VizDoom or DMLab). When running evaluations for reports or to compare with other frameworks we can
        # set this to false in command line
        summaries_use_frameskip=True,
        use_record_episode_statistics=True,
        gamma=0.99,
        env_frameskip=4,
        env_framestack=4,
        exploration_loss_coeff=0.01,
        num_workers=4,
        num_envs_per_worker=1,
        worker_num_splits=1,
        env_agents=64,
        train_for_env_steps=10000000,
        nonlinearity="relu",
        kl_loss_coeff=0.0,
        use_rnn=False,
        adaptive_stddev=False,
        reward_scale=1.0,
        with_vtrace=False,
        recurrence=1,
        batch_size=256,
        rollout=128,
        max_grad_norm=0.5,
        num_epochs=4,
        num_batches_per_epoch=4,
        ppo_clip_ratio=0.1,
        value_loss_coeff=0.5,
        exploration_loss="entropy",
        learning_rate=0.00025,
        lr_schedule="linear_decay",
        shuffle_minibatches=False,
        gae_lambda=0.95,
        batched_sampling=True,
        normalize_input=False,
        normalize_returns=False,
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

    p.add_argument(
        "--env_agents",
        default=2,
        type=int,
        help="Num agents in each envpool (if used)",
    )

def sample_factory_training(gdrl_args):
    cfg = parse_gdrl_args()

    status = run_rl(cfg)
    return status
