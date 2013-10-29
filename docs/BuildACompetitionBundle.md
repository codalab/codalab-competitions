Building a competition in CodaLab is possible by uploading a Competition Bundle. A Competition Bundle is a zip archive which contains a yaml file that describes the competition. Other assets are included in the zip archive but won't be used unless they are referenced in the competition.yaml file.

Here are the contents of the example competition.zip bundle:
```
competition.zip
  |- competition.yaml
  |- data.html
  |- evaluation.html
  |- logo.jpg
  |- overview.html
  |- program.zip
  |- reference.zip
  |- terms_and_conditions.html
```

Here is an example [competition.yaml](https://github.com/codalab/codalab/blob/master/codalab/scripts/competition_example/competition.yaml). If you are not familiar with how competitions look in CodaLab, you might browse competitions before you read the configuration to get a basic understanding of the components of a competition.

This competition is a construed example for illustrative purposes. Assume the competition goal is to compute the value of pi (3.14...). The submission that contains the closest value of pi is the winner, each participant a single float value as their submission.

Here's an annotated competition.yaml, to explain the various configuration elements.

```
# Build an example competition
---
# The title of the competition
title: Example Competition
# A description of the competition
description: This is a competition to test the competition bundle system. It should be able to create a competition from this bundle. The goal is to compute the closest value of pi possible.
# A logo/image for the competition
image: logo.jpg
# Does this competition require participant approval by the organizer
has_registration: True
# When is this competition finished. It is valid to not include an end_date, which means the competition remains open perpetually.
end_date: 2013-12-31
# Each competition has a set of html pages for potential participants to read and review and for participants to use to interact with the competition. These are the specifications for those pages.
html: 
    # Basic overview (first impression) of the challenge
    overview: overview.html
    # What are the metrics being used for this challenge, how is it being scored.
    evaluation: evaluation.html
    # Terms of participation, including data licensing, results submission, et al
    terms: terms_and_conditions.html
    # Where to find the data, how to download it.
    data: data.html
# Competitions are broken up into phases. Every competition has at least one phase, some have multiple phases.
phases:
    # Phase 1
    1:
        # Phase number for ordering
        phasenumber: 1
        # Label or name of this phase
        label: "Training"
        # When this phase starts - this is the first date participants can download the data and submit results
        start_date: 2013-06-30
        # Maximum number of submissions per participant
        max_submissions: 100
        # A bundle containing the program used to evaluate results.
        scoring_program: program.zip
        # A bundle containing reference data to compare submitted data with for scoring.
        reference_data: reference.zip
        # The datasets used for this phase, all references are URLs to externally stored data
        datasets: 
            # The first data set
            1:
                # Uniquely :) named
                name: Data 1
                # A url to the data
                url: http://spreadsheets.google.com/pub?key=pyj6tScZqmEfbZyl0qjbiRQ&output=xls
                # A brief description to indicate the contents of the data for users
                description: Example Dataset
            # A second data set, there can be any number
            2:
                # Again uniquely named so users can tell what it is
                name: Data 2
                # URL to the actual data
                url: http://spreadsheets.google.com/pub?key=0AgogXXPMARyldGJqTDRfNHBWODJMRWlZaVhNclhNZXc&output=xls 
                # Brief description
                description: Example Dataset
    # Phase 2, the actual competition (in this case)
    2:
        # The second phase.
        phasenumber: 2
        # Phase name/label
        label: "Challenge"
        # When does this phase begin
        start_date: 2013-09-30
        # Maximum submissions this phase
        max_submissions: 3
        # Scoring program for this phase (the same as the previous phase)
        scoring_program: program.zip
        # The reference data for scoring, this could/should/would be different this phase
        reference_data: reference.zip
        # Data sets
        datasets: 
            # Dataset #1
            1:
                # Data set name
                name: Challenge Data
                # URL for the dataset
                url: http://spreadsheets.google.com/pub?key=t9GL1nIZdtxszJbjKErN2Hg&output=xls
                # Data set description
                description: Example challenge data
# Leaderboard / Scoreboard configuration
leaderboard:
    # Collections of scores, ways to slice multi-dimensional scores into "groups"
    # This leaderboard has one result, the difference (difference of the submitted number from Pi)
    groups:
        # The internal key name for the overall results group
        RESULTS: &RESULTS
            # Label for this group
            label: Results
            # Ordering of the groups, starts at 1
            rank: 1
    # Actual scores in the leaderboard
    columns:
        # The internal key for this score
        DIFFERENCE:
            # This is a member of the results group
            group: *RESULTS
            # The column label for this score
            label: Difference
            # Order of the scores
            rank: 1
```

To make this example complete it's important to understand how to build and package the program.zip and reference.zip referred to in the competition.yaml.

The program.zip bundle contains the program that compares the users submission with the reference data (in the reference.zip bundle) to score the submission. In this case the reference data contains the value of pi. The program.zip bundle computes the absolute difference of the submitted value from the reference value.

Here are the contents of the reference.zip file:
```
reference.zip 
  |- answer.txt (Contains: 3.14159265359)
  |- metadata   (Contains: This is the authoritative result.)
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
