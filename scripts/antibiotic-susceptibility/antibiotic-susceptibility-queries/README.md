# Antibiotic Resistance Inference Queries

This folder contains SQL queries used for inferring antibiotic susceptibility and resistance patterns based on organism identification and existing antibiotic test results. The queries are part of a larger project aimed at creating a comprehensive antibiogram for personalized patient care in a clinical setting.

## Overview

Clinicians often rely on established knowledge about common resistance patterns when interpreting culture and sensitivity results. However, not all susceptibility tests explicitly list every antibiotic for every organism. This collection of queries explicitly codifies implicit knowledge about resistance patterns into the database, allowing for automated inference of susceptibility.

## Contents

- `create-implied-table.sql`: SQL script to create a table that extends `culture_sensitivity` with an `implied_susceptibility` column.
- `populate-implied-susceptibility.sql`: SQL script to populate the new table with inferred susceptibility based on organism-specific rules.
- `update-rules`: Folder containing individual SQL scripts for updating inferred susceptibilities, each script corresponding to a specific organism or antibiotic resistance pattern.

## Usage

The SQL scripts should be run in the order listed above. They are designed to be executed on a database that contains culture sensitivity data from a clinical microbiology lab. Please review each script to ensure compatibility with your specific database schema before running.

## Contributing

If you have suggestions for additional rules or improvements to existing queries, please open an issue or submit a pull request.

