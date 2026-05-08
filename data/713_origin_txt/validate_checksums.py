#!/usr/bin/env python3
"""
validate_checksums.py - Verify integrity of compiled experimental data

Checks MD5 checksums for all compiled CSV files to ensure data integrity
for reproducibility verification.
"""

import hashlib
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
COMPILED_DIR = SCRIPT_DIR.parent / "compiled"

def md5_file(filepath):
    """Generate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def validate_checksum(csv_file):
    """Validate a single CSV file against its MD5 checksum."""
    md5_file_path = Path(f"{csv_file}.md5")

    if not csv_file.exists():
        return None, f"CSV file not found: {csv_file}"

    if not md5_file_path.exists():
        return None, f"MD5 file not found: {md5_file_path}"

    # Read expected checksum
    with open(md5_file_path) as f:
        line = f.readline().strip()
        expected_hash = line.split()[0]

    # Calculate actual checksum
    actual_hash = md5_file(csv_file)

    if actual_hash == expected_hash:
        return True, actual_hash
    else:
        return False, f"MISMATCH: expected {expected_hash}, got {actual_hash}"

def main():
    print("=" * 60)
    print("NeurIPS 2026 — marginot - Validating Data Checksums")
    print("=" * 60)

    if not COMPILED_DIR.exists():
        print("[!] Compiled directory not found. Run compile_batches.py first.")
        sys.exit(1)

    csv_files = sorted(COMPILED_DIR.glob("*.csv"))

    if not csv_files:
        print("[!] No compiled CSV files found.")
        sys.exit(1)

    all_valid = True
    results = []

    for csv_file in csv_files:
        valid, info = validate_checksum(csv_file)

        if valid is None:
            status = "SKIP"
            all_valid = False
        elif valid:
            status = "OK"
        else:
            status = "FAIL"
            all_valid = False

        results.append((csv_file.name, status, info))
        print(f"  [{status:4s}] {csv_file.name}")
        if status == "FAIL":
            print(f"         {info}")

    print("\n" + "=" * 60)
    if all_valid:
        print("ALL CHECKSUMS VALID")
        print("=" * 60)
        sys.exit(0)
    else:
        print("CHECKSUM VALIDATION FAILED")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
