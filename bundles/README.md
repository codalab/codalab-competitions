### Standard programs and datasets

To download the relevant, type:

    ./download.sh

### Worksheet prototype

To run the test the Worksheet system, type:

    python controller.py

This should generate use the Bundles/Worksheets in `pliang` and generate new
ones in `generated`.  The HTML visualization of the output is in `html_out`.

### Command-line utility prototype

To start the worker process:

    python codalab.py worker

Now you can run commands to upload programs/datasets and run them.

    ./basic_ml.sh

There are several design changes in the new command-line utility prototype
(compared to the worksheet prototype):

- Bundles have a much more uniform design more centered around running commands
  and dependency management.  Now, a Bundle can independently have
    - Arbitrary code/data files.
    - Dependencies to other Bundles (stored as `deps`).
    - A `command` (for Run Bundles).
  All three fields are optional.
- Programs are *uploaded* from the `pliang` directory rather than just running
  in place.
- A sqlite database is used to store all the Bundle information (so it will be
  more similar to the final version).
- All execution is done in a scratch directory, which is more safe.  This also
  makes the data copying logic more explicit.
