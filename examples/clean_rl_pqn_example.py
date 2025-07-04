# Original file taken from CleanRL https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/pqn.py
# and adapted to work with Godot RL Agents envs

# docs and experiment results can be found at https://docs.cleanrl.dev/rl-algorithms/pqn/#pqnpy
import os
import pathlib
import random
import time
from collections import deque
from dataclasses import dataclass

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import tyro
from torch.utils.tensorboard import SummaryWriter

from godot_rl.wrappers.clean_rl_wrapper import CleanRLGodotEnv


@dataclass
class Args:
    onnx_export_path: str = None
    """If set, will export onnx to this path after training is done"""
    env_path: str = None
    """Path to the Godot exported environment"""
    n_parallel: int = 1
    """How many instances of the environment executable to
    launch (requires --env_path to be set if > 1)."""
    viz: bool = False
    """Whether the exported Godot environment will displayed during training"""
    speedup: int = 8
    """How much to speed up the environment"""
    exp_name: str = os.path.basename(__file__)[: -len(".py")]
    """the name of this experiment"""
    seed: int = 1
    """seed of the experiment"""
    torch_deterministic: bool = True
    """if toggled, `torch.backends.cudnn.deterministic=False`"""
    cuda: bool = True
    """if toggled, cuda will be enabled by default"""
    track: bool = False
    """if toggled, this experiment will be tracked with Weights and Biases"""
    wandb_project_name: str = "cleanRL"
    """the wandb's project name"""
    wandb_entity: str = None
    """the entity (team) of wandb's project"""
    capture_video: bool = False
    """whether to capture videos of the agent performances (check out `videos` folder)"""

    # Algorithm specific arguments
    env_id: str = "CartPole-v1"
    """the id of the environment"""
    total_timesteps: int = 1_000_000
    """total timesteps of the experiments"""
    learning_rate: float = 2.5e-4
    """the learning rate of the optimizer"""
    num_envs: int = 4
    """the number of parallel game environments [note: automatically set]"""
    num_steps: int = 128
    """the number of steps to run for each environment per update"""
    num_minibatches: int = 4
    """the number of mini-batches"""
    update_epochs: int = 4
    """the K epochs to update the policy"""
    anneal_lr: bool = True
    """Toggle learning rate annealing"""
    gamma: float = 0.99
    """the discount factor gamma"""
    start_e: float = 1
    """the starting epsilon for exploration"""
    end_e: float = 0.05
    """the ending epsilon for exploration"""
    exploration_fraction: float = 0.5
    """the fraction of `total_timesteps` it takes from start_e to end_e"""
    max_grad_norm: float = 10.0
    """the maximum norm for the gradient clipping"""
    q_lambda: float = 0.65
    """the lambda for Q(lambda)"""


# def make_env(env_path):
#     def thunk():
#         env = CleanRLGodotEnv(env_path=env_path, show_window=True)
#         return env
#
#     return thunk


def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer


# ALGO LOGIC: initialize agent here:
class QNetwork(nn.Module):
    def __init__(self, envs):
        super().__init__()

        self.network = nn.Sequential(
            layer_init(nn.Linear(np.array(envs.single_observation_space.shape).prod(), 120)),
            nn.LayerNorm(120),
            nn.ReLU(),
            layer_init(nn.Linear(120, 84)),
            nn.LayerNorm(84),
            nn.ReLU(),
            layer_init(nn.Linear(84, env.single_action_space.n)),
        )

    def forward(self, x):
        return self.network(x)


def linear_schedule(start_e: float, end_e: float, duration: int, t: int):
    slope = (end_e - start_e) / duration
    return max(slope * t + start_e, end_e)


if __name__ == "__main__":
    args = tyro.cli(Args)

    # env setup
    envs = env = CleanRLGodotEnv(
        env_path=args.env_path,
        show_window=args.viz,
        speedup=args.speedup,
        seed=args.seed,
        n_parallel=args.n_parallel,
    )
    assert isinstance(envs.single_action_space, gym.spaces.Discrete), "only discrete action space is supported"

    args.num_envs = envs.num_envs
    args.batch_size = int(args.num_envs * args.num_steps)
    args.minibatch_size = int(args.batch_size // args.num_minibatches)
    args.num_iterations = args.total_timesteps // args.batch_size
    run_name = f"{args.env_id}__{args.exp_name}__{args.seed}__{int(time.time())}"
    if args.track:
        import wandb

        wandb.init(
            project=args.wandb_project_name,
            entity=args.wandb_entity,
            sync_tensorboard=True,
            config=vars(args),
            name=run_name,
            monitor_gym=True,
            save_code=True,
        )
    writer = SummaryWriter(f"runs/{run_name}")
    writer.add_text(
        "hyperparameters",
        "|param|value|\n|-|-|\n%s" % ("\n".join([f"|{key}|{value}|" for key, value in vars(args).items()])),
    )

    # TRY NOT TO MODIFY: seeding
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.backends.cudnn.deterministic = args.torch_deterministic

    device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")

    # agent setup
    q_network = QNetwork(envs).to(device)
    optimizer = optim.RAdam(q_network.parameters(), lr=args.learning_rate)

    # storage setup
    obs = torch.zeros((args.num_steps, args.num_envs) + envs.single_observation_space.shape).to(device)
    actions = torch.zeros((args.num_steps, args.num_envs) + envs.single_action_space.shape).to(device)
    rewards = torch.zeros((args.num_steps, args.num_envs)).to(device)
    dones = torch.zeros((args.num_steps, args.num_envs)).to(device)
    values = torch.zeros((args.num_steps, args.num_envs)).to(device)

    # TRY NOT TO MODIFY: start the game
    global_step = 0
    start_time = time.time()
    next_obs, _ = envs.reset(seed=args.seed)
    next_obs = torch.Tensor(next_obs).to(device)
    next_done = torch.zeros(args.num_envs).to(device)

    # episode reward stats, modified as Godot RL does not return this information in info (yet)
    episode_returns = deque(maxlen=20)
    accum_rewards = np.zeros(args.num_envs)

    for iteration in range(1, args.num_iterations + 1):
        # Annealing the rate if instructed to do so.
        if args.anneal_lr:
            frac = 1.0 - (iteration - 1.0) / args.num_iterations
            lrnow = frac * args.learning_rate
            optimizer.param_groups[0]["lr"] = lrnow

        for step in range(0, args.num_steps):
            global_step += args.num_envs
            obs[step] = next_obs
            dones[step] = next_done

            epsilon = linear_schedule(
                args.start_e, args.end_e, args.exploration_fraction * args.total_timesteps, global_step
            )
            random_actions = torch.randint(0, envs.single_action_space.n, (args.num_envs,)).to(device)
            with torch.no_grad():
                q_values = q_network(next_obs)
                max_actions = torch.argmax(q_values, dim=1)
                values[step] = q_values[torch.arange(args.num_envs), max_actions].flatten()

            explore = torch.rand((args.num_envs,)).to(device) < epsilon
            action = torch.where(explore, random_actions, max_actions)
            actions[step] = action

            # TRY NOT TO MODIFY: execute the game and log data.
            next_obs, reward, terminations, truncations, infos = envs.step(action.cpu().numpy())
            next_done = np.logical_or(terminations, truncations)
            rewards[step] = torch.tensor(reward).to(device).view(-1)
            next_obs, next_done = torch.Tensor(next_obs).to(device), torch.Tensor(next_done).to(device)

            accum_rewards += np.array(reward)

            for i, d in enumerate(next_done):
                if d:
                    episode_returns.append(accum_rewards[i])
                    accum_rewards[i] = 0

        # Compute Q(lambda) targets
        with torch.no_grad():
            returns = torch.zeros_like(rewards).to(device)
            for t in reversed(range(args.num_steps)):
                if t == args.num_steps - 1:
                    next_value, _ = torch.max(q_network(next_obs), dim=-1)
                    nextnonterminal = 1.0 - next_done
                    returns[t] = rewards[t] + args.gamma * next_value * nextnonterminal
                else:
                    nextnonterminal = 1.0 - dones[t + 1]
                    next_value = values[t + 1]
                    returns[t] = (
                        rewards[t]
                        + args.gamma
                        * (args.q_lambda * returns[t + 1] + (1 - args.q_lambda) * next_value)
                        * nextnonterminal
                    )

        # flatten the batch
        b_obs = obs.reshape((-1,) + envs.single_observation_space.shape)
        b_actions = actions.reshape((-1,) + envs.single_action_space.shape)
        b_returns = returns.reshape(-1)

        # Optimizing the Q-network
        b_inds = np.arange(args.batch_size)
        for epoch in range(args.update_epochs):
            np.random.shuffle(b_inds)
            for start in range(0, args.batch_size, args.minibatch_size):
                end = start + args.minibatch_size
                mb_inds = b_inds[start:end]

                old_val = q_network(b_obs[mb_inds]).gather(1, b_actions[mb_inds].unsqueeze(-1).long()).squeeze()
                loss = F.mse_loss(b_returns[mb_inds], old_val)

                # optimize the model
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(q_network.parameters(), args.max_grad_norm)
                optimizer.step()

        writer.add_scalar("losses/td_loss", loss, global_step)
        writer.add_scalar("losses/q_values", old_val.mean().item(), global_step)
        writer.add_scalar("charts/SPS", int(global_step / (time.time() - start_time)), global_step)
        print(f"SPS: {int(global_step / (time.time() - start_time))}, Epsilon (rand action prob): {epsilon}")
        if len(episode_returns) > 0:
            print(
                "Returns:",
                np.mean(np.array(episode_returns)),
            )
            writer.add_scalar("charts/episodic_return", np.mean(np.array(episode_returns)), global_step)

    envs.close()
    writer.close()

    if args.onnx_export_path is not None:
        path_onnx = pathlib.Path(args.onnx_export_path).with_suffix(".onnx")
        print("Exporting onnx to: " + os.path.abspath(path_onnx))

        q_network.eval().to("cpu")

        class OnnxPolicy(torch.nn.Module):
            def __init__(self, network):
                super().__init__()
                self.network = network

            def forward(self, onnx_obs, state_ins):
                network_output = self.network(onnx_obs)
                return network_output, state_ins

        onnx_policy = OnnxPolicy(q_network.network)
        dummy_input = torch.unsqueeze(torch.tensor(envs.single_observation_space.sample()), 0)

        torch.onnx.export(
            onnx_policy,
            args=(dummy_input, torch.zeros(1).float()),
            f=str(path_onnx),
            opset_version=15,
            input_names=["obs", "state_ins"],
            output_names=["output", "state_outs"],
            dynamic_axes={
                "obs": {0: "batch_size"},
                "state_ins": {0: "batch_size"},  # variable length axes
                "output": {0: "batch_size"},
                "state_outs": {0: "batch_size"},
            },
        )
