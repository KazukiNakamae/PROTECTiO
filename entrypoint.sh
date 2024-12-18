#!/bin/bash
# Activate conda environment
source activate protectio

# Execute passed command
exec "$@"
