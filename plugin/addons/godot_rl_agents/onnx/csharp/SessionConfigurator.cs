using Godot;
using Microsoft.ML.OnnxRuntime;

namespace GodotONNX{
/// <include file='docs/SessionConfigurator.xml' path='docs/members[@name="SessionConfigurator"]/SessionConfigurator/*'/>

	public static class SessionConfigurator {

		private static SessionOptions options = new SessionOptions();
		
/// <include file='docs/SessionConfigurator.xml' path='docs/members[@name="SessionConfigurator"]/GetSessionOptions/*'/>
		public static SessionOptions GetSessionOptions() {
			options = new SessionOptions();
			options.LogSeverityLevel = OrtLoggingLevel.ORT_LOGGING_LEVEL_WARNING; 
			// see warnings
			SystemCheck();
			return options;
		}
/// <include file='docs/SessionConfigurator.xml' path='docs/members[@name="SessionConfigurator"]/SystemCheck/*'/>

static public void SystemCheck()  
	{
		//Most code for this function is verbose only, the only reason it exists is to track
		//implementation progress of the different compute APIs.

		//December 2022: CUDA is not working. 

		string OSName = OS.GetName(); //Get OS Name
		int ComputeAPIID = ComputeCheck(); //Get Compute API
		//TODO: Get CPU architecture

		//Linux can use OpenVINO (C#) on x64 and ROCm on x86 (GDNative/C++)
		//Windows can use OpenVINO (C#) on x64
		//TODO: try TensorRT instead of CUDA
		//TODO: Use OpenVINO for Intel Graphics
		
		string [] ComputeNames = {"CUDA", "DirectML/ROCm", "DirectML", "CoreML", "CPU"};
		//match OS and Compute API
		options.AppendExecutionProvider_CPU(0); // Always use CPU
		GD.Print("OS: " + OSName, " | Compute API: " + ComputeNames[ComputeAPIID]);

		switch (OSName) 
		{
		case "Windows": //Can use CUDA, DirectML
			if (ComputeAPIID == 0) 
				{
				//CUDA 
				//options.AppendExecutionProvider_CUDA(0);
				options.AppendExecutionProvider_DML(0);
					}
			else if (ComputeAPIID == 1) 
				{ 
				//DirectML
				options.AppendExecutionProvider_DML(0);
				}
			break;
		case "X11": //Can use CUDA, ROCm
			if (ComputeAPIID == 0) 
				{ 
				//CUDA
				//options.AppendExecutionProvider_CUDA(0);
				}
			if (ComputeAPIID == 1) 
				{
				//ROCm, only works on x86 
				//Research indicates that this has to be compiled as a GDNative plugin
				GD.Print("ROCm not supported yet, using CPU.");
				options.AppendExecutionProvider_CPU(0);
				}
			
			break;
		case "OSX": //Can use CoreML
			if (ComputeAPIID == 0) { //CoreML
			//TODO: Needs testing
				options.AppendExecutionProvider_CoreML(0); 
				//CoreML on ARM64, out of the box, on x64 needs .tar file from GitHub
				}
			break;
		default:
			GD.Print("OS not Supported.");
			break;
		}
	}
/// <include file='docs/SessionConfigurator.xml' path='docs/members[@name="SessionConfigurator"]/ComputeCheck/*'/>

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
