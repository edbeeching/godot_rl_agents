using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;

namespace GodotONNX{
public class ONNXInference : Node
{
	private InferenceSession session;
	public string modelPath;
	private int batchSize;



	//init function
	public void Initialize(string Path, int BatchSize)
	{
		modelPath = Path;
		batchSize = BatchSize;
		session = LoadModel(modelPath);
	}
	public Godot.Collections.Dictionary<string, Godot.Collections.Array<float>> RunInference(Godot.Collections.Array<float> obs, int state_ins)
	{
		//Current model: Any (Godot Rl Agents)
		//Expects a tensor of shape [batch_size, input_size] type float named obs and a tensor of shape [batch_size] type float named state_ins
		
		//Fill the input tensors
		// create span from inputSize
		var span = new float[obs.Count]; //There's probably a better way to do this
		for (int i = 0; i < obs.Count; i++)
		{
			span[i] = obs[i];
		}
				
		IReadOnlyCollection<NamedOnnxValue> inputs = new List<NamedOnnxValue> 
			{
			NamedOnnxValue.CreateFromTensor("obs", new DenseTensor<float>(span, new int[] { batchSize, obs.Count })),
			NamedOnnxValue.CreateFromTensor("state_ins", new DenseTensor<float>(new float[] { state_ins }, new int[] { batchSize }))
			}; 
		IReadOnlyCollection<string> outputNames = new List<string> { "output", "state_outs" }; //ONNX is sensible to these names, as well as the input names

		IDisposableReadOnlyCollection<DisposableNamedOnnxValue> results = null;
		
		try{
			results = session.Run(inputs, outputNames);
		}
		catch (OnnxRuntimeException e) {
			//This error usually means that the model is not compatible with the input, beacause of the input shape (size)
			GD.Print("Error at inference: ", e);
			return null;
		}
		//Can't convert IEnumerable<float> to Variant, so we have to convert it to an array or something
		Godot.Collections.Dictionary<string, Godot.Collections.Array<float>> output = new Godot.Collections.Dictionary<string, Godot.Collections.Array<float>>();
		DisposableNamedOnnxValue output1 = results.First();
		DisposableNamedOnnxValue output2 = results.Last();
		Godot.Collections.Array<float> output1Array = new Godot.Collections.Array<float>();
		Godot.Collections.Array<float> output2Array = new Godot.Collections.Array<float>();

		foreach (float f in output1.AsEnumerable<float>()) {
			output1Array.Add(f);
		}

		foreach (float f in output2.AsEnumerable<float>()) {
			output2Array.Add(f);
		}

		output.Add(output1.Name, output1Array);
		output.Add(output2.Name, output2Array);
		
		//Output is a dictionary of arrays, ex: { "output" : [0.1, 0.2, 0.3, 0.4, ...], "state_outs" : [0.5, ...]}
		return output;
	}	
	public InferenceSession LoadModel(string Path) 
	{
		Godot.File file = new Godot.File();
		file.Open(Path, Godot.File.ModeFlags.Read);
		byte[] model = file.GetBuffer((int)file.GetLen());
		file.Close();
		ConfigureSession();
		return new InferenceSession(model); //Load the model
	}
	public void ConfigureSession() 
	{
		//Configure the session
		//Get OS Name
		string OSName = OS.GetName();
		//Get Compute API
		int ComputeAPIID = ComputeCheck();
		//match OS and Compute API
		switch (OSName) {
		case "Windows": //Can use CUDA, DirectML, CPU
			if (ComputeAPIID == 0) {
				GD.Print("OS: Windows, Compute API: CUDA");
				//We don't do loading here, just configuration
				}
			else if (ComputeAPIID == 1) {
				GD.Print("OS: Windows, Compute API: DirectML");
				//We don't do loading here, just configuration
				}
			else if (ComputeAPIID == -1) {
				GD.Print("OS: Windows, Compute API: CPU");
				//CPU works the same on all OSes
				}
			break;
		case "X11": //Can use CUDA, ROCm, CPU
			if (ComputeAPIID == 0) {
				GD.Print("OS: Linux, Compute API: CUDA");
				//We don't do loading here, just configuration
				}
			else if (ComputeAPIID == 1) {
				GD.Print("OS: Linux, Compute API: ROCm");
				//Research indicates that this has to be compiled as a GDNative plugin
				}
			else if (ComputeAPIID == -1) {
				GD.Print("OS: Linux, Compute API: CPU");
				//CPU works the same on all OSes
				}
			break;
		case "OSX": //Can use CoreML, CPU
			if (ComputeAPIID == 0) {
				GD.Print("OS: MacOS, Compute API: CoreML");
				//We don't do loading here, just configuration
				}
			else if (ComputeAPIID == -1) {
				GD.Print("OS: MacOS, Compute API: CPU");
				//CPU works the same on all OSes
				}
			break;
		default:
			GD.Print("OS not Supported.");
			break;
		}
	}
	public int ComputeCheck() 
	{
	string adapterName = Godot.VisualServer.GetVideoAdapterName();
	//string adapterVendor = Godot.VisualServer.GetVideoAdapterVendor();
	adapterName = adapterName.ToUpper();
	//TODO: GPU vendors for MacOS, what do they even use these days?
	if (adapterName.Contains("INTEL")) {
		GD.Print("Detected GPU: Intel");//Return 1, should use DirectML
		return 1;}
	if (adapterName.Contains("AMD")) {
		GD.Print("Detected GPU: AMD");//Return 1, should use DirectML, check later for ROCm
		return 1;}
	if (adapterName.Contains("NVIDIA")){
		GD.Print("Detected GPU: NVIDIA"); //Return 0, should use CUDA
		return 0;}
	
	GD.Print("Graphics Card not recognized."); //Return -1, should use CPU
	return -1;
			}
		}
}	
