namespace CodaLab.Compute.Azure

open System
open System.Diagnostics
open System.IO
open System.Linq
open System.Runtime.Serialization
open System.Runtime.Serialization.Json
open System.Text
open System.Threading

open Microsoft.ServiceBus
open Microsoft.ServiceBus.Messaging
open Microsoft.WindowsAzure
open Microsoft.WindowsAzure.Storage
open Microsoft.WindowsAzure.Storage.Auth
open Microsoft.WindowsAzure.Storage.Blob

open CodaLab.Bundles
open CodaLab.Compute.Run

/// Messages processed by the internal agent of CloudBlockBlobWriter.
type internal CloudBlockBlobWriterAgentMessage = | Append of string | Flush of AsyncReplyChannel<unit>

/// <summary>Provides a means of persisting a stream of text to an Azure blob.</summary>
/// <param name="blob">Reference to the CloudBlockBlob instance.</param>
/// <param name="maxMillisecondsBetweenFlush">Duration in milliseconds between writes to the blob.</param>
/// <param name="maxBufferLength">Maximum length for the string buffer.</param>
/// <remarks><p>This class will buffer text supplied through its WriteLine method. Text will
/// be persisted to the blob when the buffer reaches a critical length or when the time to
/// the last write exceeds a critical threshold. Writing regularly to the blob ensures that
/// the text written through the writer becomes available in a timely manner to clients reading 
/// the blob. </p>
/// <p>The implementation uses the fact that a CloudBlockBlob is a list of blocks. Each write adds
/// a block to the list. A block has a maximum size of 4MB. The current implementation should be
/// improved to write multiple blocks when the buffer size exceeds 4MB. Other improvements should
/// include: better/custom logic to ensure timely writes to storage; ensuring that a "bad" buffer
/// length is not used.</p></remarks>
type CloudBlockBlobWriter(blob:CloudBlockBlob, maxMillisecondsBetweenFlush, maxBufferLength) =
    inherit TextWriter() 

    /// Caches text until it is written to the blob.
    let buffer = new StringBuilder(1 * maxBufferLength)

    /// Write buffer to the blob.
    let writeToBlob() = async {
        if buffer.Length > 0 then
            let data = Encoding.Default.GetBytes(buffer.ToString())
            if (data.Length >= 4 * 1024 * 1024) then failwith "Maximum block size exceeded."
            let blockIds = try blob.DownloadBlockList() 
                               |> Seq.filter(fun bi -> bi.Committed) 
                               |> Seq.map (fun bi -> bi.Name)
                               |> Seq.toList
                           with | :? StorageException as ex -> match ex.RequestInformation.HttpStatusCode with | 404 -> [] | _ -> raise ex
            let newBlockId = Convert.ToBase64String(Encoding.UTF8.GetBytes(sprintf "%6d" blockIds.Length));
            blob.PutBlock(newBlockId, new MemoryStream(data), String.Empty)
            blob.PutBlockList(blockIds @ [newBlockId])
            buffer.Clear() |> ignore }

    let millisecondsSinceLastSave (lastSavedAt:DateTime) = int (max 0.0 (DateTime.Now - lastSavedAt).TotalMilliseconds)

    /// Provides target date/time for the next save assuming a save just happened.
    let nextSave() = DateTime.Now.AddMilliseconds(maxMillisecondsBetweenFlush)

    let agent = 
        new MailboxProcessor<CloudBlockBlobWriterAgentMessage>(fun inbox -> 
            let rec loop (nextSaveAt:DateTime) = async {
                let! msg = inbox.TryReceive(timeout = int (max 0.0 (nextSaveAt - DateTime.Now).TotalMilliseconds))
                match msg with 
                | Some(Append(value)) -> 
                    buffer.AppendLine(value) |> ignore
                    let! timestamp = async { 
                        if (buffer.Length > maxBufferLength)  || ((nextSaveAt - DateTime.Now).TotalMilliseconds <= 0.0) then 
                            do! writeToBlob()
                            return nextSave()
                        else return nextSaveAt }
                    return! loop timestamp
                | Some(Flush(ch)) -> 
                    do! writeToBlob()
                    ch.Reply()
                    return! loop (nextSave())
                | None -> 
                    do! writeToBlob()
                    return! loop (nextSave())
            }
            loop (nextSave()))
    do agent.Error.Add(fun ex -> raise ex)
    do agent.Start()
    
    new(blob, maxMillisecondsBetweenFlush) = new CloudBlockBlobWriter(blob, maxMillisecondsBetweenFlush, 1024 * 1024)     
    new(blob) = new CloudBlockBlobWriter(blob, 5000.0)
       
    override x.Encoding with get() = System.Text.Encoding.UTF8

    /// Writes the specified string value followed by the default line terminator. 
    override x.WriteLine (value:string) = agent.Post(Append(value))

    /// Waits until all data written so far has been persisted to the underlying blob.
    override x.Flush() = agent.PostAndReply(fun ch -> Flush ch)

    override x.Dispose disposing = x.Flush(); base.Dispose disposing


// A simple bundle store for a container in Azure blob storage
type AzureBundleStore(container:CloudBlobContainer, root:string) =

    let init() =
        if not (Directory.Exists root) then 
            failwith (sprintf "The root folder does not exist: %s" root)
        if not (Directory.EnumerateDirectoriesAndFiles root |> Seq.isEmpty) then
            failwith (sprintf "The root folder is not empty: %s" root)

    do init()

    let exists (blobName:string) =
        let blob = container.GetBlockBlobReference(blobName)
        blob.Exists()

    let download blobName filepath =         
        Directory.CreateDirectory(Path.GetDirectoryName(filepath)) |> ignore
        let blob = container.GetBlobReferenceFromServer(blobName)
        use filestream = File.Create(filepath)
        blob.DownloadToStream(filestream)

    let upload (blobName:string) (filepath:string) =
        let blob = container.GetBlockBlobReference(blobName)
        use filestream = File.OpenRead(filepath)
        blob.UploadFromStream(filestream)

    member this.HasReference id = exists id

    member this.GetReference (id:string) = 
        let fileName = sprintf "%s%s" (Path.GetFileNameWithoutExtension(Path.GetTempFileName())) (Path.GetExtension(id))
        let filePath = Path.Combine(root, fileName)
        download id filePath
        Some(LocalBundleReference.Create(filePath)) 

    member this.PutReference id path = upload id path

    member this.GetStore() = { BundleStore.Has = this.HasReference
                               Get = this.GetReference
                               Put = this.PutReference }

// Provide an implementation of RunDiagnostic for writers backed by Azure storage.
module AzureDiagnostics =

    let private getWriter (container:CloudBlobContainer) name (bundle:Bundle) = 
        let baseId = (bundle.Id.Substring(0, bundle.Id.Length - Path.GetExtension(bundle.Id).Length))
        let blobName = sprintf "%s/%s.txt" baseId name
        let blob = container.GetBlockBlobReference(blobName)
        new CloudBlockBlobWriter(blob) :> TextWriter 

    let get container = { StdoutWriter = getWriter container "stdout"; StderrWriter = getWriter container "stderr" }

// Distributed execution

/// Defines a generic request to execute a task.
[<DataContract>]
type TaskRequest<'T> = {
    [<field: DataMember(Name = "id")>] Id : string
    [<field: DataMember(Name = "task_type")>] TaskType : string
    [<field: DataMember(Name = "task_args")>] TaskArgs : 'T
}

/// Captures input arguments for a CodaLab run.
[<DataContract>]
type RunArgs = {
    // Until a bundle service is available, the following parameters provide
    // access to the run definition. The assumption is that the run definition
    // is a bundle stored in a known storage account (set through app config).
    [<field: DataMember(Name = "bundle_id")>] BundleId : string
    [<field: DataMember(Name = "container_name")>] ContainerName : string
    [<field: DataMember(Name = "reply_to")>] ReplyTo : string
}

/// Defines a request for doing a CodaLab run.
type RunRequest = TaskRequest<RunArgs>

/// Provides status update about a CodaLab run.
[<DataContract>]
type RunUpdateArgs = {
    [<field: DataMember(Name = "status")>] Status : string
}

/// Defines a runnable task.
type Task = {
    Id : string
    Run : unit -> unit
    ReplyTo : string
}

module RunTask =

    // Execute a run.
    let run (account:CloudStorageAccount) (localStorageRoot:string) (args:RunArgs) =
        let bundleId = args.BundleId
        let containerName = args.ContainerName
        Trace.TraceInformation("CodaLab run begins for bundle {0}.", bundleId)
        let rootPath = Path.Combine(localStorageRoot, Path.GetRandomFileName())
        let tempPath = Path.Combine(rootPath, @"T") // Temp
        let runsPath = Path.Combine(rootPath, @"R") // Runs
        Directory.CreateDirectory(tempPath) |> ignore
        Directory.CreateDirectory(runsPath) |> ignore
        Trace.TraceInformation("Temp folders created under {0}", rootPath)
        let container = account.CreateCloudBlobClient().GetContainerReference(containerName)
        let azureStore = new AzureBundleStore(container, tempPath)
        let bundleSvc = new BundleService(azureStore.GetStore(), runsPath, true)
        let runDiagnostic = AzureDiagnostics.get(container)
        Trace.TraceInformation("Ready to execute")
        executeIt bundleSvc bundleId runDiagnostic
        Trace.TraceInformation("CodaLab run ends for bundle {0}.", bundleId)

    // Creates a RunTask matching the given message.
    let create account localStorageRoot (message:BrokeredMessage) = 
        let req = message.GetBody<RunRequest>(new DataContractJsonSerializer(typeof<RunRequest>))
        { Id = req.Id; ReplyTo = req.TaskArgs.ReplyTo; Run = fun () -> run account localStorageRoot req.TaskArgs }


type Worker(svcBusConnectionString, queueName, create_task) =

    /// Create Client object to connect to the specified Windows Azure Service Bus queue
    let namespaceManager = NamespaceManager.CreateFromConnectionString(svcBusConnectionString)
    do if (namespaceManager.QueueExists(queueName) = false) then
        failwith (sprintf "Queue [%s] does not exist." queueName)
    let client = QueueClient.CreateFromConnectionString(svcBusConnectionString, queueName)
    let completedEvent = new ManualResetEvent(false)

    let try_decode_message (message:BrokeredMessage) =
        try
            Some(create_task message)
        with ex ->
            Trace.TraceError("Unable to decode message: {0}\n{1}", message.SequenceNumber.ToString(), ex.StackTrace)
            None

    let send_update (task:Task) (client:QueueClient) (status:string) =
        let data = { Id = task.Id
                     TaskType = "run_update"
                     TaskArgs = { Status = status } }
        let msg = new BrokeredMessage(data, new DataContractJsonSerializer(typeof<TaskRequest<RunUpdateArgs>>))
        client.Send(msg)

    let run_or_fail (task:Task) =
        let client = QueueClient.CreateFromConnectionString(svcBusConnectionString, task.ReplyTo)
        try 
            send_update task client "running"
            task.Run()
            send_update task client "finished"
        with ex ->
            Trace.TraceError("Task (id={0}) failed:\n{1}", task.Id, ex.StackTrace)
            send_update task client "failed"

    member this.Start() =
        Trace.TraceInformation("Entering Worker::Start.")
        client.OnMessage(fun message ->
            let messageId = message.SequenceNumber.ToString()
            Trace.TraceInformation("Received message: {0}", messageId)
            message.Complete()
            match try_decode_message message with
            | Some(task) -> run_or_fail task
            | _ -> ()
            Trace.TraceInformation("Finished processing message: {0}", messageId)
        )
        completedEvent.WaitOne() |> ignore
        Trace.TraceInformation("Leaving Worker::Start.")

    member this.Stop() =
        Trace.TraceInformation("Entering Worker::Stop.")
        client.Close()
        completedEvent.Set() |> ignore
        Trace.TraceInformation("Leaving Worker::Stop.")

    static member CreateAndStart(connectionString, queueName, account, localStorageRoot) =
        let worker = new Worker(connectionString, queueName, RunTask.create account localStorageRoot)
        async { worker.Start() } |> Async.Start
        worker

