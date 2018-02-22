#!/bin/bash

echo "Adding ~/healthrex/CDSS/ to PYTHONPATH..."
export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS
printf 'export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS\n' >> ~/.bashrc
printf 'export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS\n' >> ~/.bash_profile
