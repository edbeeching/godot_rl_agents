import sys
import numpy as np
from gym import spaces
from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
from sample_factory.envs.env_utils import register_env
from sample_factory.train import run_rl
from godot_rl_agents.core.godot_env import GodotEnv
import argparse



class SampleFactoryEnvWrapper(GodotEnv):

    # def __init__(
    #     self,
    #     env_path=None,
    #     port=11008,
    #     show_window=False,
    #     seed=0,
    #     framerate=None,
    #     action_repeat=None,
    # ):
    #     super(SampleFactoryEnvWrapper).__init__(
    #         self,
    #         env_path=env_path,
    #         port=port,
    #         show_window=show_window,
    #         seed=seed,
    #         framerate=framerate,
    #         action_repeat=action_repeat,
    #     )


    @property
    def unwrapped(self):
        return self

    @property 
    def num_agents(self):
        return self.num_envs

    def reset(self, seed=None):
        obs, info = super().reset(seed=seed)
        obs = self.lod_to_dol(obs)
        return {k:np.array(v) for k,v in obs.items()}, info
    
    def step(self, action):
        obs, reward, term, trunc, info = super().step(action)
        obs = self.lod_to_dol(obs)
        return {k:np.array(v) for k,v in obs.items()}, np.array(reward), np.array(term), np.array(trunc), info  


    @staticmethod
    def lod_to_dol(lod):
        return {k: [dic[k] for dic in lod] for k in lod[0]}

    @staticmethod
    def dol_to_lod(dol):
        return [dict(zip(dol,t)) for t in zip(*dol.values())] 

    @staticmethod
    def to_numpy(lod):
        
        for d in lod:
            for k,v in d.items():
                d[k] = np.array(v)

        return lod


def make_godot_env_func(full_env_name, cfg=None, env_config=None,  render_mode = None):
    seed = 0
    port = 21008
    if env_config:
        port += 1 + env_config.env_id
        seed += 1 + env_config.env_id

    env = SampleFactoryEnvWrapper(env_path=None, port=port, seed=seed)
    
    return env


def register_gdrl_env():
    register_env("gdrl", make_godot_env_func)


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
        num_workers=1,
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



def parse_gdrl_args(argv=None, evaluation=False):
    parser, partial_cfg = parse_sf_args(argv=argv, evaluation=evaluation)
    add_gdrl_env_args(partial_cfg.env, parser, evaluation=evaluation)
    gdrl_override_defaults(partial_cfg.env, parser)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg

def sample_factory_training(args, extras):
    print(args, extras)
    register_gdrl_env()
    cfg = parse_gdrl_args(argv=extras, evaluation=args.eval)

    status = run_rl(cfg)
    return status


if __name__ == "__main__":


    env = SampleFactoryEnvWrapper()
    obs, info = env.reset()


    print(env)