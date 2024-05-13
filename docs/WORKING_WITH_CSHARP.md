# Working with C#

While the Godot RL Agents Godot plugin currently natively supports only working with gdscript and this option is recommended, 
it is possible to use C# for your projects as well. The process is slightly more complicated, so some understanding of
how the gdscript variant of the plugin works is recommended.

We recommended completing the [custom env](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md) tutorial first using
gdscript to get an idea of the usual process first.

We have prepared a simple example that comes in 3 variants:
- [GDScript](https://github.com/edbeeching/godot_rl_agents_examples/tree/main/examples/TestExamples/SimpleReachGoal/GDScript) (The entire game is written in gdscript)
- [CSharp](https://github.com/edbeeching/godot_rl_agents_examples/tree/main/examples/TestExamples/SimpleReachGoal/CSharp) (Most of the game is written in C#, except for the extended AIController which is written in GDScript)
- [CSharpAll](https://github.com/edbeeching/godot_rl_agents_examples/tree/main/examples/TestExamples/SimpleReachGoal/CSharpAll) (The entire game is written in C#, and interfacing with the plugin is done through an AIController also  written in C#)

### CSharp

In this approach, we extend the AIController using gdscript as we cannot directly extend from it using C#, but we still write the rest of the game in C# (e.g. Player and other classes). 

You can see the [extended AIController here](https://github.com/edbeeching/godot_rl_agents_examples/blob/main/examples/TestExamples/SimpleReachGoal/CSharp/scenes/player/player_ai_controller.gd). The code is very similar to the gdscript version [extended AI Controller](https://github.com/edbeeching/godot_rl_agents_examples/blob/main/examples/TestExamples/SimpleReachGoal/GDScript/scenes/player/player_ai_controller.gd), except that we don't get code completion in gdscript for the C# classes. It is slightly more complex to access/modify the gdscript AIController properties from the C# Player class, and you can see how that is done in the [Player script](https://github.com/edbeeching/godot_rl_agents_examples/blob/main/examples/TestExamples/SimpleReachGoal/CSharp/scenes/player/Player.cs).

The main advantage of this approach is that it doesn't require any modifications to the plugin, or writing an AIController wrapper (see [CSharpAll](#csharpall) for that approach). It's also easy to access data from [sensors](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/NODE_REFERENCE.md#sensors) included in the plugin which are written in gdscript. The disadvantage is that it uses [cross-language scripting](https://docs.godotengine.org/en/stable/tutorials/scripting/cross_language_scripting.html) when interfacing between the AIController and the Player script and/or the rest of the env code written in C#.

### CSharpAll

As mentioned the _CSharpAll_ variant of this example has the entire game written in C#, aiming to provide a more 
consistent experience for C# developers. The main advantage of this approach is that interfacing with the AIController 
no longer assumes [cross-language scripting](https://docs.godotengine.org/en/stable/tutorials/scripting/cross_language_scripting.html) between C# and GDScript.

This approach is slightly more complicated to set up than the _CSharp_ variant, as it requires a custom C# wrapper for 
the `ai_controller_3d.gd` node. We provide this wrapper called `AIControllerSharp3D.cs` [here](https://github.com/edbeeching/godot_rl_agents_examples/blob/main/examples/TestExamples/SimpleReachGoal/CSharpAll/scenes/player/AIControllerSharp3D.cs),
but it should be noted that this wrapper may not be kept up to date with the GDScript version, as such it may need small
changes in the future to work.

#### Using the C# AIController

As we did in the other examples, we need to inherit from the AIController node, only now we will inherit from the 
provided C# wrapper. Upon inheriting, you will find the C# equivalent of the GDScript AIController functions that you 
need to add logic to, see this section of [custom env](https://github.com/edbeeching/godot_rl_agents/blob/main/docs/CUSTOM_ENV.md#adding-the-ai-controller) tutorial for more details.

As mentioned before, by writing the AIController in C# we eliminate [cross-language scripting](https://docs.godotengine.org/en/stable/tutorials/scripting/cross_language_scripting.html) between the 'player'
C# script and the AIController script, but this does mean that interfacing with other GDScript nodes, such as the 
sensors provided by the plugin, means a minimal cross-language scripting is still required. This example also showcases
how to inferface with these components (see [PlayerAIController.cs](https://github.com/edbeeching/godot_rl_agents_examples/blob/main/examples/TestExamples/SimpleReachGoal/CSharpAll/scenes/player/PlayerAIController.cs)).

#### Modifying the AIController 3D wrapper to 2D version

In case you want to use the 2D version of the AIController, you will need to modify the provided 
`AIControllerSharp3D.cs` in a few minor ways:
- Change the class name to `AIControllerSharp2D` and the base class to `Node2D`
```diff
- public abstract partial class AIControllerSharp3D : Node3D
+ public abstract partial class AIControllerSharp2D : Node2D
```
- Change the `_player` field to be of type `Node2D` instead of `Node3D`
```diff
- public Node3D _player;
+ public Node2D _player;
```
