# General tips

In this file you will find various tips for making environments / training agents with Godot-RL.

## Observations

### Normalize observations:

Using a common range for all obs values, like `-1.0` to `1.0`, when possible, can be helpful for training (the
importance of the specific range may depend on the specific algorithm architecture). A high difference in the magnitude
of individual observations could initially cause changes to the larger (magnitude) observation values to contribute more to the output of
the model than the smaller ones, which can make training more challenging.

One way to normalize a value is to the divide the value by the maximum magnitude,
e.g. `current_rotation_euler_degrees / 360.0`.

### Use relative positions:

When possible, using relative positions might reduce the amount of states that the agent has to consider, potentially
making learning faster.
For example, consider a simpler environment in which the goal is for the agent to reach a target position.

You could provide the global positions of the agent and the goal as obs (the snippet below is for a 2D case):

```gdscript
func get_obs() -> Dictionary:
	var observations : Array = [
        _player.global_position.x,
        _player.global_position.y,
        _goal.global_position.x,
        _goal.global_position.y
	]
	return {"obs": observations}
```

Or you can instead provide the position of the goal in the player's reference. Godot has a helper function that makes
that easier:

```gdscript
func get_obs() -> Dictionary:
	var goal_position_in_player_reference: Vector2 = _player.to_local(_goal.global_position)
	var observations : Array = [
		goal_position_in_player_reference.x,
		goal_position_in_player_reference.y
	]
	return {"obs": observations}
```

This reduces the amount of combinations that the agent has to consider (e.g. the state "agent is 10 pixels right from
the goal" will be true regardless of the global positions of the agent and the goal).

Note that the observations are not normalized in the above snippets. One way to normalize these obs to the `-1` to `1`
range would be, if you know the maximum possible distance, to divide the `goal_position_in_player_reference` vector by
it. If the maximum distance is very large, you might consider clamping the values to a specific range and dividing by
the maximum value within that range (e.g. `goal_position_in_player_reference.limit_length(100.0) / 100.0`), or other
normalization techniques.

## Rewards

In very simple environments, sparse rewards (e.g. `+1` when the goal position is reached, `-1` if the episode has timed
out or on other game over condition) might be sufficient, however, in more complex environments usually
a `shaping reward` is added to make the training process easier and more likely to converge.

You can **start with simple rewards**, and iteratively add more complex shaping rewards.

In the environment type mentioned above, where the goal is for the agent to reach the goal position, you could consider a couple
of approaches to the shaping reward given on every step (you could add it to the extended AIController in the `get_reward()`
method which gets called every n physics steps as set in the sync node with the `action_repeat` property - which is when the agent is reading the reward value, or assign the value of `ai_controller.reward`
from the Player node in e.g. the `_physics_processing()` method, which would assign the reward on every physics step instead, resulting in a potentially different accumulated reward value when the reward is read):

### 1 - Negative reward  based on the current distance to goal:

```gdscript
reward -= _player.global_position.distance_to(goal.global_position) / factor
```

The reward will be lower (more negative) if the agent moves away from the goal, and higher (less negative) as the agent gets closer to the goal.
As the reward will be negative at every step unless the agent is right at the goal, in more complex environments that have obstacles/walls that end the episode if hit, giving a negative reward every step could potentially cause the agent to want to finish the episode sooner by colliding with an obstacle (resulting in a higher cumulative reward as it accumulated the negative reward for less steps). The extent of this effect may depend on adjustments to the reward magnitudes, discount factor, and other training settings.

### 2 - Reward based on the delta distance to goal (moving toward or moving away):

```gdscript
var current_distance_to_goal = player.global_position.distance_to(goal.global_position)
reward += (previous_distance_to_goal - current_distance_to_goal) / factor
previous_distance_to_goal = current_distance_to_goal
```

The reward will be positive if the agent is moving toward the goal, negative if the agent is moving away from the goal, and ~0 if the agent is standing still.

### 3 - Reward only when the smallest distance to goal is reached:

```gdscript
var current_distance_to_goal = player.global_position.distance_to(goal.global_position)
if current_distance_to_goal < best_distance_to_goal:
    reward += (best_distance_to_goal - current_distance_to_goal) / factor
best_distance_to_goal = current_distance_to_goal
```

In some environments with obstacles where there isn't a clear line of sight to the goal, this type of reward may help the agent to discover better paths as it doesn't penalize moving away from the goal.