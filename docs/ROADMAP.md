### Godot RL Agents Project RoadMap
THIS DOCUMENT IS A BIT OUT OF DATE, BUT MAY BE USEFUL TO SOMEONE SO WE HAVE LEFT IT UP

This document provides non-exaustive list of features the will be implemented in future versions of Godot RL Agents

## Version 0.1 (beta release)

- [x] 4 Example games
  - [x] Ball Chase (2D)
  - [x] SpaceShooter (2D)
  - [x] Jumper (3D)
  - [x] Flyer (3D)
- [x] Polish of example games
  - [x] Ball Chase (2D)
  - [x] SpaceShooter (2D)
  - [x] Jumper (3D) (needs animated robot)
  - [x] Flyer (3D) (could add foliage)
- [x] Training with Ray RLLib
- [x] Training with Stable baselines 3
- [x] Command line interface for training
- [x] Benchmarking environments
- [x] Testing with pytest
  - [ ] Testing of wrappers
    - [ ] Stable baselines
    - [x] Ray
    - [ ] GYM (vec env)
  - [ ] Simple test envs: 
    - [x] Identity learning
    - [ ] bandits, etc

- [x] Discrete, continuous and combinations of the two
- [x] Automatic port choice with CLA
- [x] Examples instructions
- [x] Installation instuctions
- [x] Compiled envs at higher framerates
- [x] Benchmarking of env interaction speed
- [x] Godot RL Agents Plugin
- [x] semi automatic naming of runs
- [x] trailer

## Version 0.2
- [x] Continuous integration with Travis
- [x] Extend the 2D and 3D sensor plugins
- [x] Headless training (for clusters)
- [x] Add "call" functionality to call Godot methods from python
## Version 0.3
- [ ] C# implementations of sync GDScript code
- [x] Camera observations, CNN for training
## Version 0.4
- [x] Godot 4 support
- [x] CI with github actions
- [x] Accelerated physics
- [x] Multi-agent
- [x] An additional game (racing and FPS)
- [x] Sample Factory support
- [x] Memory-based agents
## Version 0.5
- [ ] Load trained model inside Godot Engine for inference (C# lib for torch)
- [ ] CI test on windows
- [ ] Docker file (for clusters)
- [ ] Variable sized observations (Attention over)
## Version 0.6
## Version 0.7





