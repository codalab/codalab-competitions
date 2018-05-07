namespace System.IO

    [<AutoOpen>]
    module DirectoryExt =

        type Directory with

            /// Recursively enumerates the files and folders in the specified directory. Each element of 
            /// the enumerable collection is a tuple of type (bool * string) where the string component is 
            /// the path and the boolean component is true for a directory and false for a file.
            static member EnumerateDirectoriesAndFiles (path:string) = 
                let rec emit folder = seq {
                    for f in Directory.EnumerateFiles(folder) do 
                        yield false, f
                    for d in Directory.EnumerateDirectories(folder) do
                        let dpath = Path.Combine(folder, d)
                        yield true, dpath
                        for t in emit dpath do yield t }
                if Directory.Exists path then emit path else Seq.empty

            /// Performs a recursive copy of the directory tree in the given source path into the destination path.
            static member  CopyDirectoriesAndFiles (source:string) (destination:string) =
                let destinationPath (path:string) = 
                    let from = Path.GetFullPath(source)
                    if path.Length > from.Length then Path.Combine(destination, path.Substring(from.Length + 1))
                    elif path.Length = from.Length then destination
                    else failwith "Unable to create a destination path."
                Directory.EnumerateDirectoriesAndFiles source
                |> Seq.iter(fun (isDirectory, srce) ->
                    let dest = destinationPath srce
                    if isDirectory then Directory.CreateDirectory(dest) |> ignore else File.Copy(srce, dest))

