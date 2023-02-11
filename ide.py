import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from collections import deque
from tkinter import *
import base64
import sys
import subprocess
import re
import os
from tkinter import ttk
import flake8.api
import io


class Notepad(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Notetab")
        self.geometry("700x400")
        self.stack = deque(maxlen = 10)
        self.stackcursor = 0

        self.line_numbers = tk.Text(self, width=3, padx=2, pady=10, takefocus=0,
                                    border=0, background="white", state="disabled", foreground="grey")
        self.line_numbers.pack(side="left", fill="y")
        self.text = tk.Text(self, wrap="word", padx = 10, pady = 10)
        self.text.pack(fill="both", expand=True)

        self.text.bind("<Control-z>", self.undo)
        self.text.bind("<Control-Z>", self.undo)
        self.text.bind("<Tab>", self.indent_)
        self.text.bind("<Return>", lambda event: self.indent(event.widget))
        self.text.bind("<Shift-Tab>", self.unindent)
        self.text.bind("<BackSpace>", self.backspace)
        self.text.bind("<Delete>", self.backspace)
        self.text.bind("<Control-s>", self.save_file)
        self.text.bind("<F5>", self.run_python)
        self.text.bind("<MouseWheel>", self.sync_scroll)
        self.text.bind("<Control-space>", self.comparison)
        self.text.bind("<space>", self.acept_completion)
        Font_tuple = ("Lucida Console", 10)

        # Parsed the specifications to the
        # Text widget using .configure( ) method.
        self.text.configure(font=Font_tuple)
        self.line_numbers.configure(font=Font_tuple)
        self.T1 = self.text
        self.T1.tag_configure("orange", foreground="orange")
        self.T1.tag_configure("blue", foreground="blue")
        self.T1.tag_configure("purple", foreground="purple")
        self.T1.tag_configure("green", foreground="green")
        self.T1.tag_configure("red", foreground="red")

        scrollbar = tk.Scrollbar(self.text, orient='vertical', command=self.text.yview)
        scrollbar.pack(side='right', fill='y')

        self.tags = ["orange", "blue", "purple", "green", "red"]

        self.wordlist = [['and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif',
                          'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
                          'nonlocal', 'not', 'or', 'raise', 'try', 'while', 'with', 'yield',
                           'False', 'None', 'True', 'abs', 'all', 'any',  'bool', 'breakpoint',  'bytes', 'callable',
                          'chr', 'classmethod', 'dict', 'dir', 'enumerate', 'eval',
                          'exit', 'filter', 'float', 'getattr', 'globals', 'hasattr','input', 'int', 'iter', 'len',
                          'list', 'locals', 'map', 'next', 'open', 'print', 'property', 'range', 'repr', 'reversed',
                          'set', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'zip'],
                         ['int', 'float', 'bool', 'print', 'input', 'len', 'range', 'append', 'pop'],
                         ['self', 'return', 'pass']]
        def flatten(l):
            return [item for sublist in l for item in sublist]
        self.autocompleteList = flatten(self.wordlist)

        print(self.wordlist)
        self.search_start = '1.0'

        self.undo_stack = []
        self.filename = None

        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        developer_menu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="New Window", command=self.new_window)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As", command=self.save_as)
        filemenu.add_command(label="About", command=self.show_about)
        filemenu.add_command(label="Quit", command=self.quit_program)


        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Copy", command=self.copy_text)
        self.popup_menu.add_command(label="Paste", command=self.paste_text)

        self.text.bind("<Button-3>", self.show_popup_menu)

        developer_menu.add_command(label="Run Python", command=self.run_python)
        developer_menu.add_command(label="Encode Base64", command=self.encode_base64)
        developer_menu.add_command(label="Decode Base64", command=self.decode_base64)
        developer_menu.add_command(label="Lint Code", command=self.lint_code)



        #  communicate back to the scrollbar
        self.text['yscrollcommand'] = scrollbar.set


        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Developer", menu=developer_menu)

        self.config(menu=menubar)

    def lint_code(self, event=None):
        # run flake8 on the file
        os.system("flake8 " + self.filename + " > lint.txt")
        # open the file
        with open("lint.txt", "r") as f:
            # read the file
            lint = f.read()
            # if there is no lint
            if lint == "":
                # tell the user
                messagebox.showinfo("Lint", "No lint found")
            else:
                # else show the lint
                messagebox.showinfo("Lint", lint)


    @staticmethod
    def matches(fieldValue, acListEntry):
        pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)
    def comparison(self, event=None):
        def get_word_before_cursor():
            index = self.text.index(tk.INSERT)
            text_before_cursor = self.text.get(1.0, index)
            words = text_before_cursor.split()
            return words[-1] if words else ""
        word = get_word_before_cursor()
        print(word)
        print([w for w in self.autocompleteList if self.matches(word, w)])
        try:
            first_word = [w for w in self.autocompleteList if self.matches(word, w)][0]
            self.word_to_insert = first_word[len(word):]
        except IndexError:
            self.word_to_insert = ""
        # insert word_to_insert at the current cursor position
        self.text.insert(tk.INSERT, self.word_to_insert)
        # highlight the inserted word
        self.text.tag_add("sel", "insert -%dc" % len(self.word_to_insert), "insert")
    def acept_completion(self, event=None):
        # remove highlighted marker
        self.text.tag_remove("sel", "1.0", tk.END)

    def new_window(self):
        import os
        subprocess.Popen(["python", os.path.abspath(__file__)], shell=False)

    def show_popup_menu(self, event):
        self.popup_menu.post(event.x_root, event.y_root)

    def copy_text(self):
        self.clipboard_clear()
        text = self.text.get("sel.first", "sel.last")
        self.clipboard_append(text)

    def update_line_numbers(self, event=None):
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        line_number = 1
        for line in self.text.get("1.0", "end").split("\n"):
            self.line_numbers.insert("end", str(line_number) + "\n")
            line_number += 1
        self.line_numbers.configure(state="disabled")

    def sync_scroll(self, *args):
        self.line_numbers.yview_moveto(self.text.yview()[0])
        self.text.yview_moveto(self.line_numbers.yview()[0])

    def on_text_change(self, event=None):
        self.update_line_numbers()

    def paste_text(self):
        text = self.clipboard_get()
        self.text.insert("insert", text)

    def tagHighlight(self):
        start = "1.0"
        end = "end"

        for mylist in self.wordlist:
            num = int(self.wordlist.index(mylist))

            for word in mylist:
                self.T1.mark_set("matchStart", start)
                self.T1.mark_set("matchEnd", start)
                self.T1.mark_set("SearchLimit", end)

                mycount = IntVar()

                while True:
                    index = self.T1.search(word, "matchEnd", "SearchLimit", count=mycount, regexp=False)

                    if index == "": break
                    if mycount.get() == 0: break

                    self.T1.mark_set("matchStart", index)
                    self.T1.mark_set("matchEnd", "%s+%sc" % (index, mycount.get()))

                    preIndex = "%s-%sc" % (index, 1)
                    postIndex = "%s+%sc" % (index, mycount.get())

                    if self.check(index, preIndex, postIndex):
                        self.T1.tag_add(self.tags[num], "matchStart", "matchEnd")

    def new_file(self):
        self.text.delete("1.0", END)
        self.filename = None
        self.title(f"Notetab")

    def check(self, index, pre, post):
        letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                   "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

        if self.T1.get(pre) == self.T1.get(index):
            pre = index
        else:
            if self.T1.get(pre) in letters:
                return 0

        if self.T1.get(post) in letters:
            return 0

        return 1

    def scan(self):
        start = "1.0"
        end = "end"
        mycount = IntVar()

        regex_patterns = [r'".*"', r'#.*']

        for pattern in regex_patterns:
            self.T1.mark_set("start", start)
            self.T1.mark_set("end", end)

            num = int(regex_patterns.index(pattern))

            while True:
                index = self.T1.search(pattern, "start", "end", count=mycount, regexp=True)

                if index == "": break

                if (num == 1):
                    self.T1.tag_add(self.tags[4], index, index + " lineend")
                elif (num == 0):
                    self.T1.tag_add(self.tags[3], index, "%s+%sc" % (index, mycount.get()))

                self.T1.mark_set("start", "%s+%sc" % (index, mycount.get()))

    def stackify(self):
        self.stack.append(self.T1.get("1.0", "end - 1c"))
        if self.stackcursor < 9: self.stackcursor += 1

    def show_about(self):
        messagebox.showinfo("About", "Notetab\n\nThis is a notepad application made with tkinter.\nAuthor: Estêvão")

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

    def open_file(self, filename=None):
        if filename:
            filepath = filename
        else:
            filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"),
                                                                                      ("All Files", "*.*"),
                                                                                      ("Python Files", "*.py")])
        if filepath:
            with open(filepath, "r", encoding='utf-8') as file:
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", file.read().replace("\t", "    "))
                self.undo_stack = []
                self.filename = filepath
                self.update()
        self.title(f"Notetab - {self.filename}")

    def save_file(self, event=None):
        if self.filename:
            with open(self.filename, "w", encoding='utf-8') as f:
                f.write(self.text.get("1.0", "end"))
        else:
            self.save_as()
        self.title(f"Notetab - {self.filename}")


    def save_as(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            with open(filename, "w", encoding='utf-8') as f:
                f.write(self.text.get("1.0", "end"))
            self.filename = filename
        self.title(f"Notetab - {self.filename}")

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

    def getIndex(self, index):
        while True:
            if self.T1.get(index) == " ":
                index = "%s+%sc" % (index, 1)
            else:
                return self.T1.index(index)

    def indent(self, widget):
        # check if the previous line has a colon
        index1 = widget.index("insert")
        index2 = "%s-%sc" % (index1, 1)
        prevIndex = widget.get(index2, index1)
        prevIndentLine = widget.index(index1 + "linestart")
        prevIndent = self.getIndex(prevIndentLine)

        if prevIndex == ":":
            # if the previous line has a colon, add 4 spaces
            widget.insert("insert", "\n" + "    ")
            #widget.mark_set("insert", "insert + 1 line + 4char")

            while widget.compare(prevIndent, ">", prevIndentLine):
                widget.insert("insert", "    ")
                #widget.mark_set("insert", "insert + 4 chars")
                prevIndentLine += "+4c"
            return "break"

        elif prevIndent != prevIndentLine:
            widget.insert("insert", "\n")
            #widget.mark_set("insert", "insert + 1 line")

            while widget.compare(prevIndent, ">", prevIndentLine):
                widget.insert("insert", "    ")
                #widget.mark_set("insert", "insert + 4 chars")
                prevIndentLine += "+4c"
            return "break"

    def indent_(self, event=None):
        first_line, last_line = self.get_selected_lines()
        for line in range(first_line, last_line+1):
            self.text.insert(f"{line}.0", " " * 4)
        # self.undo_stack.append(self.text.get("1.0", tk.END))
        return 'break'

    def backspace(self, event=None):
        if self.text.get("insert-1c") == " " and self.text.get("insert-2c") == " "\
                and self.text.get("insert-3c") == " " and self.text.get("insert-4c") == " ":
            first_line, last_line = self.get_selected_lines()
            for line in range(first_line, last_line + 1):
                line_start = "{}.0".format(line)
                if self.text.get(line_start, line_start + "4") == "    ":
                    self.text.delete(line_start, line_start + "3")
                    break
                elif self.text.get(line_start, line_start + "3") == "   ":
                    self.text.delete(line_start, line_start + "2")
                    break
                elif self.text.get(line_start, line_start + "2") == "  ":
                    self.text.delete(line_start, line_start + "1")
                    break
                elif self.text.get(line_start, line_start + "1") == " ":
                    self.text.delete(line_start, line_start + "0")
                    break
        self.undo_stack.append(self.text.get("1.0", tk.END))

    def unindent(self, event=None):
        first_line, last_line = self.get_selected_lines()
        for line in range(first_line, last_line + 1):
            line_start = "{}.0".format(line)
            if self.text.get(line_start, line_start + "4") == "    ":
                self.text.delete(line_start, line_start + "4")
            elif self.text.get(line_start, line_start + "3") == "   ":
                self.text.delete(line_start, line_start + "3")
            elif self.text.get(line_start, line_start + "2") == "  ":
                self.text.delete(line_start, line_start + "2")
            elif self.text.get(line_start, line_start + "1") == " ":
                self.text.delete(line_start, line_start + "1")
        # self.undo_stack.append(self.text.get("1.0", tk.END))

    def replace(self, word, replace_with):
        start = "1.0"
        while True:
            pos = self.text.search(word, start, stopindex="end")
            if not pos:
                break
            self.text.delete(pos, "{}+{}c".format(pos, len(word)))
            self.text.insert(pos, replace_with)
            start = "{}+{}c".format(pos, len(replace_with))

    def update(self) -> None:
        self.on_text_change()
        self.stackify()
        self.tagHighlight()
        self.scan()

    def run_python(self, event=None):
        import subprocess
        subprocess.run(["cmd", "/c", "start", "cmd", "/k", "python", self.filename], shell=True)

    def decode_base64(self):
        decode_text = base64.b64decode(self.text.get("1.0", "end")).decode("utf-8")
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", decode_text)
        self.update()

    def encode_base64(self):
        encode_text = base64.b64encode(self.text.get("1.0", "end").encode("utf-8")).decode("utf-8")
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", encode_text)

    def quit_program(self):
        sys.exit()


if __name__ == "__main__":
    notepad = Notepad()
    notepad.create_widgets()
    notepad.bind("<Key>", lambda event: notepad.update())
    args = sys.argv
    if len(args) > 1:
        notepad.open_file(args[1])
    notepad.mainloop()