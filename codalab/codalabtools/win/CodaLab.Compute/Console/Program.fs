
open System
open System.Configuration
open System.Diagnostics
open System.Threading

open Microsoft.WindowsAzure.Storage

open CodaLab.Compute.Azure

[<EntryPoint>]
let main argv = 
    let connectionString = ConfigurationManager.AppSettings.["CodaLab.ServiceBus.ConnectionString"]
    let queueName = ConfigurationManager.AppSettings.["CodaLab.Compute.QueueName"]
    let storageConnectionString = ConfigurationManager.AppSettings.["CodaLab.Storage.ConnectionString"]
    let account = CloudStorageAccount.Parse(storageConnectionString)
    let localStorageRoot = System.IO.Path.GetTempPath()
    let worker = new Worker(connectionString, queueName, RunTask.create account localStorageRoot)
    worker.Start()
    0
