import tkinter as tk

from ankiword.ui.image_frame import ImagePickerFrame


class ImagePicker():
    def __init__(self, img_array):
        self.window = None
        self.frame = None
        self.image_array = img_array

    def run(self):
        window = tk.Tk()

        window.title("Image Picker")

        window.resizable(False, False)
        window.rowconfigure(0, minsize=400, weight=1)
        window.columnconfigure(0, minsize=500, weight=1)

        self.frame = ImagePickerFrame(window, self.image_array)
        self.frame.grid(column=0, row=0, sticky=("nsew"))

        window.mainloop()

    def retrieve_result(self):
        return self.frame.get_image()


if __name__ == "__main__":
    img_array = ['/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind11.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind12.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind13.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind14.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind17.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind18.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind19.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind2.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind20.jpg',
                 '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind21.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind22.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind23.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind24.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind3.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind4.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind6.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind7.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind8.jpg', '/Volumes/Work/Workspace/Dict_To_Anki/ankiword/data/imgs/kind9.jpg']

    app = ImagePicker(img_array)
    app.run()
    print(app.retrieve_result())
