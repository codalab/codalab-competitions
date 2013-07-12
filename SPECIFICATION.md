# Overview

This document describes the design of the CodaLab website.  This is still
incomplete.

## Entities

These are the low-level entities in CodaLab:

- **Bundle**: a Bundle is the basic building block used to represent programs
  and datasets.  Formally, it is an *immutable* directory containing files and
  possibly further sub-directories.  Each Bundle has a global ID which is
  unique and stable (this is how we get reproducibility in research).  Some
  Bundles are uploaded by the user, and others are generated on CodaLab by
  running programs.  A Bundle has a designated directory inside it (currently,
  this directory is represented as a YAML file):
    - <code>metadata</code>
        - <code>name</code>: name of the Bundle.
        - <code>description</code>: free-form description of the Bundle
        - <code>tags</code>: list of strings to help CodaLab classify the Bundle.

- **Program**: a Program is a Bundle (which presumably contains executable
  code) plus a *command-line string* which is executed to access that code.
  The Bundle also must contain additional information:
    - Architecture: this program can only be run on certain architectures (e.g., Windows, Linux, MacOS)?
    - Modules needed: what does program need (in the appropriate path) to run (e.g., numpy, scipy, Matlab)?

- **Run**: A Run represents the execution of a program.  Formally, is just a
  Bundle, but is required to have the following directories:
    - <code>program</code>: the Bundle of the program that is run.
    - <code>input</code>: the Bundle of the input that is read by the program.
    - <code>output</code>: the Bundle of the output written by the program.
    - <code>stdout</code>: what was output to stdout
    - <code>stderr</code>: what was output to stderr
    - <code>specification</code>: contains information about the Run (optional)
        - <code>allowedMemory</code>: how much memory to give the Run
        - <code>allowedTime</code>: how much time to give the Run
    - <code>status</code>: contains system statistics about the Run
        - <code>command</code>: what command was executed
        - <code>exitCode</code>: 0 means normal termination
        - <code>time</code>: how long did the Run take?
        - <code>OS</code>: what operating system was used to run it
        - <code>CPU</code>: what CPU was used
        - <code>memory</code>: how much memory did the Run take?
  While the Run is executing, all of these directories should be updated in
  real-time.

These are the high-level entities in CodaLab:

- **Worksheet**: A Worksheet represents a multi-stage experiment that a user
  wants to perform (e.g., running and evaluating a machine learning algorithm).
  Formally, a Worksheet is a sequence of *blocks*, where each block is one of
  the following:
    - A rich text block which allows users to document their experiment using free text.
    - A single Bundle whose contents can be viewed and edited.
    - A Table, where each row represents a Bundle and columns represent
      different attributes of that Bundle.  This is useful for comparing
      different algorithms side-by-side according to some metric.

- **Competition**: A Competition is an organized way for users to upload either
  a program or predictions.  An evaluation program will automatically scores
  those predictions against the dataset that the competition organizer has
  provided and generate various metrics.  In the case that competititors upload
  predictions, a Competition contains:
    - A dataset (Bundle) which competitors download during the competition and
      can do whatever they want with.
    - A Bundle containing the true predictions which is not revealed to the competitors.
    - An evaluation Program, which takes as input the true predictions and the
      predictions of competitor and generates evaluation metrics in the
      corresponding Run.
    - Various metadata associated with the Competition (e.g., timeline, access,
      etc.).

Both Worksheets and Competitions are built on the common foundation of Bundles,
Programs, and Runs.  In the following sections, we will go through each of
these entities in greater detail, including what exactly is the information we
need to track about each one.

## User

A user represents someone who uses CodaLab to upload Bundles, download Bundles,
create Runs, etc.

### Database fields

- Username (mandatory): immutable, Java identifier
- Email (mandatory): used to validate passwords, etc.
- First name, last name (mandatory)
- Affiliation (mandatory)
- Homepage (optional)
- Interests (optional): free-form paragraph description
- Groups that this user is part of (e.g., admin, medicalImaging), used to
  determine access control.
- Link to Facebook/Google IDs?
- List of Programs/Bundles/Users they are interested in tracking.  They will be
  notified of any activity around them.
- Analytics: creation time, login/logout times

## Bundle

A Bundle is the fundamental primitive in CodaLab: It is used to represent both
datasets, statistics of programs, trained models, and predictions.  The idea is
many research workflows are quite heterogenous, where one program's output is
another's input (raw data to reformatting to feature extraction to machine
learning algorithms to evaluation).

### Database fields

Some of these database fields are also in the <code>metadata</code> file,
because that is possibly how the user first uploaded it.  CodaLab must
automatically keep the <code>metadata</code> and the database synchronized.

- Name (mandatory if this is a program or dataset): immutable Java identifier
- Description (text, mandatory): should be fairly descriptive (need to encourage this socially).
- Tags: created by users or created by programs as a weak type system.
- Owner (User who created this)
- Creation time
- Which groups are allowed to list/read/download/run on this Bundle.
- Provenance: list of Bundles that this Bundle depends on (for example, it is
 common for one of the sub-directories to be a link to a sub-directory inside
 another Bundle).

### Examples

As we noted earlier, Bundles have many uses.  Here are some examples of what
Bundles are used to represent in machine learning:

- **Dataset** (in ARFF format):
    - <code>metadata</code>
    - <code>data.arff</code>: contains the actual data in ARFF format
    - <code>status/numExamples</code>: number of examples (produced by a program that inspects a Dataset).
    - <code>status/numAttributes</code>: number of attributes
- **Model** (for Weka):
    - <code>weka_classifier</code>:
- **Run** (was already shown above).

## Program

Recall that a Program includes a Bundle and a command-line string.

### Database fields

- (all the fields inherited from Bundle)
- ID (should be hash of the Bundle name and command-line)
- Command (string): what to run 

### Examples of types of programs

- Learner (e.g., SVMlight): takes a datashard, and returns a model along with statistics.
- Predictor: takes a model and a datashard, returns predictions.
- Dataset splitter: divide one datashard into two datashard (based on training fraction, randomly or keeping the order (makes sense for NLP)).
- Dataset stripper: removes the correct labels from each training example.
- Dataset inspector: input is a datashard, output is a datashard.  Makes sure
  that the input dataset basically conforms the correct format, can be lenient.
  The output dataset should canoncalize things (for SvmLightFormat, remove
  trailing spaces, replace tabs with spaces, sort features by index, etc.).
- Dataset converters (e.g., convert ARFF or CSV to SVMlight): these converters
  are not meant to be invertible, but commit to a particular encoding.  For
  example, ARFF can have categorical features (red,white,blue), whereas
  SVMlight only takes real vectors.
- Evaluator: takes the predictions and computes statistics (e.g., accuarcy,
  ROC, precision, recall); will be different for different tasks
- Compiler: input is program, output is compiled program targeting a particular
  architecture
- Visualizer: takes predictions or statistics and generates a table or figure.

## Run

A Run is a Bundle with some additional fields.

### Database fields

- (all the fields inherited from Bundle)
- (all the fields from the <code>specification</code> directory)
- (all the fields from the <code>status</code> directory)
- Whether the user should be emailed when a Run finishes.
- Whether a Run should be terminated (user can select this).

## Worksheet

There are several applications of a worksheet:

- Blog post: if I found some interesting patterns (e.g., linear classifiers
  work well for high-dimensional data), I can add a set of Codalab experiments
  to a worksheet, write some analysis and publish the worksheet and make it
  public to people.
- Paper: if I published a paper, I can put all the datasets, code, and
  experiments in one worksheet and include the link to that page from my
  website.
- Working: if I am just developing a bunch of different algorithms, I can create
  a worksheet as a scratch space to keep track of the algorithms that I am
  working on, what the results are so far, etc.

## Competition

Any user can create a competition.  He has to supply the following:
- Deadline dates (when datasets will be released, etc.)
- Multiple datasets (one for training, one for testing)
- A worksheet describing the competition rules, etc.
- Access restrictions (the competition is only open to people in a certain group)

When competitors upload predictions, an Evaluation program is launched, some
metrics are computed, and the leaderboard is updated.

## Miscellaneous

- As much as possible, information should be represented as a directory so that
  it can be downloadable.
- The database should be used to index the information efficiently, especially
  for numeric properties, so we can pull up the algorithms that have the lowest
  error rates.
- An inverted index (e.g., Lucene) should be used for search.

## Macro

Macros provide the users a way to easily create multiple related experiments
given a set of arguments.  TODO: complete this.
