"""
One-time script to pre-process ADI_data_CA.csv (433MB) into a small lookup pickle.

Input:  ADI_data_CA.csv with columns BENE_ZIP_CD, ADI_NATRANK, ADI_STATERNK
Output: adi_lookup.pkl — dict mapping 9-digit ZIP to (natrank, staternk)
        Also includes 5-digit ZIP aggregates (median of all 9-digit entries).

Usage:
    python preprocess_adi.py /path/to/ADI_data_CA.csv /path/to/output/adi_lookup.pkl

Example:
    python preprocess_adi.py \
        /Users/sandychen/Desktop/Healthrex_workspace/stanford_models/ADI_data_CA.csv \
        /Users/sandychen/Desktop/Healthrex_workspace/stanford_models/adi_lookup.pkl
"""
import csv
import pickle
import sys
from collections import defaultdict

def main():
    if len(sys.argv) != 3:
        print("Usage: python preprocess_adi.py <input_csv> <output_pkl>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_pkl = sys.argv[2]

    print(f"Reading {input_csv}...")
    zip9_lookup = {}
    zip5_values = defaultdict(list)

    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            zip_code = row['BENE_ZIP_CD'].strip().strip('"')
            natrank = row['ADI_NATRANK'].strip().strip('"')
            staternk = row['ADI_STATERNK'].strip().strip('"')

            # Skip non-numeric ranks (some entries have 'GQ' or 'PH')
            try:
                natrank_int = int(natrank)
                staternk_int = int(staternk)
            except ValueError:
                continue

            # Store 9-digit lookup
            zip9_lookup[zip_code] = (natrank_int, staternk_int)

            # Accumulate for 5-digit aggregation
            zip5 = zip_code[:5]
            zip5_values[zip5].append((natrank_int, staternk_int))

            count += 1
            if count % 500000 == 0:
                print(f"  Processed {count:,} rows...")

    # Compute 5-digit medians
    zip5_lookup = {}
    for zip5, values in zip5_values.items():
        natranks = sorted(v[0] for v in values)
        staternks = sorted(v[1] for v in values)
        mid = len(values) // 2
        zip5_lookup[zip5] = (natranks[mid], staternks[mid])

    result = {
        'zip9': zip9_lookup,
        'zip5': zip5_lookup,
    }

    print(f"\nResults:")
    print(f"  9-digit ZIP entries: {len(zip9_lookup):,}")
    print(f"  5-digit ZIP entries: {len(zip5_lookup):,}")

    print(f"\nWriting {output_pkl}...")
    with open(output_pkl, 'wb') as f:
        pickle.dump(result, f)

    import os
    size_mb = os.path.getsize(output_pkl) / (1024 * 1024)
    print(f"Done. Output size: {size_mb:.1f} MB")

if __name__ == '__main__':
    main()
