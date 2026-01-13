"""
Statistical Analysis Module for Collatz Data.

This program processes raw sequences to generate advanced metrics:
- Median
- Expansion Factor (Max/Start)
- Glide Time
- Parity Balance
It also generates a summary CSV report.
"""

import collatz_tools as ct


def main():
    """
    Main loop of the statistical analyzer.
    Manages data source selection (new calculation or file loading),
    processing, and report saving.
    """
    print("--- COLLATZ STATISTICS ANALYZER ---")
    print("Do you want to [1] Generate new data, or [2] Load from file? (1/2): ")
    choice = input("Choice: ")

    all_sequences = []

    if choice == '1':
        start, end = ct.get_data_range_input()
        print("Calculating sequences...")
        all_sequences = ct.calculate_all_sequences(start, end, progress_callback=ct.terminal_progress_bar)

    elif choice == '2':
        filename = input("Enter filename (press Enter for default): ") or ct.DEFAULT_FILENAME
        print(f"Loading data from {filename}...")
        all_sequences = ct.read_sequences_from_file(filename, progress_callback=ct.terminal_progress_bar)

    else:
        print("Unknown option.")
        return

    if not all_sequences:
        print("No data to analyze.")
        return

    # Process statistics
    print(f"\nProcessing statistics for {len(all_sequences)} sequences...")
    stats_list = ct.analyze_sequence_dataset(all_sequences)

    # Save report
    stats_filename = "Report_Stats_Full.csv"
    ct.save_stats_to_csv(stats_list, stats_filename)

    # Display sample info for the first few
    print("\n--- Sample Results (First 3) ---")
    for stat in stats_list[:3]:
        ct.display_stats_in_terminal(stat)

    print(f"\nFull report saved to: {stats_filename}")


if __name__ == "__main__":
    main()

