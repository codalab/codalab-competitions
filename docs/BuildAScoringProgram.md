In the current CodaLab competition model a competition is constructed with a set of Reference Data and a Scoring Program. The way competitions work currently the Reference Data is compared with a participants submission and the differences in the two are scored using the Scoring Program.

The program.zip bundle contains the Scoring Program that compares the participants submission with the reference data (in the reference.zip bundle) to score the submission. In this example the reference data contains the value of pi. The program.zip bundle computes the absolute difference of the submitted value from the reference value.

Here are the contents of the reference.zip file:
```
reference.zip 
  |- answer.txt (Contains: 3.14159265359)
  |- metadata   (Contains: This is the authoritative result.)
```

A submission.zip for this competition would look similar:
```
submission.zip 
  |- answer.txt (Contains: 3.1415359)
```

Here are the contents of the program.zip file:
```
program.zip
  |- evaluate.exe (The program that's run)
  |- metadata     (Contents below...)
  |- supporting modules and libraries for evaluate.exe to run in isolation.
```

The program.zip metadata file contains:
```
command: $program/evaluate.exe $input $output
description: Example competition evaluation program.
```

Here are the assumptions about the scoring process and the scoring program:

1. There is a fixed directory structure that the scoring program operates within. It looks like this:
    ```
    Submission Directory
      |- input
        |- ref (This is the reference data unzipped)
        |- res (This is the user submission unzipped)
      |- program (This is the scoring program [and any included dependencies] unzipped)
      |- output (This is where the scores.txt file needs to be written by the scoring program)
    ```
1. The scoring program will be invoked as ```<program> <input directory> <output directory>```
1. The scoring program is executed so that stderr and stdout are captured
1. The scoring program will generate a scores.txt file (it has to be named scores.txt) that contains key value pairs of metrics. This is a score file for the example competition:
    ```
    Difference: 0.0057
    ```
1. Each key in the scores.txt file is identical to a leaderboard column key in the competition.yaml. (e.g. "DIFFERENCE" in the [example competition.yaml](https://github.com/codalab/codalab/wiki/12.-Building-a-Competition-Bundle). This is how scores are related to the competition for reporting so it is critical the leaderboard keys and the keys in the scores.txt are identical.