import tkinter as tk


class ImagePicker(tk.Frame):
    def __init__(self, master=None, img_array=None):
        super().__init__(master)
        self.master = master
        self.array = img_array if img_array else []
        self.current = 0
        self.fr_sidebar = tk.Frame(self)
        # self.fr_images = tk.Frame(self)
        self.txt_edit = tk.Text(self)

        self.pack()
        self.config()
        self.create_widgets()
        self.show()

    def config(self):
        self.fr_sidebar.grid_rowconfigure(
            list(range(0, 10)), minsize=0, weight=1)
        self.fr_sidebar.grid_rowconfigure(
            [0, 1, 8, 9], minsize=20, weight=0)

    def create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, minsize=100)
        self.columnconfigure(1, weight=10)

        self.create_sidebar()

    def create_sidebar(self):
        lbl_total_images = tk.Label(
            self.fr_sidebar, text="Total Images: {}".format(len(self.array)))
        lbl_current = tk.Label(
            self.fr_sidebar, text="Current: {}".format(self.current))
        btn_upload = tk.Button(self.fr_sidebar, text="Manual Upload")
        btn_close = tk.Button(
            self.fr_sidebar, text="Close")

        lbl_total_images.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        lbl_current.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        btn_upload.grid(row=8, column=0, sticky="ew", padx=5, pady=5)
        btn_close.grid(row=9, column=0, sticky="ew", padx=5, pady=5)

    def show(self):
        self.fr_sidebar.grid(row=0, column=0, sticky="ns")
        self.txt_edit.grid(row=0, column=1, sticky="nsew")


if __name__ == "__main__":
    window = tk.Tk()

    window.title("Image Picker")
    window.minsize(width=600, height=400)
    window.rowconfigure(0, minsize=400, weight=1)
    window.columnconfigure(0, minsize=400, weight=1)

    app = ImagePicker(window)
    # app.pack(fill=tk.BOTH, expand=1)
    app.grid(column=0, row=0, sticky=("nsew"))

window.mainloop()
