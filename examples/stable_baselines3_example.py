import argparse

from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv
from stable_baselines3 import PPO

# To download the env source and binary:
# 1.  gdrl.env_from_hub -r edbeeching/godot_rl_BallChase
# 2.  chmod +x examples/godot_rl_BallChase/bin/BallChase.x86_64


parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument(
    "--env_path",
    # default="envs/example_envs/builds/JumperHard/jumper_hard.x86_64",
    default=None,
    type=str,
    help="The Godot binary to use, do not include for in editor training",
)

parser.add_argument("--speedup", default=1, type=int, help="whether to speed up the physics in the env")

args, extras = parser.parse_known_args()


env = StableBaselinesGodotEnv(env_path=args.env_path, show_window=True, speedup=args.speedup)

model = PPO("MultiInputPolicy", env, ent_coef=0.0001, verbose=2, n_steps=32, tensorboard_log="logs/log")
model.learn(200000)

print("closing env")
env.close()
