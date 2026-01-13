"""
Collatz Problem Analysis Tools.

This module contains a set of calculation, statistical, and visualization functions
dedicated to investigating the 3n+1 hypothesis. It handles CSV file operations,
progress bar generation, and rendering of advanced correlation charts.
"""

import csv
import statistics
import tkinter as tk
from itertools import zip_longest
from typing import List, Tuple, Dict, Optional, Callable, Any
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# CONSTANTS
DIVISOR_EVEN = 2
MULTIPLIER_ODD = 3
ADDEND_ODD = 1
DEFAULT_FILENAME = "Collatz_data_range.csv"


# --- Helper and Interface Functions ---

def display_info() -> None:
    """Displays the rules of the Collatz problem to the console."""
    print("---------------------------------------")
    print("Collatz Problem - Tools")
    print("---------------------------------------")


def display_stats_in_terminal(stats: Dict[str, Any]) -> None:
    """
    Formats and displays a single statistics record in the terminal.
    """
    print(f"\n--- Statistics for number: {stats['Start']} ---")
    print(f"Steps (Length): {stats['Length']}")
    print(f"Max Value: {stats['Max_Value']}")
    print(f"Max Index (Step): {stats['Max_Index']}")
    print(f"Average: {stats['Average']}")
    print(f"Median: {stats['Median']}")
    print(f"Expansion Coeff: {stats['Expansion_X']:.2f}")
    print(f"Glide Time: {stats['Glide_Time']}")
    print(f"Parity: {stats['Parity_Even_Pct']:.1f}% even")


def terminal_progress_bar(current: int, total: int) -> None:
    """
    A simple progress bar displayed in the terminal using sys.stdout.
    """
    if total == 0: return
    percent = 100 * (current / float(total))
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {percent:.1f}% Complete')
    sys.stdout.flush()
    if current == total:
        sys.stdout.write('\n')


def get_data_range_input() -> Tuple[int, int]:
    """
    Prompts the user to enter a range of numbers (start and end).
    """
    while True:
        try:
            n1 = int(input("Enter range START: "))
            n2 = int(input("Enter range END: "))
            if n1 > 0 and n2 > 0:
                if n1 > n2:
                    print("Start must be less than or equal to End. Swapping...")
                    n1, n2 = n2, n1
                return n1, n2
            else:
                print("Numbers must be natural (positive integers).")
        except ValueError:
            print("Invalid input. Please enter integers.")


# --- Core Calculation Logic ---

def calculate_next_step(n: int) -> int:
    """Calculates the next term in the Collatz sequence."""
    if n % 2 == 0:
        return n // DIVISOR_EVEN
    else:
        return n * MULTIPLIER_ODD + ADDEND_ODD


def generate_collatz_sequence(start_n: int) -> List[int]:
    """Generates a full Collatz sequence for a given starting number."""
    sequence = [start_n]
    current = start_n
    while current != 1:
        current = calculate_next_step(current)
        sequence.append(current)
    return sequence


def calculate_all_sequences(start: int, end: int, progress_callback: Optional[Callable] = None) -> List[List[int]]:
    """Generates Collatz sequences for a range of numbers [start, end]."""
    all_data = []
    total = end - start + 1
    count = 0

    for i in range(start, end + 1):
        seq = generate_collatz_sequence(i)
        all_data.append(seq)
        count += 1
        if progress_callback:
            progress_callback(count, total)

    return all_data


# --- File Operations (I/O) ---

def save_sequences_to_file(data: List[List[int]], filename: str = DEFAULT_FILENAME,
                           progress_callback: Optional[Callable] = None) -> None:
    """Saves sequences to a CSV file (transposed)."""
    print(f"Transposing data for CSV format (Columns = Sequences)...")
    transposed_data = list(zip_longest(*data, fillvalue=""))

    total_rows = len(transposed_data)
    print(f"Saving to file: {filename}...")

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        headers = [f"Seq_{seq[0]}" for seq in data]
        writer.writerow(headers)

        for i, row in enumerate(transposed_data):
            writer.writerow(row)
            if progress_callback and i % 100 == 0:
                progress_callback(i + 1, total_rows)

        if progress_callback:
            progress_callback(total_rows, total_rows)

    print("\nFile saved successfully.")


def read_sequences_from_file(filename: str, progress_callback: Optional[Callable] = None) -> List[List[int]]:
    """Reads sequences from a CSV file."""
    sequences = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            headers = next(reader)

            num_columns = len(headers)
            temp_columns = [[] for _ in range(num_columns)]

            rows = list(reader)
            total_rows = len(rows)

            for i, row in enumerate(rows):
                for col_index, val in enumerate(row):
                    if val:
                        temp_columns[col_index].append(int(val))

                if progress_callback and i % 1000 == 0:
                    progress_callback(i + 1, total_rows)

            sequences = temp_columns
            return sequences

    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return []
    except Exception as e:
        print(f"Read error: {e}")
        return []


def read_stats_from_file(filename: str, progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """Reads the statistics report from a CSV file."""
    stats_list = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            total = len(rows)

            for i, row in enumerate(rows):
                try:
                    row['Start'] = int(row['Start'])
                    row['Length'] = int(row['Length'])
                    row['Max_Value'] = int(row['Max_Value'])
                    row['Max_Index'] = int(row['Max_Index'])
                    row['Average'] = float(row['Average'])
                    row['Median'] = float(row['Median'])
                    row['Expansion_X'] = float(row['Expansion_X'])
                    row['Glide_Time'] = int(row['Glide_Time'])
                    row['Parity_Even_Pct'] = float(row['Parity_Even_Pct'])
                    stats_list.append(row)
                except ValueError:
                    continue

                if progress_callback and i % 100 == 0:
                    progress_callback(i + 1, total)

        return stats_list
    except FileNotFoundError:
        print("Statistics file not found.")
        return []


# --- Statistics and Analysis ---

def calculate_glide_time(sequence: List[int]) -> int:
    """Calculates Glide Time."""
    start_val = sequence[0]
    for i, val in enumerate(sequence):
        if i == 0: continue
        if val < start_val:
            return i
    return 0


def analyze_sequence_dataset(sequences: List[List[int]]) -> List[Dict[str, Any]]:
    """Calculates detailed statistics for a list of sequences."""
    stats_results = []

    for seq in sequences:
        if not seq: continue

        start = seq[0]
        length = len(seq)
        max_val = max(seq)
        max_idx = seq.index(max_val)
        avg_val = statistics.mean(seq)
        median_val = statistics.median(seq)
        expansion = max_val / start if start != 0 else 0
        glide = calculate_glide_time(seq)
        evens = sum(1 for x in seq if x % 2 == 0)
        parity_pct = (evens / length) * 100

        # Mapping Polish keys concept to English Keys
        record = {
            "Start": start,
            "Length": length,
            "Max_Value": max_val,
            "Max_Index": max_idx,  # Krok_Max
            "Average": round(avg_val, 2),
            "Median": median_val,
            "Expansion_X": round(expansion, 2),
            "Glide_Time": glide,
            "Parity_Even_Pct": round(parity_pct, 2)
        }
        stats_results.append(record)

    return stats_results


def save_stats_to_csv(stats_list: List[Dict[str, Any]], filename: str) -> None:
    """Saves the list of statistics dictionaries to a CSV file."""
    if not stats_list:
        print("No statistics to save.")
        return

    keys = stats_list[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(stats_list)
    print(f"Statistics report saved to: {filename}")


# --- Visualization ---

def plot_graph(data_source: Any, in_window: bool = True, progress_callback: Optional[Callable] = None) -> None:
    """
    Draws a graph.
    Mode 1: Sequences -> Line Plot.
    Mode 2: Stats -> 3x3 Grid showing ALL metrics.
    """

    mode = "unknown"
    if not data_source:
        print("No data to display.")
        return

    # Wykrywanie trybu na podstawie typu danych
    if isinstance(data_source[0], list):
        mode = "sequences"
    elif isinstance(data_source[0], dict):
        mode = "stats"

    fig = plt.Figure(figsize=(12, 9), dpi=90)

    # --- Mode 1: Sequences ---
    if mode == "sequences":
        ax = fig.add_subplot(111)
        limit = 500
        if len(data_source) > limit:
            print(f"Warning: Displaying only first {limit} sequences.")
            to_plot = data_source[:limit]
        else:
            to_plot = data_source

        for seq in to_plot:
            ax.plot(seq, alpha=0.6, linewidth=1)

        ax.set_title("Collatz Sequences Trajectories (Log Scale)")
        ax.set_xlabel("Step")
        ax.set_ylabel("Value (Log)")
        ax.set_yscale('log')
        ax.grid(True, which="both", ls="-", alpha=0.2)

    # --- Mode 2: Statistics (Full Dashboard) ---
    elif mode == "stats":
        fig.subplots_adjust(hspace=0.4, wspace=0.3)

        # Pobieranie danych
        starts = [d['Start'] for d in data_source]
        lengths = [d['Length'] for d in data_source]
        maxs = [d['Max_Value'] for d in data_source]
        max_idxs = [d['Max_Index'] for d in data_source]
        avgs = [d['Average'] for d in data_source]
        medians = [d['Median'] for d in data_source]
        expansions = [d['Expansion_X'] for d in data_source]
        glides = [d['Glide_Time'] for d in data_source]
        parities = [d['Parity_Even_Pct'] for d in data_source]

        # 1-8. Wykresy korelacji (Bez zmian)
        ax1 = fig.add_subplot(331)
        ax1.scatter(starts, lengths, s=1, c='blue', alpha=0.5)
        ax1.set_title("Start vs Length")
        ax1.set_ylabel("Steps")

        ax2 = fig.add_subplot(332)
        ax2.scatter(starts, maxs, s=1, c='red', alpha=0.5)
        ax2.set_title("Start vs Max Value")
        ax2.set_yscale('log')

        ax3 = fig.add_subplot(333)
        ax3.scatter(starts, glides, s=1, c='purple', alpha=0.5)
        ax3.set_title("Start vs Glide Time")

        ax4 = fig.add_subplot(334)
        ax4.scatter(starts, avgs, s=1, c='orange', alpha=0.5)
        ax4.set_title("Start vs Average Val")
        ax4.set_yscale('log')

        ax5 = fig.add_subplot(335)
        ax5.scatter(starts, medians, s=1, c='brown', alpha=0.5)
        ax5.set_title("Start vs Median Val")
        ax5.set_yscale('log')

        ax6 = fig.add_subplot(336)
        ax6.scatter(starts, max_idxs, s=1, c='cyan', alpha=0.5)
        ax6.set_title("Start vs Max Index")

        ax7 = fig.add_subplot(337)
        ax7.scatter(starts, parities, s=1, c='gray', alpha=0.5)
        ax7.set_title("Start vs Even %")
        ax7.set_ylabel("% Even")

        ax8 = fig.add_subplot(338)
        ax8.scatter(lengths, expansions, s=1, c='green', alpha=0.5)
        ax8.set_title("Steps vs Expansion")
        ax8.set_xlabel("Steps")

        # 9. Benford's Law (NAPRAWIONE)
        ax9 = fig.add_subplot(339)
        # Pobieramy pierwszą cyfrę z Max_Value
        first_digits = [int(str(m)[0]) for m in maxs]

        # Zliczamy wystąpienia cyfr 1-9
        digit_counts = {i: first_digits.count(i) for i in range(1, 10)}
        total_digits = len(first_digits)

        if total_digits > 0:
            # Obliczamy częstość
            freqs = [digit_counts[i] / total_digits for i in range(1, 10)]

            # Wzorzec Benforda (idealny)
            benford_ideal = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]

            x = range(1, 10)

            # Rysujemy słupki
            ax9.bar(x, freqs, alpha=0.6, label='Actual', color='#4444ff')
            # Rysujemy linię idealną
            ax9.plot(x, benford_ideal, 'r-o', label='Ideal', linewidth=2)

            # --- NAPRAWA OS I ETYKIET ---
            ax9.set_xticks(x)  # Wymuszamy zaznaczenie każdego punktu 1-9
            ax9.set_xticklabels(x)  # Podpisujemy je cyframi 1-9
            ax9.set_xlim(0.5, 9.5)  # Ustawiamy marginesy, żeby słupki nie dotykały ramek
            # ----------------------------

            ax9.set_title("Benford (Max Vals)")
            ax9.legend(fontsize='small')
        else:
            ax9.text(0.5, 0.5, "No Data", ha='center')

    fig.tight_layout()

    # --- Display Logic ---
    if not in_window:
        plt.show()
    else:
        root = tk.Tk()
        root.title("Collatz Analysis Report - Full Dashboard")
        root.geometry("1200x900")

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        canvas_cont = tk.Canvas(main_frame)
        canvas_cont.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        sb = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas_cont.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        canvas_cont.configure(yscrollcommand=sb.set)

        inner_frame = tk.Frame(canvas_cont)
        canvas_cont.create_window((0, 0), window=inner_frame, anchor="nw")

        def on_frame_configure(event):
            canvas_cont.configure(scrollregion=canvas_cont.bbox("all"))

        inner_frame.bind("<Configure>", on_frame_configure)

        canvas = FigureCanvasTkAgg(fig, master=inner_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        btn = tk.Button(inner_frame, text="Close Report", command=root.destroy, font=("Arial", 12, "bold"),
                        bg="#dddddd")
        btn.pack(pady=10)

        root.mainloop()
