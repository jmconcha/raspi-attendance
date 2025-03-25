import tkinter as tk
import ttkbootstrap as ttk

class App(ttk.Window):
    def __init__(self):
        super().__init__()
        self.title("Select Subject")
        self.geometry("300x200")

        options = ["Apple", "Banana", "Cherry", "Date", "Elderberry",
                   "Fig", "Grape", "Honeydew", "Kiwi", "Lemon",
                   "Mango", "Nectarine", "Orange", "Papaya", "Quince"]
        self.selected_var = tk.StringVar(value=options[0])  # Default selection

        # Use a Button instead of a Combobox
        self.dropdown_btn = ttk.Button(
            self, text=self.selected_var.get(), bootstyle="primary",
            command=lambda: self.open_dropdown(options)
        )
        self.dropdown_btn.pack(pady=20)

    def open_dropdown(self, options):
        """Opens a touchscreen-friendly popup with a Listbox and scrollbar."""
        popup = tk.Toplevel(self)
        popup.title("Select an Option")
        popup.geometry("250x300")
        popup.transient(self)

        # Frame to hold Listbox and Scrollbar
        frame = ttk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)

        # Listbox with scrollbar support
        listbox = tk.Listbox(frame, font=("Arial", 24), height=10, yscrollcommand=scrollbar.set)
        for option in options:
            listbox.insert(tk.END, option)

        # Configure scrollbar to scroll Listbox
        scrollbar.config(command=listbox.yview)

        # Layout
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind single click instead of double-click
        listbox.bind("<ButtonRelease-1>", lambda e: self.select_item(listbox, popup))

    def select_item(self, listbox, popup):
        """Set the selected item and close the popup."""
        try:
            selected_value = listbox.get(listbox.curselection())
            self.selected_var.set(selected_value)
            self.dropdown_btn.config(text=selected_value)  # Update button text
        except tk.TclError:
            pass  # No selection
        popup.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
