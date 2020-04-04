import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox as mb


class ImagePicker(tk.Frame):
    button_state_dict = {
        0: "disabled",
        1: "normal"
    }

    def __init__(self, master=None, img_array=None, path='../data/imgs'):
        super().__init__(master)
        self.master = master

        # TEST
        img_array = ['/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind11.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind12.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind13.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind14.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind17.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind18.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind19.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind2.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind20.jpg',
                     '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind21.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind22.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind23.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind24.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind3.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind4.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind6.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind7.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind8.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind9.jpg']
        # TEST

        self.array = img_array if img_array else []

        self._initialize()
        self._config()
        self._create_widgets()
        self.show()

    def _handle_next(self):
        self.btn_prev["state"] = self.button_state_dict[True]
        self.current_page += 1
        self.lbl_current["text"] = "Current Page: "+str(self.current_page + 1)
        self._create_image_grid()

        if (self.current_page+1)*9 > len(self.array):
            self.btn_next["state"] = self.button_state_dict[False]

    def _handle_prev(self):
        self.btn_next["state"] = self.button_state_dict[True]
        self.current_page -= 1
        self.lbl_current["text"] = "Current Page: "+str(self.current_page + 1)
        self._create_image_grid()

        if self.current_page == 0:
            self.btn_prev["state"] = self.button_state_dict[False]

    def _handle_click_image(self, event, label_image):
        if not label_image or not label_image.image:
            return
        if mb.askyesno('Are you sure?',
                       "Do you want to use this image for this word?"):
            # Save the imagedata, pass it out to the others.
            self.master.destroy()
            pass

    def _initialize(self):
        # Main Components
        self.current_page = 0
        self.fr_sidebar = tk.Frame(self)
        self.fr_images = tk.Frame(self, bg='white')
        self.img_list = []
        for i in range(0, 3):
            for j in range(0, 3):
                label = tk.Label(self.fr_images)
                label.grid(row=i, column=j, sticky="nswe",
                           padx=10, pady=10)
                label.bind(
                    "<Button-1>",
                    lambda e, image=label: self._handle_click_image(e, image))
                self.img_list.append(label)

        # Side bar
        self.lbl_total_images = tk.Label(
            self.fr_sidebar, text="Total Images: {}".format(len(self.array)))
        self.lbl_current = tk.Label(
            self.fr_sidebar,
            text="Current Page: {}".format(self.current_page + 1))

        self.btn_upload = tk.Button(self.fr_sidebar, text="Manual Upload")
        self.btn_close = tk.Button(
            self.fr_sidebar, text="Close")

        # Prev Next for sidebar
        init_prev_state = "disable"
        init_next_state = self.button_state_dict[len(self.array) > 9]
        self.fr_prenev = tk.Frame(self.fr_sidebar)
        self.btn_prev = tk.Button(
            self.fr_prenev, text="< Prev",
            state=init_prev_state, command=self._handle_prev)
        self.btn_next = tk.Button(
            self.fr_prenev, text="> Next",
            state=init_next_state, command=self._handle_next)

    def _config(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, minsize=100)
        self.columnconfigure(1, minsize=500, weight=10)

        self.fr_sidebar.grid_rowconfigure(
            list(range(0, 10)), minsize=0, weight=1)
        self.fr_sidebar.grid_rowconfigure(
            [0, 1, 8, 9], minsize=20, weight=0)
        self.fr_sidebar.grid_columnconfigure(
            [0, 1], minsize=0, weight=1)

    def _create_sidebar(self):
        self.lbl_total_images.grid(
            row=0, column=0, sticky="ew", padx=5, pady=5)
        self.lbl_current.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.fr_prenev.grid(row=2, column=0, sticky="nwse")
        self.btn_prev.grid(row=0, column=0, sticky='ew', padx=7, pady=2)
        self.btn_next.grid(row=0, column=1, sticky='ew', padx=2, pady=2)

        self.btn_upload.grid(row=8, column=0, sticky="ew", padx=5, pady=5)
        self.btn_close.grid(row=9, column=0, sticky="ew", padx=5, pady=5)

    def _create_image_grid(self):
        current_index = (self.current_page)*9
        next_index = current_index + 9

        if next_index >= len(self.array):
            next_index = len(self.array)
        current_array = self.array[current_index:next_index]

        for i in range(3):
            for j in range(3):
                index = i*3 + j
                if index >= len(current_array):
                    tkimage = None
                else:
                    im = Image.open(current_array[index])
                    resized = im.resize((150, 150), Image.ANTIALIAS)
                    tkimage = ImageTk.PhotoImage(resized)
                self.img_list[index].configure(image=tkimage)
                self.img_list[index].image = tkimage

    def _create_widgets(self):
        self._create_sidebar()
        self._create_image_grid()

    def show(self):
        self.fr_sidebar.grid(row=0, column=0, sticky="ns")
        # self.txt_edit.grid(row=0, column=1, sticky="nsew")
        self.fr_images.grid(row=0, column=1, sticky="nsew")


if __name__ == "__main__":
    window = tk.Tk()

    window.title("Image Picker")

    window.resizable(False, False)
    window.rowconfigure(0, minsize=400, weight=1)
    window.columnconfigure(0, minsize=500, weight=1)

    app = ImagePicker(window)
    # app.pack(fill=tk.BOTH, expand=1)
    app.grid(column=0, row=0, sticky=("nsew"))

window.mainloop()
