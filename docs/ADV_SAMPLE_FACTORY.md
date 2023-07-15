# Advanced usage with Sample-factory

Sample Factory is one of the fastest RL libraries focused on very efficient synchronous and asynchronous implementations of policy gradients (PPO).

Sample Factory is thoroughly tested, used by many researchers and practitioners, and is actively maintained. Our implementation is known to reach SOTA performance in a variety of domains while minimizing RL experiment training time and hardware requirements.

Find out more on their website: www.samplefactory.dev

## Key features

- Highly optimized algorithm [architecture](https://www.samplefactory.dev/06-architecture/overview/) for maximum learning throughput
- [Synchronous and asynchronous](https://www.samplefactory.dev/07-advanced-topics/sync-async/) training regimes
- [Serial (single-process) mode](https://www.samplefactory.dev/07-advanced-topics/serial-mode/) for easy debugging
- Optimal performance in both CPU-based and [GPU-accelerated environments](https://www.samplefactory.dev/09-environment-integrations/isaacgym/)
- Single- & multi-agent training, self-play, supports [training multiple policies](https://www.samplefactory.dev/07-advanced-topics/multi-policy-training/) at once on one or many GPUs
- Population-Based Training ([PBT](https://www.samplefactory.dev/07-advanced-topics/pbt/))
- Discrete, continuous, hybrid action spaces
- Vector-based, image-based, dictionary observation spaces
- Automatically creates a model architecture by parsing action/observation space specification. Supports [custom model architectures](https://www.samplefactory.dev/03-customization/custom-models/)
- Library is designed to be imported into other projects, [custom environments](https://www.samplefactory.dev/03-customization/custom-environments/) are first-class citizens
- Detailed [WandB and Tensorboard summaries](https://www.samplefactory.dev/05-monitoring/metrics-reference/), [custom metrics](https://www.samplefactory.dev/05-monitoring/custom-metrics/)
- [HuggingFace 🤗 integration](https://www.samplefactory.dev/10-huggingface/huggingface/) (upload trained models and metrics to the Hub)
- [Multiple](https://www.samplefactory.dev/09-environment-integrations/mujoco/) [example](https://www.samplefactory.dev/09-environment-integrations/atari/) [environment](https://www.samplefactory.dev/09-environment-integrations/vizdoom/) [integrations](https://www.samplefactory.dev/09-environment-integrations/dmlab/) with tuned parameters and trained models

## Installation

```bash
# remove sb3 installation with pip uninstall godot-rl[sb3]
pip install godot-rl[sf]
```

## Basic Environment Usage

Usage instructions for envs **BallChase**, **FlyBy** and **JumperHard.**

**Note:** for windows / mac you will need to replace the .x86_64 file suffix

- Download the env:

```bash
gdrl.env_from_hub -r edbeeching/godot_rl_<ENV_NAME>
chmod +x examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 # linux example
```

• Train a model from scratch:

```bash
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 --num_workers=10 --experiment_name=BallChase --viz  --speedup=8 --batched_sampling=True
```

• Download a pretrained checkpoint from the HF hub:

```bash
python -m sample_factory.huggingface.load_from_hub -r edbeeching/sample_factory_<ENV_NAME>
```

• Visualize a trained model:

```bash
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_<ENV_NAME>/bin/<ENV_NAME>.x86_64 --num_workers=1 --experiment_name=<ENV_NAME> --viz --eval --batched_sampling=True --speedup=8 --push_to_hub --hf_repository=<HF_USERNAME>/sample_factory_<ENV_NAME>
```

## Advanced Environment Usage

### Usage instructions for env **Racer.**

• Download the env:

```bash
gdrl.env_from_hub -r edbeeching/godot_rl_Racer
chmod +x examples/godot_rl_Racer/bin/Racer.x86_64 # linux example
```

• Train a model from scratch:

```bash
gdrl--trainer=sf --env=gdrl --env_path=examples/godot_rl_Racer/bin/Racer.x86_64 --train_for_env_steps=10000000 --experiment_name=Racer --reward_scale=0.01 --worker_num_splits=2 --num_envs_per_worker=2 --num_workers=40 --speedup=8 --batched_sampling=True --batch_size=2048 --num_batches_per_epoch=2 --num_epochs=2  --learning_rate=0.0001 --exploration_loss_coef=0.0001 --lr_schedule=kl_adaptive_epoch --lr_schedule_kl_threshold=0.04 --use_rnn=True --recurrence=32
```

• Download a pretrained checkpoint from the HF hub:

```bash
python -m sample_factory.huggingface.load_from_hub -r edbeeching/sample_factory_Racer
```

• Visualize a trained model:

```bash
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_Racer/bin/Racer.x86_64 --num_workers=1 --experiment_name=Racer --viz --eval --batched_sampling=True --speedup=8 --push_to_hub --hf_repository=edbeeching/sample_factory_Racer
```

### Usage instructions for env **MultiAgent FPS**

• Download the env:

```bash
gdrl.env_from_hub -r edbeeching/godot_rl_FPS
chmod +x examples/godot_rl_FPS/bin/FPS.x86_64 # linux example
```

• Train a model from scratch:

```bash
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_FPS/bin/FPS.x86_64 --num_workers=10 --experiment_name=FPS --viz --batched_sampling=True --speedup=8 --num_workers=80 --batched_sampling=False --num_policies=4 --with_pbt=True --pbt_period_env_steps=1000000 --pbt_start_mutation=1000000 --batch_size=2048 --num_batches_per_epoch=2 --num_epochs=2 --learning_rate=0.00005 --exploration_loss_coef=0.001 --lr_schedule=kl_adaptive_epoch --lr_schedule_kl_threshold=0.08 --use_rnn=True --recurrence=32
```

• Download a pretrained checkpoint from the HF hub:

```bash
python -m sample_factory.huggingface.load_from_hub -r edbeeching/sample_factory_FPS
```

• Visualize a trained model:

```bash
gdrl --trainer=sf --env=gdrl --env_path=examples/godot_rl_FPS/bin/FPS.x86_64 --num_workers=1 --experiment_name=FPS --viz --eval --batched_sampling=True --speedup=8 --push_to_hub --hf_repository=edbeeching/sample_factory_FPS
```

## Training on a cluster

The above training commands should all work on a headless cluster, just remove the `--viz` flag.
