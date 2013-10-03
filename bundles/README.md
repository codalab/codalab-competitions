### Standard programs and datasets

To get started, download some relevant programs and datasets, type:

    ./download.sh

### Command-line utility prototype

To start the worker process:

    python codalab.py worker

Now you can run commands to upload programs/datasets and run them.

    ./basic_ml.sh

There are several design changes in the new command-line utility prototype
(compared to the worksheet prototype `controller.py`, see below):

- Bundles have a much more uniform design more centered around running commands
  and dependency management.  Now, a Bundle can independently have
    - Arbitrary code/data files.
    - Dependencies to other Bundles (stored as `deps`).
    - A `command` (for Run Bundles).
  All three fields are optional.
- Programs are *uploaded* from the `pliang` directory rather than just running
  in place.
- A sqlite database is used to store all the Bundle information (so it will be
  more similar to the final web-based version).
- All execution is done in a scratch directory.  This also makes the data
  copying logic explicit.

### Worksheet prototype

The Worksheet prototype is outdated and needs to be integrated with the new
command-line prototype schema.

But if you still want to run the Worksheet system, type:

    python controller.py

This should generate use the Bundles/Worksheets in `pliang` and generate new
ones in `generated`.  The HTML visualization of the output is in `html_out`.
