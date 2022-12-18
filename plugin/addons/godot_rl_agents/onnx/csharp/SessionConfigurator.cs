using Godot;
using Microsoft.ML.OnnxRuntime;

namespace GodotONNX{

	public static class SessionConfigurator {
		private static SessionOptions options = new SessionOptions();
		
		public static SessionOptions GetSessionOptions() {
			options = new SessionOptions();
			SystemCheck();
		
			return options;
		}

static public int SystemCheck()  //-1 CPU, 0 GPU, 1 DirectML, 2 CoreML
	{
		//Most code for this function is verbose only, the only reason it exists is to track
		//the implementation progress of the various compute APIs.
		//Get OS Name
		string OSName = OS.GetName();
		//Get Compute API
		int ComputeAPIID = ComputeCheck();
		//TODO: Get CPU architecture
		//
		//Linux can use OpenVINO (C#) on x64 and ROCm on x86 (GDNative/C++)
		string [] ComputeNames = {"CUDA", "DirectML/ROCm", "DirectML", "CoreML", "CPU"};
		//match OS and Compute API
		options.AppendExecutionProvider_CPU(0);
		GD.Print("OS: " + OSName, "Compute API: " + ComputeAPIID);
		if (ComputeAPIID == -1) return -1;

		switch (OSName) {
		case "Windows": //Can use CUDA, DirectML, CPU
			if (ComputeAPIID == 0) { //CUDA
				options.AppendExecutionProvider_CUDA(0);
					}
			else if (ComputeAPIID == 1) { //DirectML
				options.AppendExecutionProvider_DML(0);
				}
			break;
		case "X11": //Can use CUDA, ROCm
			if (ComputeAPIID == 0) { //CUDA
				options.AppendExecutionProvider_CUDA(0);
				}
			if (ComputeAPIID == 1) { //ROCm, only works on x86 
				//Research indicates that this has to be compiled as a GDNative plugin
				GD.Print("ROCm not supported yet, using CPU.");
				options.AppendExecutionProvider_CPU(0);
				return -1;
				}
			
			break;
		case "OSX": //Can use CoreML
			if (ComputeAPIID == 0) { //CoreML
				options.AppendExecutionProvider_CoreML(0);
				return 2;
				}
			break;
		default:
			GD.Print("OS not Supported.");
			break;
		}
		return -1;
	}
	public static int ComputeCheck() 
	{
	string adapterName = Godot.VisualServer.GetVideoAdapterName();
	//string adapterVendor = Godot.VisualServer.GetVideoAdapterVendor();
	adapterName = adapterName.ToUpper(new System.Globalization.CultureInfo(""));
	//TODO: GPU vendors for MacOS, what do they even use these days?
	if (adapterName.Contains("INTEL")) {
		//Return 2, should use DirectML only
		return 2;}
	if (adapterName.Contains("AMD")) {
		//Return 1, should use DirectML, check later for ROCm
		return 1;}
	if (adapterName.Contains("NVIDIA")){
		//Return 0, should use CUDA
		return 0;}
	
	GD.Print("Graphics Card not recognized."); //Return -1, should use CPU
	return -1;
			}
		}
}	
