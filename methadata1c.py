import logging

class Methadata1C:
    _name = ""
    _this_object = None

    def __init__(self, comobject, name = ""):
        self._name = name
        if self._name == "":
            self._this_object = comobject
        else:
            self._this_object = getattr(comobject, name)

    def getchild(self, name):
        return getattr(self._this_object, name)

    def getmethod(self, name):
        return getattr(self._this_object, name)


class CommonModuleExchange(Methadata1C):
    __logger = logging.getLogger("CommonModule")
    _node_exchange = None
    _GetExchangeParameters = None
    _StartExchange = None

    def __init__(self, connection):
        super(CommonModuleExchange, self).__init__(connection, "ОбменДаннымиСервер")
        self._GetExchangeParameters = self.getmethod("ПараметрыОбмена")
        self._StartExchange = self.getmethod("ВыполнитьОбменДаннымиДляУзлаИнформационнойБазы")

        exhange_planes_manager = Methadata1C(connection, "ПланыОбмена")
        self._node_exchange = exhange_planes_manager.getmethod("ГлавныйУзел")()
        self.__logger.debug("Модуль обмена данными успешно инициализирован!")
        pass

    def start_loading(self):
        parameters = self._GetExchangeParameters()

        self.__logger.debug("Начинаю загрузку")
        setattr(parameters, "ВыполнятьВыгрузку", False)
        setattr(parameters, "ВыполнятьЗагрузку", True)
        error = [True]
        self._StartExchange(self._node_exchange, parameters, error[0])
        self.__logger.debug("Результат загрузки. Успешно: %s", not error)

        return not error[0]