using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;
using System.Management;

namespace GodotONNX{
public class ONNXInference : Node
{
	private InferenceSession session;
	[Export(PropertyHint.File, "*.onnx")]
	public string modelPath;

	public override void _Ready()
	{
		var session = LoadModel(modelPath);
	}
	public InferenceSession LoadModel(string modelPath) {
		Godot.File file = new Godot.File();
		file.Open(modelPath, Godot.File.ModeFlags.Read);
		byte[] model = file.GetBuffer((int)file.GetLen());
		file.Close();
		ConfigureSession();
		
		InferenceSession NewSession = new InferenceSession(model); //Load the model
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
				//We don't do loading here, just configuration
				}
			break;
		case "X11": //Can use CUDA, ROCm, CPU
			if (ComputeAPIID == 0) {
				GD.Print("OS: Linux, Compute API: CUDA");
				//We don't do loading here, just configuration
				}
			else if (ComputeAPIID == 1) {
				GD.Print("OS: Linux, Compute API: ROCm");
				//We don't do loading here, just configuration
				}
			else if (ComputeAPIID == -1) {
				GD.Print("OS: Linux, Compute API: CPU");
				//We don't do loading here, just configuration
				}
			break;
		case "OSX": //Can use CoreML, CPU
			if (ComputeAPIID == 0) {
				GD.Print("OS: MacOS, Compute API: Metal");
				//We don't do loading here, just configuration
				}
			else if (ComputeAPIID == -1) {
				GD.Print("OS: MacOS, Compute API: CPU");
				//We don't do loading here, just configuration
				}
			break;
		}
	}
	public int ComputeCheck() {
	string adapterName = Godot.VisualServer.GetVideoAdapterName();
	//string adapterVendor = Godot.VisualServer.GetVideoAdapterVendor();
	adapterName = adapterName.ToUpper();

	if (adapterName.Contains("INTEL") == true) {
		GD.Print("Detected GPU: Intel");//Return 1, should use DirectML
		return 1;}
	else if (adapterName.Contains("AMD") == true) {
		GD.Print("Detected GPU: AMD");//Return 1, should use DirectML, check later for ROCm
		return 1;}
	else if (adapterName.Contains("NVIDIA") == true){
		GD.Print("Detected GPU: NVIDIA"); //Return 0, should use CUDA
		return 0;}
	else {
		GD.Print("Graphics Card not recognized."); //Return -1, should use CPU
		return -1;}
			}
		}
	}
