namespace CodaLab.Compute

open System
open System.Collections.Generic
open System.Diagnostics
open System.IO
open System.IO.Compression
open System.Net
open System.Runtime.Serialization
open System.Text

open CodaLab.Compute.Utilities
open CodaLab.Bundles

module Run =

    // Helper to write a line to multiple TextWriter instances.
    type internal TextWriterBroadcaster(writers:TextWriter list) =
        member this.WriteLine(fmt, [<ParamArray>] value: Object[]) =
            for writer in writers do writer.WriteLine(fmt, value)

    let private MaxDepth = 3

    let rec private getSubBundles (bundle:Bundle) (svc:BundleService) depth =
        if (depth > 0) then
            let bundleInfo = bundle.ReadMetadata()
            let children = bundleInfo.References()
            for (childPath, childRef) in children do
                let fullPath = Path.Combine(bundle.AbsolutePath, childPath)
                let childBundle = svc.GetInto childRef fullPath
                getSubBundles childBundle svc (depth-1)

    let executeIt (bundleSvc:BundleService) (runId:string) (diag:RunDiagnostic) = 
        try
            Trace.TraceInformation("{0}: evaluation setup begins.", System.DateTime.UtcNow)
            let bundle = bundleSvc.Get runId
            let bundleInfo = bundle.ReadMetadata()
            // Setup stdout/stderr directed at the end-user.
            use stdout = diag.StdoutWriter bundle
            use stderr = diag.StderrWriter bundle
            let writerOut = new TextWriterBroadcaster([Console.Out; stdout])
            let writerErr = new TextWriterBroadcaster([Console.Error; stderr])
            // Stage program data
            let programPath = Path.Combine(bundle.AbsolutePath, "program")
            Trace.TraceInformation("Ready to stage program into {0}", programPath)
            let programBundleUri = bundleInfo.Program
            if String.IsNullOrWhiteSpace programBundleUri then failwith "Program location is not specified."
            let programBundle = bundleSvc.GetInto programBundleUri programPath
            let programBundleInfo = programBundle.ReadMetadata()
            let programCommand = programBundleInfo.Command
            if String.IsNullOrWhiteSpace programCommand then
                writerErr.WriteLine("No program specified: command keyword is missing from bundle metadata.")
                failwith "Program command is not specified."
            getSubBundles programBundle bundleSvc MaxDepth
            // Stage input data            
            let inputPath = Path.Combine(bundle.AbsolutePath, "input")
            Trace.TraceInformation("Ready to stage input into {0}", inputPath)
            let inputBundleUri = bundleInfo.Input
            if String.IsNullOrWhiteSpace inputBundleUri then failwith "Input location is not specified."
            let inputBundle = bundleSvc.GetInto inputBundleUri inputPath
            getSubBundles inputBundle bundleSvc MaxDepth
            writerOut.WriteLine("Files staged for execution:")
            // Stage output folder
            let outputFolder = Path.Combine(bundle.AbsolutePath, "output")
            if not(Directory.Exists(outputFolder)) then Directory.CreateDirectory(outputFolder) |> ignore
            // Stage temp folder
            let tempFolder = Path.Combine(bundle.AbsolutePath, "temp")
            if not(Directory.Exists(tempFolder)) then Directory.CreateDirectory(tempFolder) |> ignore
            // Report the list of folders and files staged
            writerOut.WriteLine("")
            writerOut.WriteLine("Files staged for execution:")
            let leftTrimLength = bundle.AbsolutePath.Length
            Directory.EnumerateDirectoriesAndFiles bundle.AbsolutePath
            |> Seq.iter (fun (_, p) -> if p.Length > leftTrimLength then writerOut.WriteLine(" {0}", p.Substring(leftTrimLength+1)))
            writerOut.WriteLine("")
            // Invoke custom evaluation program
            let progCmd = programCommand.Replace("$program", @"..\program")
                                        .Replace("$input", @"..\input")
                                        .Replace("$output", @"..\output")
                                        .Replace("$tmp", @".").Trim()
            let progExe, progArgs = 
                let i = progCmd.IndexOf(" ")
                if i > 1 then progCmd.Substring(0, i).Trim(), progCmd.Substring(i, progCmd.Length-i).Trim() 
                else progCmd, String.Empty
            writerOut.WriteLine("Invoking custom program: {0}", progCmd)
            let procInfo = new ProcessStartInfo()
            procInfo.FileName <- progExe
            procInfo.Arguments <- progArgs
            procInfo.WorkingDirectory <- tempFolder
            procInfo.WindowStyle <- ProcessWindowStyle.Hidden
            procInfo.UseShellExecute <- false
            procInfo.RedirectStandardOutput <- true
            procInfo.RedirectStandardError <- true
            let p = Process.Start(procInfo)
            p.OutputDataReceived.Add(fun dre -> if not(IsNull(dre.Data)) then writerOut.WriteLine(dre.Data))
            p.ErrorDataReceived.Add(fun dre -> if not(IsNull(dre.Data)) then writerErr.WriteLine(dre.Data))
            p.BeginOutputReadLine()
            p.BeginErrorReadLine()
            p.WaitForExit()
            // Report the list of generated output files
            writerOut.WriteLine("")
            writerOut.WriteLine("Files generated in output folder during execution:")
            Directory.EnumerateDirectoriesAndFiles outputFolder
            |> Seq.iter (fun (_, p) -> if p.Length > outputFolder.Length then writerOut.WriteLine(" {0}", p.Substring(outputFolder.Length+1)))
            writerOut.WriteLine("")
            // Pack results
            Trace.TraceInformation("Packing results...")
            let outputId = sprintf "%s/output.zip" (runId.Substring(0, runId.Length - Path.GetExtension(runId).Length))
            bundleSvc.Put outputId outputFolder
            if p.ExitCode > 0 then
                raise(new Exception(String.Format("Evaluation completed with non-zero exit code (exit code = {0}).", p.ExitCode)))
        with | ex ->
            Trace.TraceError("{0}: evaluation failed\n   {1}\n{2}", System.DateTime.UtcNow, ex.Message, ex.StackTrace)
            raise(new Exception("Evaluation failed", ex))

