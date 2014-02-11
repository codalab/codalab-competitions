namespace CodaLab.Bundles

open System
open System.Collections.Generic
open System.Diagnostics
open System.IO
open System.IO.Compression
open System.Net
open System.Text

open YamlDotNet
open YamlDotNet.RepresentationModel

// Reads bundle metadata from a specified YAML file.
type Metadata(yamlFilePath) =

    let loadYaml filepath =
        let yaml = new YamlStream()
        if File.Exists filepath then
            use strm = File.OpenText(filepath)
            yaml.Load(strm)
        else yaml.Load(new StringReader("description: "))
        Seq.head yaml.Documents

    let tryFindSimpleValue (yaml:YamlDocument) key =
        match yaml.RootNode with
        | :? YamlMappingNode as mapping ->
            match mapping.Children.TryGetValue(new YamlScalarNode(key)) with
            | false, _ -> None
            | true, n -> match n with | :? YamlScalarNode as sn -> Some(sn) | _ -> None
        | _ -> None

    let findSimpleValueOrDefault (yaml:YamlDocument) key defaultValue = 
        match tryFindSimpleValue yaml key with | Some(n) -> n.Value | None -> defaultValue

    let description (yaml:YamlDocument) = findSimpleValueOrDefault yaml "description" String.Empty
    let input (yaml:YamlDocument) = findSimpleValueOrDefault yaml "input" String.Empty
    let program (yaml:YamlDocument) = findSimpleValueOrDefault yaml "program" String.Empty
    let command (yaml:YamlDocument) = findSimpleValueOrDefault yaml "command" String.Empty

    let findBundleReferences (yaml:YamlDocument) = seq {
        let reservedKeys = Set.ofList ["description"; "command"]
        match yaml.RootNode with
        | :? YamlMappingNode as mapping ->
            for child in mapping.Children do
                let knOpt = match child.Key with | :? YamlScalarNode as n -> Some(n) | _ -> None
                let kvOpt = match child.Value with | :? YamlScalarNode as n -> Some(n) | _ -> None
                match (knOpt, kvOpt) with
                | Some(kn), Some(kv) -> if reservedKeys.Contains kn.Value then () else yield (kn.Value, kv.Value)
                | _, _ -> ()
        | _ -> () }

    let yamlDoc = loadYaml yamlFilePath

    // Gets the value of the "description" key
    member this.Description with get() = description yamlDoc
    // Gets the value of the "input" key
    member this.Input with get() = input yamlDoc
    // Gets the value of the "program" key
    member this.Program with get() = program yamlDoc
    // Gets the value of the "command" key
    member this.Command with get() = command yamlDoc
    // Recursively get all bundle references (expressed as key-value pairs) in this bundle
    // and its sub-bundles up to a maximum depth (hardwired at 3).
    member this.References() = findBundleReferences yamlDoc

// Represents a reference to a bundle on the local machine.
type public LocalBundleReference =
    // A bundle stored as a directory structure 
    | DirectoryBundle of string (* full path of the directory *)
    // A bundle stored in a ZIP
    | ZipBundle of string (* full path of the ZIP file *)
    // A bundle which is just a metadata file
    | MetadataOnlyBundle of string  (* full path of the metadata file *)  
    with 
    // Copy the bundle into the specified location.
    member this.CopyTo destination =
        match this with
        | DirectoryBundle(source) -> 
            Directory.CopyDirectoriesAndFiles source destination
        | ZipBundle(source) -> 
            ZipFile.ExtractToDirectory(source, destination)
        | MetadataOnlyBundle(source) -> 
            Directory.CreateDirectory destination |> ignore
            File.Copy(source, Path.Combine(destination, "metadata"))
    // Create a local reference associated with the give file or directory path.
    static member Create(path) =
        if File.Exists(path) then
            match Path.GetExtension(path).ToLowerInvariant() with
            | ".zip" -> ZipBundle(path)
            | _      -> MetadataOnlyBundle(path)
        else if Directory.Exists path then DirectoryBundle(path) 
        else failwith (sprintf "The specified path does not exist: %s" path)

// A bundle available as a directory structure on the local file system.
type Bundle(id:string, lref:LocalBundleReference, path) =   
    member this.Id with get() = id
    member this.AbsolutePath with get() = path
    member this.ReadMetadata() = new Metadata(Path.Combine(path, "metadata"))

// Represents a backend capable to storing and serving bundles to the BundleService    
type BundleStore = {
    Has : string (* bundleId *) -> bool
    Get : string (* bundleId *) -> LocalBundleReference option
    Put : string (* bundleId *) -> string (* bundlePath *) -> unit
}

// A local proxy to a bundle service.
type BundleService(storage:BundleStore, root:string, useShortPaths:bool) =

    let init() =
        if not (Directory.Exists root) then 
            failwith (sprintf "The root folder does not exist: %s" root)
        if not (Directory.EnumerateDirectoriesAndFiles root |> Seq.isEmpty) then
            failwith (sprintf "The root folder is not empty: %s" root)

    do init()

    let tempPath (id:string) = 
        if useShortPaths then Path.Combine(root, Path.GetFileNameWithoutExtension(Path.GetTempFileName()))
        else Path.Combine(root, Path.GetDirectoryName(id), Path.GetFileNameWithoutExtension(id))

    let cache = new Dictionary<string, LocalBundleReference>()

    let hasBundle (id:string) = if cache.ContainsKey(id) then true else storage.Has(id)

    let getBundleReference (id:string) =
        match cache.TryGetValue(id) with
        | true, bRef -> bRef
        | false, _ -> 
            match storage.Get(id) with
            | Some(lRef) ->   
                cache.Add(id, lRef)
                lRef
            | None -> failwith (sprintf "A bundle with the specified ID does not exist (id = %s)." id)
     
    let getBundle (id:string) getAbsPath =
        let bref = getBundleReference id
        let absPath = getAbsPath bref
        if not (Directory.Exists absPath) then bref.CopyTo absPath
        new Bundle(id, bref, absPath)
        
    let addBundle (id:string) (path:string) =
        if hasBundle(id) then failwith (sprintf "A bundle with the same id already exists in the provider (id = %s)." id)
        let lref = LocalBundleReference.Create path
        let filepath =
            match lref with
            | DirectoryBundle(srce) -> 
                let zipPath = sprintf "%s.zip" (tempPath id)
                ZipFile.CreateFromDirectory(srce, zipPath)
                zipPath
            | ZipBundle(srce) -> 
                srce
            | MetadataOnlyBundle(srce) -> 
                raise(NotImplementedException())
        storage.Put id filepath 

    // Checks if the bundle with the given ID exists. Bundle IDs are case-sensitive.                        
    member this.Has id = hasBundle id
    // Get the bundle with the given ID.
    member this.Get id = 
        getBundle id (fun bref -> match bref with | DirectoryBundle(srce) -> srce | _ -> tempPath id)   
    // Get a copy of the bundle with the given ID expanded at the specified destination.
    member this.GetInto id destination = 
        getBundle id (fun _ -> destination)
    // Register a local bundle with the service
    member this.Put bundle = addBundle bundle

// A simple bundle store for the local file system
type internal LocalBundleStore() =

    let cache = new Dictionary<string, LocalBundleReference>()

    member this.HasReference id = cache.ContainsKey(id)
    member this.GetReference id = match cache.TryGetValue id with | true, r -> Some(r) | false, _ -> None
    member this.PutReference id path = cache.Add(id, LocalBundleReference.Create path)

    member this.GetStore() = { BundleStore.Has = this.HasReference
                               Get = this.GetReference
                               Put = this.PutReference }


// Represents a means of creating text writers for capturing standard diagnostic information
// during a run.
type RunDiagnostic = {
    StdoutWriter : Bundle -> TextWriter
    StderrWriter : Bundle -> TextWriter
}

// Provide an implementation of RunDiagnostic for the local file system.
module LocalDiagnostics =

    let private getWriter name (bundle:Bundle)  = File.CreateText(Path.Combine(bundle.AbsolutePath, name)) :> TextWriter

    let get() = { StdoutWriter = getWriter "stdout.txt"; StderrWriter = getWriter "stderr.txt" }
