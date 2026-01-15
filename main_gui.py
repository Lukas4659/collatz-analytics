import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
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
            pass  # Ignore errors if widget is destroyed

    def flush(self):
        pass


class CollatzApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Setup
        self.title("Collatz Analytics System v2.4")
        self.geometry("1200x850")
        self.iconbitmap(self.resource_path("ikona.ico"))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables for Data Management
        self.full_stats_data = []  # Copy of ALL generated data
        self.current_display_data = []  # Data currently shown (filtered/sorted)
        self.raw_sequences = []  # Raw sequences for line plots

        self.sort_descending = False  # Toggle for sorting
        self.last_sorted_col = None  # To track which column was last sorted

        # 2. Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)  # Spacer to push bottom items
        self.setup_sidebar()

        # 3. Main Content Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Log area expands
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.setup_main_area()

        # 4. Redirect Console
        sys.stdout = TextRedirector(self.log_box, "stdout")
        sys.stderr = TextRedirector(self.log_box, "stderr")

        print("--- System Ready ---")
        print("Welcome to Collatz Analytics.")

    def resource_path(self, relative_path):
        """ Get absolute path to resource for Dev and PyInstaller """
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
                # Load smaller for logo
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

        # --- EASTER EGG CONTAINER (SIDEBAR) ---
        # This is an empty frame that will hold the image when triggered
        self.easter_egg_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.easter_egg_frame.pack(padx=20, pady=10, fill="x")

        # --- BOTTOM CREDITS & EASTER EGG TRIGGER ---
        self.bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", pady=20)

        self.lbl_credits = ctk.CTkLabel(self.bottom_frame,
                                        text="Ver: 2.4 | Year: 2026\nAuthor: Lukas4659",
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

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        self.progress_bar.set(0)

        # Console Log
        self.log_box = ctk.CTkTextbox(self.main_frame, width=600, height=150, state="disabled", font=("Consolas", 12))
        self.log_box.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        # --- DATA MANAGEMENT PANEL (Filter/Sort) ---
        self.data_mgmt_frame = ctk.CTkFrame(self.main_frame)
        self.data_mgmt_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 0))

        # Filter Logic
        lbl_filter = ctk.CTkLabel(self.data_mgmt_frame, text="Filter Data:")
        lbl_filter.pack(side="left", padx=10, pady=5)

        self.combo_col = ctk.CTkComboBox(self.data_mgmt_frame,
                                         values=["Start", "Length", "Max_Value", "Glide_Time", "Parity_Even_Pct"],
                                         width=120)
        self.combo_col.pack(side="left", padx=5)
        self.combo_col.set("Max_Value")

        self.combo_op = ctk.CTkComboBox(self.data_mgmt_frame, values=[">", "<", "="], width=60)
        self.combo_op.pack(side="left", padx=5)
        self.combo_op.set(">")

        self.entry_val = ctk.CTkEntry(self.data_mgmt_frame, placeholder_text="Value", width=100)
        self.entry_val.pack(side="left", padx=5)

        self.btn_filter = ctk.CTkButton(self.data_mgmt_frame, text="Apply Filter", width=100, command=self.apply_filter)
        self.btn_filter.pack(side="left", padx=10)

        self.btn_reset = ctk.CTkButton(self.data_mgmt_frame, text="Reset / Show All", width=100, fg_color="gray",
                                       command=self.reset_filter)
        self.btn_reset.pack(side="left", padx=5)

        self.lbl_count = ctk.CTkLabel(self.data_mgmt_frame, text="Rows: 0", text_color="gray70")
        self.lbl_count.pack(side="right", padx=15)

        # --- TABLE ---
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.tree_scroll_y = ttk.Scrollbar(self.table_frame)
        self.tree_scroll_y.pack(side="right", fill="y")

        self.table_columns = ("Start", "Length", "Max_Value", "Average", "Median", "Glide_Time", "Parity_Even_Pct")

        self.tree = ttk.Treeview(self.table_frame, columns=self.table_columns, show="headings",
                                 yscrollcommand=self.tree_scroll_y.set)

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        # Bind Headers for Sorting
        for col in self.table_columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_data_by_column(c))
            self.tree.column(col, width=90, anchor="center")

    # --- EASTER EGG LOGIC ---
    def open_easter_egg(self, event):
        # 1. Check if already open (if frame has children widgets)
        if self.easter_egg_frame.winfo_children():
            return

        try:
            img_path = self.resource_path("Ptys.jpg")
            if not os.path.exists(img_path):
                img_path = self.resource_path("Ptys.png")

            if not os.path.exists(img_path):
                messagebox.showerror("Error", "Ptyś image not found!")
                return

            # 2. Load and Resize Image to fit sidebar
            pil_img = Image.open(img_path)
            # Sidebar is ~250px wide. Let's target 210px width for image and calculate height.
            target_width = 210
            width_percent = (target_width / float(pil_img.size[0]))
            target_height = int((float(pil_img.size[1]) * float(width_percent)))

            # Use CTkImage for better scaling in CustomTkinter
            my_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_width, target_height))

            # 3. Create Close Button
            # Using a small red button positioned to the right
            btn_close = ctk.CTkButton(self.easter_egg_frame, text="Close ✕", width=60, height=20,
                                      fg_color="#c9302c", hover_color="#a82824",  # Red colors
                                      font=ctk.CTkFont(size=11),
                                      command=self.close_easter_egg)
            btn_close.pack(anchor="e", pady=(0, 5))  # Anchor east (right)

            # 4. Create and pack the image label inside the container frame
            lbl_img = ctk.CTkLabel(self.easter_egg_frame, image=my_image, text="")
            lbl_img.pack()

        except Exception as e:
            print(f"Easter egg broken: {e}")

    def close_easter_egg(self):
        """ Clears the easter egg frame, effectively hiding the image """
        for widget in self.easter_egg_frame.winfo_children():
            widget.destroy()

    # --- LOGIC: GENERATION ---
    def start_generation_thread(self):
        try:
            start = int(self.entry_start.get())
            end = int(self.entry_end.get())
            if start <= 0 or end <= 0: raise ValueError

            self.btn_generate.configure(state="disabled")
            self.progress_bar.set(0)

            threading.Thread(target=self.run_generation_process, args=(start, end), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive integers.")

    def run_generation_process(self, start, end):
        try:
            print(f"\n>>> Generating range {start}-{end}...")

            def progress_update(current, total):
                self.progress_bar.set(current / total)

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
        self.refresh_table()
        print(f">>> Done. {len(self.current_display_data)} records ready.")
        messagebox.showinfo("Success", "Data ready!")

    # --- LOGIC: TABLE & FILTERING ---

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        count = len(self.current_display_data)
        self.lbl_count.configure(text=f"Rows: {count}")

        limit = 5000
        if count > limit:
            print(f"Displaying first {limit} rows (total {count}) to prevent lag...")

        for i, row in enumerate(self.current_display_data):
            if i >= limit: break
            vals = (row['Start'], row['Length'], row['Max_Value'],
                    row['Average'], row['Median'], row['Glide_Time'], row['Parity_Even_Pct'])
            self.tree.insert("", "end", values=vals)

    def sort_data_by_column(self, col_name):
        if self.last_sorted_col == col_name:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_descending = False
            self.last_sorted_col = col_name

        print(f"Sorting by {col_name} ({'DESC' if self.sort_descending else 'ASC'})...")

        for col in self.table_columns:
            if col == col_name:
                arrow = "▼" if self.sort_descending else "▲"
                self.tree.heading(col, text=f"{col} {arrow}")
            else:
                self.tree.heading(col, text=col)

        try:
            self.current_display_data.sort(
                key=lambda x: x[col_name],
                reverse=self.sort_descending
            )
            self.refresh_table()
        except KeyError:
            print(f"Error sorting by {col_name}")

    def apply_filter(self):
        col = self.combo_col.get()
        op = self.combo_op.get()
        val_str = self.entry_val.get()

        if not self.full_stats_data:
            print("No data to filter.")
            return

        try:
            val = float(val_str)
            print(f"Filtering: {col} {op} {val}")

            new_data = []
            for row in self.full_stats_data:
                row_val = row[col]
                match = False
                if op == ">":
                    match = row_val > val
                elif op == "<":
                    match = row_val < val
                elif op == "=":
                    match = row_val == val

                if match:
                    new_data.append(row)

            self.current_display_data = new_data
            self.refresh_table()
            print(f"Filter applied. {len(new_data)} rows remaining.")

        except ValueError:
            messagebox.showerror("Filter Error", "Please enter a numeric value.")

    def reset_filter(self):
        if not self.full_stats_data: return
        print("Filter reset. Showing all data.")
        self.current_display_data = self.full_stats_data.copy()
        self.refresh_table()

        for col in self.table_columns:
            self.tree.heading(col, text=col)
        self.last_sorted_col = None

    # --- VISUALIZATION ---
    def show_stats_dashboard(self):
        if not self.current_display_data:
            messagebox.showwarning("No Data", "Table is empty. Generate or Load data.")
            return

        print(f"Opening Stats Dashboard for {len(self.current_display_data)} records...")
        ct.plot_graph(self.current_display_data, in_window=True)

    def show_trajectory_plot(self):
        if not self.raw_sequences:
            messagebox.showwarning("No Data", "No raw sequences available.")
            return

        if len(self.current_display_data) != len(self.full_stats_data):
            print("Note: Filtering trajectories based on table results...")
            allowed_starts = set(row['Start'] for row in self.current_display_data)
            filtered_seqs = [seq for seq in self.raw_sequences if seq[0] in allowed_starts]
            ct.plot_graph(filtered_seqs, in_window=True)
        else:
            ct.plot_graph(self.raw_sequences, in_window=True)

    # --- FILE I/O ---
    def load_from_file(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filename: return

        print(f"Loading: {filename}...")
        threading.Thread(target=self._load_thread, args=(filename,), daemon=True).start()

    def _load_thread(self, filename):
        try:
            stats = ct.read_stats_from_file(filename)
            if stats:
                self.full_stats_data = stats
                self.current_display_data = stats.copy()
                self.raw_sequences = []
                self.after(0, self.on_generation_complete)
            else:
                print("Could not load stats. Trying as sequences...")
                seqs = ct.read_sequences_from_file(filename)
                if seqs:
                    self.raw_sequences = seqs
                    self.full_stats_data = ct.analyze_sequence_dataset(seqs)
                    self.current_display_data = self.full_stats_data.copy()
                    self.after(0, self.on_generation_complete)
        except Exception as e:
            print(f"Load error: {e}")


if __name__ == "__main__":
    app = CollatzApp()
    app.mainloop()