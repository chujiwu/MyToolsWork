class Child(object):
    def __init__(self):
        self._name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def _say_name(self):
        print(self._name)


class Father(Child):
    def __init__(self):
        super().__init__()

    def _say_name(self):
        super()._say_name()


father = Father()
father.name = "father"
father._say_name()
