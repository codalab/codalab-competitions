namespace CodaLab.Compute.Worker

open System
open System.Collections.Generic
open System.Diagnostics
open System.Linq
open System.Net
open System.Threading
open Microsoft.WindowsAzure
open Microsoft.WindowsAzure.Diagnostics
open Microsoft.WindowsAzure.ServiceRuntime
open Microsoft.WindowsAzure.Storage
open Microsoft.ServiceBus
open Microsoft.ServiceBus.Messaging

open CodaLab.Compute.Azure

type WorkerRole() =
    inherit RoleEntryPoint() 

    // Lazily create the Service Bus Queue client. The creation is delayed until the role's OnStart method is called.
    let worker = lazy (
        let queueName = CloudConfigurationManager.GetSetting("CodaLab.Compute.QueueName")
        let connectionString = CloudConfigurationManager.GetSetting("CodaLab.ServiceBus.ConnectionString")
        let storageConnectionString = CloudConfigurationManager.GetSetting("CodaLab.Storage.ConnectionString")
        let account = CloudStorageAccount.Parse(storageConnectionString)
        let localStorageRoot = RoleEnvironment.GetLocalResource("RunStorage").RootPath
        new Worker(connectionString, queueName, RunTask.create account localStorageRoot)
    )

    override wr.Run() =
        Trace.TraceInformation("Entering WorkerRole::Run RoleId={0}", RoleEnvironment.CurrentRoleInstance.Id)
        worker.Value.Start()

    override wr.OnStart() = 
        Trace.TraceInformation("Entering WorkerRole::OnStart RoleId={0}", RoleEnvironment.CurrentRoleInstance.Id)
        // Set the maximum number of concurrent connections 
        ServicePointManager.DefaultConnectionLimit <- 12
        // Create the worker.
        Trace.TraceInformation("EnvVar PATH: {0}", Environment.GetEnvironmentVariable("PATH"))
        Trace.TraceInformation("EnvVar INSTALL_PATH: {0}", Environment.GetEnvironmentVariable("INSTALL_PATH"))
        Environment.SetEnvironmentVariable("PATH", "%PATH%;D:\Python27")
        Trace.TraceInformation("EnvVar PATH: {0}", Environment.GetEnvironmentVariable("PATH"))
        worker.Force() |> ignore
        base.OnStart()

    override wr.OnStop() =
        Trace.TraceInformation("Entering WorkerRole::OnStop RoleId={0}", RoleEnvironment.CurrentRoleInstance.Id)
        worker.Value.Stop()
        base.OnStop()
