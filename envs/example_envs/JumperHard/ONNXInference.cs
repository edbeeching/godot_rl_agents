using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;
using System.Management;

namespace GodotONNX;
public class ONNXInference : Node
{
	private InferenceSession session;
	[Export(PropertyHint.File, "*.onnx")]
	public string modelPath;

	public override void _Ready()
	{
		var session = LoadModel(modelPath);
		Run();
	}
	public void Run(Godot inputs){
		IDisposableReadOnlyCollection<DisposableNamedOnnxValue> results = session.Run(inputs);
		IEnumerable<float> output = results.First().AsEnumerable<float>();
		GD.Print(results.ToString());
	}	
	public InferenceSession LoadModel(string Path) {
		Godot.File file = new Godot.File();
		file.Open(Path, Godot.File.ModeFlags.Read);
		byte[] model = file.GetBuffer((int)file.GetLen());
		file.Close();
		ConfigureSession();
		
		InferenceSession NewSession = new(model); //Load the model
		return NewSession;
	}
	public void ConfigureSession() {
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
	public int ComputeCheck() {
	string adapterName = Godot.VisualServer.GetVideoAdapterName();
	//string adapterVendor = Godot.VisualServer.GetVideoAdapterVendor();
	adapterName = adapterName.ToUpper();
	//TODO: GPU vendors for MacOS, what do they even use these days?
	if (adapterName.Contains("INTEL")) {
		GD.Print("Detected GPU: Intel");//Return 1, should use DirectML
		return 1;}
	else if (adapterName.Contains("AMD")) {
		GD.Print("Detected GPU: AMD");//Return 1, should use DirectML, check later for ROCm
		return 1;}
	else if (adapterName.Contains("NVIDIA")){
		GD.Print("Detected GPU: NVIDIA"); //Return 0, should use CUDA
		return 0;}
	
	GD.Print("Graphics Card not recognized."); //Return -1, should use CPU
	return -1;
			}
		}
	
