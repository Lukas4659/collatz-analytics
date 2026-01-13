"""
Collatz Data Generator.

This script allows the user to define a range of natural numbers,
calculates full Collatz sequences for them, and saves the results
to a CSV file with a transposed structure (columns).
"""

import collatz_tools as ct


def main():
    """
    Main control procedure for the generator.

    Sequence:
    1. Get range input from user.
    2. Calculate sequences with progress bar.
    3. Save to external CSV file.
    """

    print("--- COLLATZ DATA GENERATOR ---")

    # 1. Get input using our tools
    start, end = ct.get_data_range_input()

    # 2. Calculate
    print("Calculations in progress...")
    data = ct.calculate_all_sequences(start, end, progress_callback=ct.terminal_progress_bar)

    # 3. Save (using default filename from tools)
    ct.save_sequences_to_file(data, progress_callback=ct.terminal_progress_bar)

    print("Generator finished successfully.")


if __name__ == "__main__":
    main()

