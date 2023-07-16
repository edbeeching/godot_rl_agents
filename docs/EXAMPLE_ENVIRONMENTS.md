# Example environments 
THIS DOCUMENT IS A BIT OUT OF DATE, BUT MAY BE USEFUL TO SOMEONE SO WE HAVE LEFT IT UP


This is a WIP and needs updating since the Godot 4 update.
For the current version, we provide 4 example environments, located in **envs/example_envs/**
![Alt text](all_example_envs.png?raw=true "All Environments")

## Jumper (Hard)


![Alt text](example_envs_jumper_hard.png?raw=true "The Jumper (Hard) Environment")

**Overview**: Watch you agent learn to jump from platform to platform

**Agents:** Single agent, 16 parallel versions of the environment are created per game executable

**Observation:** A vector, pointing in the direction of the next platform. A raycast-based cone of observations around the agent.

**Reward function:**
* Dense reward based on decrease in euclidean distance to next platform

* Sparse reward of 10.0 when the agent reaches the next platform
* Penalty of -10.0 when the agent falls off the platform

**Reset condition:**
* Falling off
* Reaching the episode limit of 5000 timesteps

**Action space**:
    Mixed continuous and discrete action space:
        Discrete actions: Jump or not jump
        Continous actions: Turn strength left / right, move strength forwards / backwards


### Example training:
The agent can be trained with the following command:
```
gdrl --env_path envs/builds/JumperHard/jumper_hard.x86_64 --config_file envs/configs/ppo_config_jumper_hard.yaml --experiment_name=Experiment_01
```
Training logs will be output by default to **./logs/rllib/PPO/jumper_hard/**
You can monitor training curves etc with tensorboard
```
tensorboard --logdir /PATH/TO/LOG/DIR
```
### Pretrained models:
We provide pretrained models while can be visualized with the following command:
```
gdrl --env_path envs/builds/JumperHard/jumper_hard.x86_64 --eval --restore envs/checkpoints/jumper_hard/checkpoint_000500/checkpoint-500

```


## Ball chase
![Alt text](example_envs_ball_chase.png?raw=true "The Ball Chase Environment")

**Overview**: Collect pink fruits and avoid the walls

**Agents:** Single agent, 16 parallel versions of the environment are created per game executable

**Observation:** A vector, pointing in the direction of the next pink fruit. A circle of 2D raycasts around the agent.

**Reward function:**
* Dense reward based on decrease in euclidean distance to next pink fruit
* Sparse reward of 10.0 when the fruit is collected
* Penalty of -10.0 when the agent hits a wall

**Reset condition:**
* Hitting a wall
* Reaching the episode limit of 5000 timesteps
  
**Action space**:
* Continuous action space: 2D vector indicating the move direction in x and y

### Example training:
The agent can be trained with the following command:
```
gdrl --trainer=rllib --env_path envs/builds/BallChase/ball_chase.x86_64 --config_file envs/configs/ppo_config_ball_chase.yaml --experiment_name=BallChase_01 
```
Training logs will be output by default to **./logs/rllib/PPO/ball_chase/**
You can monitor training curves etc with tensorboard
```
tensorboard --logdir /PATH/TO/LOG/DIR
```
### Pretrained models:
We provide pretrained models while can be visualized with the following command:
```
gdrl --env_path envs/builds/BallChase/ball_chase.x86_64 --eval --restore envs/checkpoints/ball_chase/checkpoint_000100/checkpoint-100

```

## Fly By
![Alt text](example_envs_fly_by.png?raw=true "The Fly By Environment")
**Overview**: Race through the environment by flying through the targets

**Agents:** Single agent, 16 parallel versions of the environment are created per game executable

**Observation:** Two vectors, pointing in the direction of the two next waypoints.

**Reward function:**
* Dense reward based on decrease in euclidean distance to waypoint
* Sparse reward of 10.0 when the waypoint is reached
* Penalty of -10.0 when the agent leaves the game area

**Reset condition:**
* Leaving the game area
* Reaching the episode limit of 5000 timesteps
  
**Action space**:
* Continuous action space: 2D vector indicating the move direction in x and y

### Example training:
The agent can be trained with the following command:
```
gdrl --trainer=rllib --env_path envs/builds/FlyBy/fly_by.x86_64 --config_file envs/configs/ppo_config_fly_by.yaml --experiment_name=FlyBy_01 
```
Training logs will be output by default to **./logs/rllib/PPO/fly_by/**
You can monitor training curves etc with tensorboard
```
tensorboard --logdir /PATH/TO/LOG/DIR
```
### Pretrained models:
We provide pretrained models while can be visualized with the following command:
```
gdrl --env_path envs/builds/FlyBy/fly_by.x86_64 --eval --restore envs/checkpoints/fly_by/checkpoint_000500/checkpoint-500

```


## Space Shooter
![Alt text](example_envs_space_shooter.png?raw=true "The Space Shooter Environment")

**Note** This environment is still a work in progress and is subject to major changes, multi-agent Deep Reinforcement Learning is challenging. We plan to include a major update in multi-agent in version 0.3 of Godot RL agents.

**Agents:** Multi-agent, two teams of 8 agents are created per game executable

**Observation:** the remaining ammo of the two guns, the relative positions and angles of the 3 nearest members of the enemy team and the player team. This observation is higher game specific and will likely change to a more general one in future versions of Godot RL agents.

**Reward function:**
* Dense reward based on decrease in euclidean distance to waypoint
* Sparse reward of 1 for each hit given to an enemy
* Sparse reward of 10.0 for each kill of an enemy
* Penalty of -10.0 when the agent dies

**Reset condition:**
* Leaving the game area
* Reaching the episode limit of 5000 timesteps
* Dying
  
**Action space**:
* Continuous action space: A scalar indicating the angle which the play should move toward and a scalar value indication the angle the player should fire towards

### Example training:
The agent can be trained with the following command:
```
gdrl --trainer=rllib --env_path envs/builds/SpaceShooter/space_shooter.x86_64 --config_file envs/configs/ppo_config_space_shooter.yaml --experiment_name=Shooter_01 
```
Training logs will be output by default to **./logs/rllib/PPO/space_shooter/**
You can monitor training curves etc with tensorboard
```
tensorboard --logdir /PATH/TO/LOG/DIR
```
### Pretrained models:
We provide pretrained models while can be visualized with the following command:
```
gdrl --env_path envs/builds/SpaceShooter/space_shooter.x86_64 --eval --restore envs/checkpoints/space_shooter/checkpoint_002000/checkpoint-2000

```
