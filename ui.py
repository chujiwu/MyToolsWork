from tkinter import *


class ColorPalette(object):
    def __init__(self, root):
        frame = Frame(root, bg=rgb_to_color("255,20,21"))
        frame.size = (600, 600)
        frame.place(x=10, y=10)
        print(frame.size)

    def set_color_palette(self):
        pass

    def update_color_palette(self):
        pass


def rgb_to_color(rgb):
    color_str = ""
    l = rgb.split(",")
    if len(l) == 3:
        color_str += "#"
        for s in l:
            hex_str = hex(int(s))[2:]
            if len(hex_str) == 1:
                color_str += "0"
            color_str += hex_str
        return color_str
    else:
        raise Exception("rgb value is not right")


if __name__ == "__main__":
    print(rgb_to_color("255,2,10"))
    root = Tk()
    root.geometry("600x600")
    frame = Frame(root, bg="red", width=200, height=200)
    frame.config(width=600, height=600)
    print(frame.size)
    frame.place(x=10, y=10)
    # frame.pack()
    # color_palette = ColorPalette(root)
    root.mainloop()
