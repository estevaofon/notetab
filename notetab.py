import tkinter as tk
from tkinter import filedialog

class Notepad(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Notetab")

        self.text = tk.Text(self, wrap="word")
        self.text.pack(fill="both", expand=True)

        self.text.bind("<Control-z>", self.undo)
        self.text.bind("<Control-Z>", self.undo)
        self.text.bind("<Tab>", self.indent)
        self.text.bind("<Shift-Tab>", self.unindent)
        self.text.bind("<BackSpace>", self.backspace)
        self.text.bind("<Delete>", self.backspace)
        self.search_start = '1.0'

        self.undo_stack = []

        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

    def clear_search(self):
        self.text.tag_remove("sel", "1.0", "end")

    def search(self, search_string):
        self.clear_search()
        if self.search_start == "end":
            self.search_start = "1.0"
        pos = self.text.search(search_string, self.search_start, nocase=True, stopindex="end")
        self.text.focus()
        if pos:
            self.text.tag_remove("highlight", "1.0", "end")
            self.text.tag_add("highlight", pos, f"{pos} + {len(search_string)}c")
            self.text.see("insert")
            self.search_start = f"{pos} + {len(search_string)}c"
            self.text.tag_add("sel", pos, "{}+{}c".format(pos, len(search_string)))
        else:
            self.search_start = "end"

    def create_widgets(self):
        # ...
        self.show_search_replace = tk.BooleanVar()
        show_search_replace_checkbutton = tk.Checkbutton(self, text="Show Search/Replace", variable=self.show_search_replace, command=self.toggle_search_replace)
        show_search_replace_checkbutton.pack(side="top", fill="x")
        self.search_replace_frame = tk.Frame(self)
        self.search_replace_frame.pack(side="top", fill="x")
        search_entry = tk.Entry(self.search_replace_frame)
        search_entry.pack(side="left")
        search_button = tk.Button(self.search_replace_frame, text="Search", command=lambda: self.search(search_entry.get()))
        search_button.pack(side="left")
        replace_entry = tk.Entry(self.search_replace_frame)
        replace_entry.pack(side="left")
        replace_with_entry = tk.Entry(self.search_replace_frame)
        replace_with_entry.pack(side="left")
        replace_button = tk.Button(self.search_replace_frame, text="Replace", command=lambda: self.replace(replace_entry.get(), replace_with_entry.get()))
        replace_button.pack(side="right")
        self.toggle_search_replace()

    def toggle_search_replace(self):
        if self.show_search_replace.get():
            self.search_replace_frame.pack(side="top", fill="x")
        else:
            self.search_replace_frame.pack_forget()

    def open_file(self):
        filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            with open(filepath, "r") as file:
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", file.read().replace("\t", "    "))
                self.undo_stack = []

    def save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            with open(filepath, "w") as file:
                file.write(self.text.get("1.0", tk.END).replace("\t", "    "))

    def undo(self, event=None):
        if self.undo_stack:
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", self.undo_stack.pop().replace("\t", "    "))

    def get_selected_lines(self):
        try:
            start, end = self.text.index("sel.first"), self.text.index("sel.last")
        except tk.TclError:
            start, end = self.text.index("insert"), self.text.index("insert")

        start_line, _ = map(int, start.split("."))
        end_line, _ = map(int, end.split("."))

        return start_line, end_line

    def indent(self, event=None):
        first_line, last_line = self.get_selected_lines()
        for line in range(first_line, last_line+1):
            self.text.insert(f"{line}.0", " " * 4)
        return 'break'

    def backspace(self, event=None):
        if self.text.get("insert-1c") == "    ":
            self.text.delete("insert-4c", "insert")
        else:
            self.text.delete("insert-1c", "insert")
        self.undo_stack.append(self.text.get("1.0", tk.END))

    def unindent(self, event=None):
        first_line, last_line = self.get_selected_lines()
        for line in range(first_line, last_line + 1):
            line_start = "{}.0".format(line)
            if self.text.get(line_start, line_start + "4") == "    ":
                self.text.delete(line_start, line_start + "4")

    def replace(self, word, replace_with):
        start = "1.0"
        while True:
            pos = self.text.search(word, start, stopindex="end")
            if not pos:
                break
            self.text.delete(pos, "{}+{}c".format(pos, len(word)))
            self.text.insert(pos, replace_with)
            start = "{}+{}c".format(pos, len(replace_with))


if __name__ == "__main__":
    notepad = Notepad()
    notepad.create_widgets()
    notepad.mainloop()