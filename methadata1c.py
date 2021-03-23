class Methadata1C:
    _name = ""
    _this_object = None

    def __init__(self, comobject, name=""):
        self._name = name
        if self._name == "":
            self._this_object = comobject
        else:
            self._this_object = getattr(comobject, name)

    def getchild(self, name):
        return Methadata1C(self._this_object, name)

    def getvariable(self, name):
        return getattr(self._this_object, name)

    def getmethod(self, name):
        return getattr(self._this_object, name)


