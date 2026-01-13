"""
Visualization and User Interface Module (CLI).

Allows interactive selection of graphical modes:
1. Trajectory Visualization (Line plot of sequences)
2. Statistical Panels (Correlation analysis + Benford's Law)
"""

import collatz_tools as ct
import sys


def main():
    """
    Runs the main interactive menu.
    """
    while True:
        print("\n========================================")
        print("   COLLATZ DATA VISUALIZER v2.0 (CLI)   ")
        print("========================================")
        print("Select mode:")
        print("1. 📈 Sequence TRAJECTORIES (Line Plot)")
        print("      (Requires raw sequences CSV file)")
        print("2. 📊 STATISTICAL Report (Correlations + Benford)")
        print("      (Requires statistics CSV file)")
        print("3. ❌ Exit")

        choice = input("\nChoice (1/2/3): ")

        if choice == '3':
            print("Exiting...")
            sys.exit()

        elif choice == '1':
            default_seq = ct.DEFAULT_FILENAME
            filename = input(f"Raw Data Filename [default: {default_seq}]: ") or default_seq

            print("Loading sequences...")
            data = ct.read_sequences_from_file(filename, progress_callback=ct.terminal_progress_bar)

            if data:
                print(f"Opening plot window for {len(data)} sequences...")
                print("(Close the plot window to return to menu)")
                # in_window=True ensures it spawns the Tkinter wrapper defined in tools
                ct.plot_graph(data, in_window=True)
                print("--- Plot closed ---")

        elif choice == '2':
            default_stat = "Report_Stats_Full.csv"
            filename = input(f"Statistics Filename [default: {default_stat}]: ") or default_stat

            print("Loading statistics...")
            stats_data = ct.read_stats_from_file(filename, progress_callback=ct.terminal_progress_bar)

            if stats_data:
                print("Opening analysis panel...")
                print("(Close the plot window to return to menu)")
                ct.plot_graph(stats_data, in_window=True)
                print("--- Panel closed ---")

        else:
            print("Invalid selection. Try again.")


if __name__ == "__main__":
    main()

