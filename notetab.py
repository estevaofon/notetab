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

        self.undo_stack = []

        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

    def clear_search(self):
        self.text.tag_remove("sel", "1.0", "end")

    def search(self, word, start="1.0", stop="end"):
        self.clear_search()
        pos = self.text.search(word, start, stopindex=stop)
        if pos:
            self.text.mark_set("insert", pos)
            self.text.see("insert")
            self.text.tag_add("sel", pos, "{}+{}c".format(pos, len(word)))
            self.text.focus()
            return True
        return False

    def create_widgets(self):
        # ...
        search_frame = tk.Frame(self)
        search_frame.pack(side="top", fill="x")
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side="left")
        search_button = tk.Button(search_frame, text="Search", command=lambda: self.search(search_entry.get()))
        search_button.pack(side="right")

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



if __name__ == "__main__":
    notepad = Notepad()
    notepad.create_widgets()
    notepad.mainloop()