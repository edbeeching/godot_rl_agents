# docs and experiment results can be found at https://docs.cleanrl.dev/rl-algorithms/ppo/#ppo_continuous_actionpy
import argparse
import os
import pathlib
import random
import time
from collections import deque
from distutils.util import strtobool

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions.normal import Normal
from torch.utils.tensorboard import SummaryWriter

from godot_rl.wrappers.clean_rl_wrapper import CleanRLGodotEnv


def parse_args():
    # fmt: off
    parser = argparse.ArgumentParser()
    parser.add_argument("--viz", action="store_true", default=False,
                        help="If set, the simulation will be displayed in a window during training. Otherwise "
                             "training will run without rendering the simulation. This setting does not apply to "
                             "in-editor training.")
    parser.add_argument("--experiment_dir", default="logs/cleanrl", type=str,
                        help="The name of the experiment directory, in which the tensorboard logs are getting stored")
    parser.add_argument("--experiment_name", default=os.path.basename(__file__).rstrip(".py"), type=str,
                        help="The name of the experiment, which will be displayed in tensorboard")
    parser.add_argument("--seed", type=int, default=1,
                        help="seed of the experiment")
    parser.add_argument("--torch-deterministic", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
                        help="if toggled, `torch.backends.cudnn.deterministic=False`")
    parser.add_argument("--cuda", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
                        help="if toggled, cuda will be enabled by default")
    parser.add_argument("--track", type=lambda x: bool(strtobool(x)), default=False, nargs="?", const=True,
                        help="if toggled, this experiment will be tracked with Weights and Biases")
    parser.add_argument("--wandb-project-name", type=str, default="cleanRL",
                        help="the wandb's project name")
    parser.add_argument("--wandb-entity", type=str, default=None,
                        help="the entity (team) of wandb's project")
    parser.add_argument("--capture-video", type=lambda x: bool(strtobool(x)), default=False, nargs="?", const=True,
                        help="whether to capture videos of the agent performances (check out `videos` folder)")
    parser.add_argument(
        "--onnx_export_path",
        default=None,
        type=str,
        help="If included, will export onnx file after training to the path specified."
    )

    # Algorithm specific arguments
    parser.add_argument("--env_path", type=str, default=None,
                        help="the path of the environment")
    parser.add_argument("--speedup", type=int, default=8,
                        help="the speedup of the godot environment")
    parser.add_argument("--total-timesteps", type=int, default=1000000,
                        help="total timesteps of the experiments")
    parser.add_argument("--learning-rate", type=float, default=3e-4,
                        help="the learning rate of the optimizer")
    parser.add_argument("--num-steps", type=int, default=32,
                        help="the number of steps to run in each environment per policy rollout")
    parser.add_argument("--anneal-lr", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
                        help="Toggle learning rate annealing for policy and value networks")
    parser.add_argument("--gamma", type=float, default=0.99,
                        help="the discount factor gamma")
    parser.add_argument("--gae-lambda", type=float, default=0.95,
                        help="the lambda for the general advantage estimation")
    parser.add_argument("--num-minibatches", type=int, default=8,
                        help="the number of mini-batches")
    parser.add_argument("--update-epochs", type=int, default=10,
                        help="the K epochs to update the policy")
    parser.add_argument("--norm-adv", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
                        help="Toggles advantages normalization")
    parser.add_argument("--clip-coef", type=float, default=0.2,
                        help="the surrogate clipping coefficient")
    parser.add_argument("--clip-vloss", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
                        help="Toggles whether or not to use a clipped loss for the value function, as per the paper.")
    parser.add_argument("--ent-coef", type=float, default=0.0001,
                        help="coefficient of the entropy")
    parser.add_argument("--vf-coef", type=float, default=0.5,
                        help="coefficient of the value function")
    parser.add_argument("--max-grad-norm", type=float, default=0.5,
                        help="the maximum norm for the gradient clipping")
    parser.add_argument("--target-kl", type=float, default=None,
                        help="the target KL divergence threshold")
    parser.add_argument("--n_parallel", default=1, type=int, help="How many instances of the environment executable to "
                                                                  "launch - requires --env_path to be set if > 1.")
    args = parser.parse_args()

    # fmt: on
    return args


def make_env(env_path, speedup):
    def thunk():
        env = CleanRLGodotEnv(env_path=env_path, show_window=True, speedup=speedup)
        return env

    return thunk


def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer


class Agent(nn.Module):
    def __init__(self, envs):
        super().__init__()
        self.critic = nn.Sequential(
            layer_init(nn.Linear(np.array(envs.single_observation_space.shape).prod(), 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 1), std=1.0),
        )
        self.actor_mean = nn.Sequential(
            layer_init(nn.Linear(np.array(envs.single_observation_space.shape).prod(), 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, np.prod(envs.single_action_space.shape)), std=0.01),
        )
        self.actor_logstd = nn.Parameter(torch.zeros(1, np.prod(envs.single_action_space.shape)))

    def get_value(self, x):
        return self.critic(x)

    def get_action_and_value(self, x, action=None):
        action_mean = self.actor_mean(x)
        action_logstd = self.actor_logstd.expand_as(action_mean)
        action_std = torch.exp(action_logstd)
        probs = Normal(action_mean, action_std)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action).sum(1), probs.entropy().sum(1), self.critic(x)


if __name__ == "__main__":
    args = parse_args()
    run_name = f"{args.experiment_name}__{args.seed}__{int(time.time())}"
    if args.track:
        import wandb

        wandb.init(
            project=args.wandb_project_name,
            entity=args.wandb_entity,
            sync_tensorboard=True,
            config=vars(args),
            name=run_name,
            # monitor_gym=True, no longer works for gymnasium
            save_code=True,
        )
    writer = SummaryWriter(f"{args.experiment_dir}/{run_name}")
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

    # env setup

    envs = env = CleanRLGodotEnv(
        env_path=args.env_path, show_window=args.viz, speedup=args.speedup, seed=args.seed, n_parallel=args.n_parallel
    )
    args.num_envs = envs.num_envs
    args.batch_size = int(args.num_envs * args.num_steps)
    args.minibatch_size = int(args.batch_size // args.num_minibatches)
    agent = Agent(envs).to(device)
    optimizer = optim.Adam(agent.parameters(), lr=args.learning_rate, eps=1e-5)

    # ALGO Logic: Storage setup
    obs = torch.zeros((args.num_steps, args.num_envs) + envs.single_observation_space.shape).to(device)
    actions = torch.zeros((args.num_steps, args.num_envs) + envs.single_action_space.shape).to(device)
    logprobs = torch.zeros((args.num_steps, args.num_envs)).to(device)
    rewards = torch.zeros((args.num_steps, args.num_envs)).to(device)
    dones = torch.zeros((args.num_steps, args.num_envs)).to(device)
    values = torch.zeros((args.num_steps, args.num_envs)).to(device)

    # TRY NOT TO MODIFY: start the game
    global_step = 0
    start_time = time.time()
    next_obs, _ = envs.reset(seed=args.seed)
    next_obs = torch.Tensor(next_obs).to(device)
    next_done = torch.zeros(args.num_envs).to(device)
    num_updates = args.total_timesteps // args.batch_size
    video_filenames = set()

    # episode reward stats, modified as Godot RL does not return this information in info (yet)
    episode_returns = deque(maxlen=20)
    accum_rewards = np.zeros(args.num_envs)

    for update in range(1, num_updates + 1):
        # Annealing the rate if instructed to do so.
        if args.anneal_lr:
            frac = 1.0 - (update - 1.0) / num_updates
            lrnow = frac * args.learning_rate
            optimizer.param_groups[0]["lr"] = lrnow

        for step in range(0, args.num_steps):
            global_step += 1 * args.num_envs
            obs[step] = next_obs
            dones[step] = next_done

            # ALGO LOGIC: action logic
            with torch.no_grad():
                action, logprob, _, value = agent.get_action_and_value(next_obs)
                values[step] = value.flatten()
            actions[step] = action
            logprobs[step] = logprob

            # TRY NOT TO MODIFY: execute the game and log data.
            next_obs, reward, terminated, truncated, infos = envs.step(action.cpu().numpy())
            done = np.logical_or(terminated, truncated)
            rewards[step] = torch.tensor(reward).to(device).view(-1)
            next_obs, next_done = torch.Tensor(next_obs).to(device), torch.Tensor(done).to(device)

            accum_rewards += np.array(reward)

            for i, d in enumerate(done):
                if d:
                    episode_returns.append(accum_rewards[i])
                    accum_rewards[i] = 0

        # bootstrap value if not done
        with torch.no_grad():
            next_value = agent.get_value(next_obs).reshape(1, -1)
            advantages = torch.zeros_like(rewards).to(device)
            lastgaelam = 0
            for t in reversed(range(args.num_steps)):
                if t == args.num_steps - 1:
                    nextnonterminal = 1.0 - next_done
                    nextvalues = next_value
                else:
                    nextnonterminal = 1.0 - dones[t + 1]
                    nextvalues = values[t + 1]
                delta = rewards[t] + args.gamma * nextvalues * nextnonterminal - values[t]
                advantages[t] = lastgaelam = delta + args.gamma * args.gae_lambda * nextnonterminal * lastgaelam
            returns = advantages + values

        # flatten the batch
        b_obs = obs.reshape((-1,) + envs.single_observation_space.shape)
        b_logprobs = logprobs.reshape(-1)
        b_actions = actions.reshape((-1,) + envs.single_action_space.shape)
        b_advantages = advantages.reshape(-1)
        b_returns = returns.reshape(-1)
        b_values = values.reshape(-1)

        # Optimizing the policy and value network
        b_inds = np.arange(args.batch_size)
        clipfracs = []
        for epoch in range(args.update_epochs):
            np.random.shuffle(b_inds)
            for start in range(0, args.batch_size, args.minibatch_size):
                end = start + args.minibatch_size
                mb_inds = b_inds[start:end]

                _, newlogprob, entropy, newvalue = agent.get_action_and_value(b_obs[mb_inds], b_actions[mb_inds])
                logratio = newlogprob - b_logprobs[mb_inds]
                ratio = logratio.exp()

                with torch.no_grad():
                    # calculate approx_kl http://joschu.net/blog/kl-approx.html
                    old_approx_kl = (-logratio).mean()
                    approx_kl = ((ratio - 1) - logratio).mean()
                    clipfracs += [((ratio - 1.0).abs() > args.clip_coef).float().mean().item()]

                mb_advantages = b_advantages[mb_inds]
                if args.norm_adv:
                    mb_advantages = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)

                # Policy loss
                pg_loss1 = -mb_advantages * ratio
                pg_loss2 = -mb_advantages * torch.clamp(ratio, 1 - args.clip_coef, 1 + args.clip_coef)
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                newvalue = newvalue.view(-1)
                if args.clip_vloss:
                    v_loss_unclipped = (newvalue - b_returns[mb_inds]) ** 2
                    v_clipped = b_values[mb_inds] + torch.clamp(
                        newvalue - b_values[mb_inds],
                        -args.clip_coef,
                        args.clip_coef,
                    )
                    v_loss_clipped = (v_clipped - b_returns[mb_inds]) ** 2
                    v_loss_max = torch.max(v_loss_unclipped, v_loss_clipped)
                    v_loss = 0.5 * v_loss_max.mean()
                else:
                    v_loss = 0.5 * ((newvalue - b_returns[mb_inds]) ** 2).mean()

                entropy_loss = entropy.mean()
                loss = pg_loss - args.ent_coef * entropy_loss + v_loss * args.vf_coef

                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(agent.parameters(), args.max_grad_norm)
                optimizer.step()

            if args.target_kl is not None:
                if approx_kl > args.target_kl:
                    break

        y_pred, y_true = b_values.cpu().numpy(), b_returns.cpu().numpy()
        var_y = np.var(y_true)
        explained_var = np.nan if var_y == 0 else 1 - np.var(y_true - y_pred) / var_y

        # TRY NOT TO MODIFY: record rewards for plotting purposes
        writer.add_scalar("charts/learning_rate", optimizer.param_groups[0]["lr"], global_step)
        writer.add_scalar("losses/value_loss", v_loss.item(), global_step)
        writer.add_scalar("losses/policy_loss", pg_loss.item(), global_step)
        writer.add_scalar("losses/entropy", entropy_loss.item(), global_step)
        writer.add_scalar("losses/old_approx_kl", old_approx_kl.item(), global_step)
        writer.add_scalar("losses/approx_kl", approx_kl.item(), global_step)
        writer.add_scalar("losses/clipfrac", np.mean(clipfracs), global_step)
        writer.add_scalar("losses/explained_variance", explained_var, global_step)
        if len(episode_returns) > 0:
            print("SPS:", int(global_step / (time.time() - start_time)), "Returns:", np.mean(np.array(episode_returns)))
            writer.add_scalar("charts/SPS", int(global_step / (time.time() - start_time)), global_step)
            writer.add_scalar("charts/episodic_return", np.mean(np.array(episode_returns)), global_step)

    envs.close()
    writer.close()

    if args.onnx_export_path is not None:
        path_onnx = pathlib.Path(args.onnx_export_path).with_suffix(".onnx")
        print("Exporting onnx to: " + os.path.abspath(path_onnx))

        agent.eval().to("cpu")

        class OnnxPolicy(torch.nn.Module):
            def __init__(self, actor_mean):
                super().__init__()
                self.actor_mean = actor_mean

            def forward(self, obs, state_ins):
                action_mean = self.actor_mean(obs)
                return action_mean, state_ins

        onnx_policy = OnnxPolicy(agent.actor_mean)
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
