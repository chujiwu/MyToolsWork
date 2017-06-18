import tkinter

class Ui(object):
    def __init__(self):
        pass

    def start_up(self):
        self._ui_initialize()

    def _ui_initialize(self):
        root = tkinter.Tk()
        root.geometry(600, 600)
        root.mainloop()
        pass