namespace CodaLab.Compute.Utilities

open System
open System.IO
open System.Text
open System.Runtime.Serialization
open System.Runtime.Serialization.Json

[<AutoOpen>]
module Common =

    //let IsNull<'T when 'T : equality> (x:'T) = (x = Unchecked.defaultof<'T>)
    let IsNull<'T>(x:'T) = match box x with | null -> true | _ -> false

