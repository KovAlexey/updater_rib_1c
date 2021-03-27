from methadata1c import Methadata1C


class CommonModuleUpdate(Methadata1C):
    _method_need_update = None
    _method_start_update = None

    UPDATE_OK = 0
    UPDATE_NOT_REQUIRED = 1
    UPDATE_NOT_MONOPOLY = 2
    UPDATE_EXC = 3

    def __init__(self, connection):
        super(CommonModuleUpdate, self).__init__(connection)

        module = Methadata1C(connection, "ОбновлениеИнформационнойБазы")
        self._method_need_update = module.getmethod("НеобходимоОбновлениеИнформационнойБазы")
        self._method_start_update = module.getmethod("ВыполняетсяОбновлениеИнформационнойБазы")

    def need_update(self) -> bool:
        return self._method_need_update()

    def start_update(self):
        self.__logger.debug("Начинаю выполнение обработчиков обновления")
        print("Выполнение отложенных обработчков")
        try:
            result = self._method_start_update(True)
        except Exception as e:
            self.__lo

        print("Выполнение отложенных обработчков закончено. Результат: %s", result)
        self.__logger.debug("Закончили выполнение обработчиков обновления")
