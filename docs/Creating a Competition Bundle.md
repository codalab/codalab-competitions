# Creating a Competition Bundle


*More details coming soon...*



# Ingestion Program


### metadata format

For ingestion programs you must include a file in the root directory named `metadata`.

Example `metadata` file:

```
command: python $program/test.py $input $output $shared
```

Before your program is executed the following strings will be replaced with the corresponding data:

| variable | description |
| --- | --- |
| $program | root directory containing your program |
| $input | input directory containing competition data |
| $output | where the code submission saves results |
| $shared | special directory to talk to submission program during a code submission |
| $hidden | directory where hidden reference data is stored |
