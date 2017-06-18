class Config(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        # !!!
        return cls.__instance

    def __init__(self):
        self._palette_path = ""
        self._form_folder = ""
        pass

    @property
    def palette_path(self):
        return self._palette_path

    @palette_path.setter
    def palette_path(self, palette_path):
        self._palette_path = palette_path

    @property
    def form_folder(self):
        return self._form_folder

    @form_folder.setter
    def form_folder(self, form_folder):
        self._form_folder = form_folder

