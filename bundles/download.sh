#!/bin/bash

# Run this script to download all the standard Bundles.

(cd base/weka && ./download.sh)
(cd base/uci_arff && ./download.sh)
(cd pliang/census_population && ./download.sh)
