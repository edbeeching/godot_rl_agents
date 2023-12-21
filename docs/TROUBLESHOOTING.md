# Troubleshooting
This page will describe some common issues and solutions.

### Onnx inference error:

**Issue:** 
When I try to start onnx inference in Godot editor, I get `Invalid Call. Nonexistent function 'new' in base 'CSharpScript'`:

![onnx_inference_error_image](https://github.com/edbeeching/godot_rl_agents/assets/61947090/6ec96d99-423e-42cb-939d-357f0cee1064)

**Solution:**
Check that you have a .csproj file in the Godot project folder named the same as the Godot project name (e.g. `GodotGame.csproj`). If not, create one.
Also check that you have a Godot version with .mono/net installed. The content of the .csproj file should be the same as the file from the [plugin](https://github.com/edbeeching/godot_rl_agents_plugin/blob/main/Godot%20RL%20Agents.csproj). If you're using additional nuget packages, you may need to include them in the file as well.

You can also make the file from Godot (check image below), just remember to add the content from the plugin file linked above into the newly created .csproj file.

![godot_build_solution_image](https://github.com/edbeeching/godot_rl_agents/assets/61947090/a016f401-2896-473b-8149-2a986c055eee)
