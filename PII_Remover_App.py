import logging
import tkinter as tk
from tkinter import ttk
import time
from tkinter import filedialog, messagebox
from script import remove_pii_from_excel

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_file():
    input_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not input_file:
        return
    output_file = input_file.replace(".xlsx", "_cleaned.xlsx")
    try:
        remove_pii_from_excel(input_file, output_file)
        messagebox.showinfo("Success", f"File cleaned and saved as {output_file}")
    except Exception as e:
        logging.error("Error during PII removal", exc_info=True)
        messagebox.showerror("Error", "An error occurred. Check app.log for details.")

    app = tk.Tk()
    app.title("PII Remover")
    tk.Label(app, text="Upload an Excel file to remove PII").pack(pady=10)
    tk.Button(app, text="Select File", command=process_file).pack(pady=10)
    app.mainloop()

def process_file():
    # Open file dialog to select the Excel file
    input_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not input_file:
        return  # Exit if no file is selected

    # Set the output file name
    output_file = input_file.replace(".xlsx", "_cleaned.xlsx")
    
    try:
        # Call the PII removal function
        remove_pii_from_excel(input_file, output_file)
        messagebox.showinfo("Success", f"File cleaned and saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def show_progress():
    # Create a progress window
    progress_window = tk.Tk()
    progress_window.overrideredirect(True)
    progress_window.geometry("300x100")
    progress_label = tk.Label(progress_window, text="Loading PII Remover...", font=("Arial", 14), bg="#f8f9fa")
    progress_label.pack(pady=10)

    # Create a progress bar
    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=250, mode="indeterminate")
    progress_bar.pack(pady=10)
    progress_bar.start(10)  # Start progress bar animation

    # Center the progress window
    screen_width = progress_window.winfo_screenwidth()
    screen_height = progress_window.winfo_screenheight()
    x = (screen_width // 2) - (300 // 2)
    y = (screen_height // 2) - (100 // 2)
    progress_window.geometry(f"+{x}+{y}")

    # Simulate loading for a few seconds
    progress_window.update()
    time.sleep(3)  # Adjust duration as needed
    progress_bar.stop()
    progress_window.destroy()

if __name__ == "__main__":
    try:
        # Show progress bar
        show_progress()

        # Create the main GUI window
        app = tk.Tk()
        app.title("PII Remover")
        app.geometry("600x350")  # Adjusted window size for better layout
        app.configure(bg="#f8f9fa")  # Light gray background

        # Add a frame to center the content
        frame = tk.Frame(app, bg="#ffffff", padx=20, pady=20, relief="raised", borderwidth=2)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Add a title to the app
        title_label = tk.Label(frame, text="PII Remover", font=("Arial", 18, "bold"), bg="#ffffff", fg="#333333")
        title_label.pack(pady=(10, 5))

        # Add a description
        description_label = tk.Label(
            frame,
            text="Select an Excel file to remove Personally Identifiable Information (PII).\n"
                 "The cleaned file will be saved in the same location as the input file.\n"
                 "Important: Place your PII in an excel file column named 'comment'."
,
            font=("Arial", 12),
            bg="#ffffff",
            fg="#555555",
            justify="center",
            wraplength=500,
        )
        description_label.pack(pady=(5, 20))

        # Add a button to process the file
        button = tk.Button(
            frame,
            text="Select File",
            command=process_file,
            font=("Arial", 14),
            bg="#007bff",
            fg="#ffffff",
            activebackground="#0056b3",
            activeforeground="#ffffff",
            relief="flat",
            padx=10,
            pady=5,
        )
        button.pack(pady=10)

        # Add footer text
        footer_label = tk.Label(frame, text="Made for OCTO's secure data handling needs!", font=("Arial", 10),
                                bg="#ffffff", fg="#999999")
        footer_label.pack(pady=(20, 10))

        # Run the application
        app.mainloop()

    except Exception as e:
        logging.error("Fatal error in main loop", exc_info=True)
