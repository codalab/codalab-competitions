# Creating a Submission Bundle

Submission bundles are zip files that come in two flavors:

1. **Result submissions** may contain whatever the competition requires. `JSON` files, images, anything!
2. **Code submissions** must contain a `metadata` file describing how to run the submission.

# metadata format

For code submissions you must include a file in the root directory named `metadata`.

Example `metadata` file:

```
command: python $program/test.py $input $output $shared
```

Before your program is executed the following strings will be replaced with the corresponding data:

| variable | description |
| --- | --- |
| $program | root directory containing your program |
| $input | input directory containing competition data |
| $output | directory to put your code results |
| $shared | special directory to talk to ingestion program during your code submission |
