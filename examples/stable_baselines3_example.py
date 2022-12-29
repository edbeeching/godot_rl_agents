from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv
from stable_baselines3 import PPO

# To download the env source and binary:
# 1.  gdrl.env_from_hub -r edbeeching/godot_rl_BallChase
# 2.  chmod +x examples/godot_rl_BallChase/bin/BallChase.x86_64

env = StableBaselinesGodotEnv(env_path="examples/godot_rl_BallChase/bin/BallChase.x86_64", show_window=True, speedup=8)

model = PPO(
    "MultiInputPolicy",
    env,
    ent_coef=0.0001,
    verbose=2,
    n_steps=32,
    tensorboard_log="logs/log",
)
model.learn(200000)

print("closing env")
env.close()
