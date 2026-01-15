import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import time  # <--- NEW IMPORT
from PIL import Image, ImageTk

# Import our backend tools
import collatz_tools as ct

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class TextRedirector:
    """ Redirects print() to UI textbox """

    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str_val):
        try:
            self.widget.configure(state="normal")
            self.widget.insert("end", str_val)
            self.widget.see("end")
            self.widget.configure(state="disabled")
        except:
            pass

    def flush(self):
        pass


class CollatzApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Setup
        self.title("Collatz Analytics System v2.7")  # Version bump
        self.geometry("1200x950")
        self.iconbitmap(self.resource_path("ikona.ico"))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables for Data Management
        self.full_stats_data = []
        self.current_display_data = []
        self.raw_sequences = []

        self.sort_descending = False
        self.last_sorted_col = None

        # List to store filter widgets references for multiple rows
        self.filter_rows = []

        # 2. Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        self.setup_sidebar()

        # 3. Main Content Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Grid config
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        self.setup_main_area()

        # 4. Redirect Console
        sys.stdout = TextRedirector(self.log_box, "stdout")
        sys.stderr = TextRedirector(self.log_box, "stderr")

        print("--- System Ready ---")
        print("Welcome to Collatz Analytics.")

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def setup_sidebar(self):
        # --- LOGO ---
        try:
            img_path = self.resource_path("Ptys.jpg")
            if os.path.exists(img_path):
                pil_img = Image.open(img_path)
                my_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))
                self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=my_image, text="")
                self.logo_label.pack(pady=(20, 10))
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")

        lbl_title = ctk.CTkLabel(self.sidebar_frame, text="CONTROL PANEL", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_title.pack(padx=20, pady=10)

        # --- GENERATION ---
        lbl_gen = ctk.CTkLabel(self.sidebar_frame, text="1. Data Generation", anchor="w",
                               font=ctk.CTkFont(weight="bold"))
        lbl_gen.pack(padx=20, pady=(10, 0), fill="x")

        self.entry_start = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Start (e.g. 1)")
        self.entry_start.pack(padx=20, pady=5)
        self.entry_end = ctk.CTkEntry(self.sidebar_frame, placeholder_text="End (e.g. 1000)")
        self.entry_end.pack(padx=20, pady=5)

        self.btn_generate = ctk.CTkButton(self.sidebar_frame, text="Generate Data",
                                          command=self.start_generation_thread)
        self.btn_generate.pack(padx=20, pady=10)

        # --- VISUALIZATION ---
        lbl_viz = ctk.CTkLabel(self.sidebar_frame, text="2. Visualization", anchor="w", font=ctk.CTkFont(weight="bold"))
        lbl_viz.pack(padx=20, pady=(20, 0), fill="x")

        self.btn_plot_seq = ctk.CTkButton(self.sidebar_frame, text="Plot Trajectories",
                                          fg_color="transparent", border_width=2,
                                          command=self.show_trajectory_plot)
        self.btn_plot_seq.pack(padx=20, pady=5)

        self.btn_plot_stats = ctk.CTkButton(self.sidebar_frame, text="Show Statistics Dashboard",
                                            fg_color="transparent", border_width=2,
                                            command=self.show_stats_dashboard)
        self.btn_plot_stats.pack(padx=20, pady=5)

        # --- FILE I/O ---
        lbl_io = ctk.CTkLabel(self.sidebar_frame, text="3. File Operations", anchor="w",
                              font=ctk.CTkFont(weight="bold"))
        lbl_io.pack(padx=20, pady=(20, 0), fill="x")

        self.btn_load_csv = ctk.CTkButton(self.sidebar_frame, text="Load External CSV", command=self.load_from_file)
        self.btn_load_csv.pack(padx=20, pady=10)

        # --- EASTER EGG CONTAINER ---
        self.easter_egg_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.easter_egg_frame.pack(padx=20, pady=10, fill="x")

        # --- BOTTOM CREDITS ---
        self.bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", pady=20)

        self.lbl_credits = ctk.CTkLabel(self.bottom_frame,
                                        text="Ver: 2.7 | Year: 2026\nAuthor: Lukas4659",
                                        font=("Arial", 10), text_color="gray60")
        self.lbl_credits.pack(pady=(0, 5))

        self.lbl_ptys = ctk.CTkLabel(self.bottom_frame, text="Ptyś",
                                     text_color="gray30", font=("Arial", 10, "italic"), cursor="hand2")
        self.lbl_ptys.pack()
        self.lbl_ptys.bind("<Button-1>", self.open_easter_egg)

    def setup_main_area(self):
        # Header
        self.lbl_header = ctk.CTkLabel(self.main_frame, text="Operation Log & Results",
                                       font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        # --- PROGRESS AREA (Modified) ---
        # Container frame for Bar + ETA Label
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.progress_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", pady=(0, 2))
        self.progress_bar.set(0)

        # ETA Label (Small, right-aligned)
        self.lbl_eta = ctk.CTkLabel(self.progress_frame, text="Time Remaining: --:--",
                                    font=ctk.CTkFont(size=11), text_color="gray70")
        self.lbl_eta.pack(anchor="e")  # Anchor East (Right)

        # Logs
        self.log_box = ctk.CTkTextbox(self.main_frame, width=600, height=150, state="disabled", font=("Consolas", 12))
        self.log_box.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        # --- ADVANCED FILTERING PANEL ---
        self.data_mgmt_frame = ctk.CTkFrame(self.main_frame)
        self.data_mgmt_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 0))

        self.create_filter_row(row_idx=0, label_text="Filter 1:")
        self.create_filter_row(row_idx=1, label_text="Filter 2 (Nested):")
        self.create_filter_row(row_idx=2, label_text="Filter 3 (Nested):")

        # Apply / Reset Buttons
        btn_frame = ctk.CTkFrame(self.data_mgmt_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=5, rowspan=3, padx=20, pady=5, sticky="ns")

        self.btn_filter = ctk.CTkButton(btn_frame, text="Apply Filters", width=120, height=40,
                                        fg_color="green", hover_color="darkgreen",
                                        command=self.apply_advanced_filters)
        self.btn_filter.pack(pady=5)

        self.btn_reset = ctk.CTkButton(btn_frame, text="Reset All", width=120,
                                       fg_color="gray", command=self.reset_filter)
        self.btn_reset.pack(pady=5)

        self.lbl_count = ctk.CTkLabel(btn_frame, text="Rows: 0", text_color="gray70")
        self.lbl_count.pack(pady=5)

        # --- TABLE ---
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.tree_scroll_y = ttk.Scrollbar(self.table_frame)
        self.tree_scroll_y.pack(side="right", fill="y")

        self.table_columns = ("Start", "Length", "Max_Value", "Average", "Median", "Glide_Time", "Parity_Even_Pct")

        self.tree = ttk.Treeview(self.table_frame, columns=self.table_columns, show="headings",
                                 yscrollcommand=self.tree_scroll_y.set)

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        for col in self.table_columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_data_by_column(c))
            self.tree.column(col, width=90, anchor="center")

    def create_filter_row(self, row_idx, label_text):
        """ Helper to build a standardized filter row """
        lbl = ctk.CTkLabel(self.data_mgmt_frame, text=label_text, font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")

        combo_col = ctk.CTkComboBox(self.data_mgmt_frame,
                                    values=["Start", "Length", "Max_Value", "Glide_Time", "Parity_Even_Pct"], width=130)
        combo_col.grid(row=row_idx, column=1, padx=5, pady=5)
        combo_col.set("Max_Value")

        combo_op = ctk.CTkComboBox(self.data_mgmt_frame, values=[">", "<", "=", "Range"], width=80)
        combo_op.grid(row=row_idx, column=2, padx=5, pady=5)
        combo_op.set(">")

        entry1 = ctk.CTkEntry(self.data_mgmt_frame, placeholder_text="Val / Min", width=100)
        entry1.grid(row=row_idx, column=3, padx=5, pady=5)

        entry2 = ctk.CTkEntry(self.data_mgmt_frame, placeholder_text="Max", width=100)
        entry2.grid(row=row_idx, column=4, padx=5, pady=5)
        entry2.configure(state="disabled", fg_color="gray25")

        def on_op_change(choice):
            if choice == "Range":
                entry2.configure(state="normal", fg_color=["#F9F9FA", "#343638"])
            else:
                entry2.delete(0, "end")
                entry2.configure(state="disabled", fg_color="gray25")

        combo_op.configure(command=on_op_change)

        self.filter_rows.append({
            "col": combo_col,
            "op": combo_op,
            "val1": entry1,
            "val2": entry2
        })

    # --- EASTER EGG ---
    def open_easter_egg(self, event):
        if self.easter_egg_frame.winfo_children(): return
        try:
            img_path = self.resource_path("Ptys.jpg")
            if not os.path.exists(img_path): img_path = self.resource_path("Ptys.png")
            if not os.path.exists(img_path):
                messagebox.showerror("Error", "Ptyś not found!")
                return

            pil_img = Image.open(img_path)
            target_width = 210
            width_percent = (target_width / float(pil_img.size[0]))
            target_height = int((float(pil_img.size[1]) * float(width_percent)))
            my_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_width, target_height))

            btn_close = ctk.CTkButton(self.easter_egg_frame, text="Close ✕", width=60, height=20,
                                      fg_color="#c9302c", hover_color="#a82824",
                                      font=ctk.CTkFont(size=11), command=self.close_easter_egg)
            btn_close.pack(anchor="e", pady=(0, 5))
            ctk.CTkLabel(self.easter_egg_frame, image=my_image, text="").pack()
        except Exception:
            pass

    def close_easter_egg(self):
        for w in self.easter_egg_frame.winfo_children(): w.destroy()

    # --- GENERATION ---
    def start_generation_thread(self):
        try:
            s, e = int(self.entry_start.get()), int(self.entry_end.get())
            if s <= 0 or e <= 0: raise ValueError
            self.btn_generate.configure(state="disabled")
            self.progress_bar.set(0)
            self.lbl_eta.configure(text="Calculating ETA...")  # Reset text
            threading.Thread(target=self.run_generation_process, args=(s, e), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Invalid integers.")

    def run_generation_process(self, start, end):
        try:
            print(f"\n>>> Generating {start}-{end}...")

            # --- ETA LOGIC START ---
            start_time = time.time()
            total_items = end - start + 1

            def progress_update(current, total):
                # Update bar
                self.progress_bar.set(current / total)

                # Calculate ETA (only every ~50 items to save resources, or if it's the end)
                # Since 'current' is simple counter, let's update frequently but safely.
                # collatz_tools updates every 100 items by default, so we are safe to do math here.

                elapsed = time.time() - start_time
                if elapsed > 0 and current > 0:
                    rate = current / elapsed  # items per second
                    remaining_items = total - current
                    eta_seconds = remaining_items / rate

                    # Format time MM:SS
                    mins, secs = divmod(int(eta_seconds), 60)
                    if mins > 60:
                        hrs, mins = divmod(mins, 60)
                        time_str = f"{hrs}h {mins}m {secs}s"
                    else:
                        time_str = f"{mins:02d}:{secs:02d}"

                    # Update label via main thread safety not strictly required for simple config,
                    # but good practice. Since we use threading, we should be careful.
                    # Tkinter is not thread-safe, but configure() usually works.
                    # Ideally: self.after(0, ...) but let's try direct update as CustomTkinter handles some of this.
                    if current % 10 == 0:  # Update text less frequently than bar
                        self.lbl_eta.configure(text=f"ETA: {time_str} ({int(rate)} seq/s)")

            # --- ETA LOGIC END ---

            self.raw_sequences = ct.calculate_all_sequences(start, end, progress_callback=progress_update)
            print("Status: Calculating statistics...")
            self.full_stats_data = ct.analyze_sequence_dataset(self.raw_sequences)
            self.current_display_data = self.full_stats_data.copy()
            self.after(0, self.on_generation_complete)
        except Exception as e:
            print(f"Error: {e}")
            self.after(0, lambda: self.btn_generate.configure(state="normal"))

    def on_generation_complete(self):
        self.btn_generate.configure(state="normal")
        self.lbl_eta.configure(text="Status: Completed")
        self.refresh_table()
        print(f">>> Done. {len(self.current_display_data)} records.")
        messagebox.showinfo("Success", "Data ready!")

    # --- TABLE & FILTERING ---
    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        count = len(self.current_display_data)
        self.lbl_count.configure(text=f"Rows: {count}")
        limit = 5000
        if count > limit: print(f"Displaying first {limit} rows...")
        for i, row in enumerate(self.current_display_data):
            if i >= limit: break
            vals = (row['Start'], row['Length'], row['Max_Value'], row['Average'], row['Median'], row['Glide_Time'],
                    row['Parity_Even_Pct'])
            self.tree.insert("", "end", values=vals)

    def sort_data_by_column(self, col_name):
        if self.last_sorted_col == col_name:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_descending = False; self.last_sorted_col = col_name

        for col in self.table_columns:
            if col == col_name:
                self.tree.heading(col, text=f"{col} {'▼' if self.sort_descending else '▲'}")
            else:
                self.tree.heading(col, text=col)

        self.current_display_data.sort(key=lambda x: x[col_name], reverse=self.sort_descending)
        self.refresh_table()

    def apply_advanced_filters(self):
        if not self.full_stats_data: return
        dataset = self.full_stats_data.copy()
        for i, f_row in enumerate(self.filter_rows):
            col = f_row["col"].get()
            op = f_row["op"].get()
            val1_str = f_row["val1"].get()
            val2_str = f_row["val2"].get()

            if not val1_str: continue

            try:
                val1 = float(val1_str)
                print(f"Applying Filter {i + 1}: {col} {op} {val1} ...")

                filtered_subset = []
                for row in dataset:
                    row_val = row[col]
                    match = False
                    if op == ">":
                        match = row_val > val1
                    elif op == "<":
                        match = row_val < val1
                    elif op == "=":
                        match = row_val == val1
                    elif op == "Range":
                        if not val2_str:
                            match = True
                        else:
                            match = val1 <= row_val <= float(val2_str)

                    if match: filtered_subset.append(row)
                dataset = filtered_subset
            except ValueError:
                messagebox.showerror("Filter Error", f"Invalid number in Filter {i + 1}")
                return

        self.current_display_data = dataset
        self.refresh_table()
        print(f"Filters applied. Remaining rows: {len(dataset)}")

    def reset_filter(self):
        if not self.full_stats_data: return
        self.current_display_data = self.full_stats_data.copy()

        for f_row in self.filter_rows:
            f_row["val1"].delete(0, "end")
            f_row["val2"].delete(0, "end")
            f_row["op"].set(">")
            f_row["val2"].configure(state="disabled", fg_color="gray25")

        self.refresh_table()
        for col in self.table_columns: self.tree.heading(col, text=col)
        self.last_sorted_col = None

    # --- VISUALIZATION ---
    def show_stats_dashboard(self):
        if not self.current_display_data:
            messagebox.showwarning("No Data", "Table empty.")
            return
        ct.plot_graph(self.current_display_data, in_window=True)

    def show_trajectory_plot(self):
        if not self.raw_sequences:
            messagebox.showwarning("No Data", "No raw sequences.")
            return
        if len(self.current_display_data) != len(self.full_stats_data):
            allowed_starts = set(row['Start'] for row in self.current_display_data)
            filtered_seqs = [seq for seq in self.raw_sequences if seq[0] in allowed_starts]
            ct.plot_graph(filtered_seqs, in_window=True)
        else:
            ct.plot_graph(self.raw_sequences, in_window=True)

    # --- IO ---
    def load_from_file(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename: threading.Thread(target=self._load_thread, args=(filename,), daemon=True).start()

    def _load_thread(self, filename):
        try:
            stats = ct.read_stats_from_file(filename)
            if stats:
                self.full_stats_data = stats
                self.current_display_data = stats.copy()
                self.raw_sequences = []
                self.after(0, self.on_generation_complete)
            else:
                seqs = ct.read_sequences_from_file(filename)
                if seqs:
                    self.raw_sequences = seqs
                    self.full_stats_data = ct.analyze_sequence_dataset(seqs)
                    self.current_display_data = self.full_stats_data.copy()
                    self.after(0, self.on_generation_complete)
        except Exception:
            pass


if __name__ == "__main__":
    app = CollatzApp()
    app.mainloop()