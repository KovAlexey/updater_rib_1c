import logging
from lxml import etree

from methadata1c import Methadata1C


class CommonModuleExchange(Methadata1C):
    __logger = logging.getLogger("CommonModule")
    _node_exchange = None
    _method_get_exchange_parameters = None
    _method_start_exchange = None
    _method_journal_settings = None
    _method_get_journal_registration = None
    _enum_action_load = None
    _enum_action_upload = None
    _const_journal_error_level = None

    def __init__(self, connection):
        super(CommonModuleExchange, self).__init__(connection)

        module = Methadata1C(connection, "ОбменДаннымиСервер")
        self._method_get_exchange_parameters = module.getmethod("ПараметрыОбмена")
        self._method_start_exchange = module.getmethod("ВыполнитьОбменДаннымиДляУзлаИнформационнойБазы")

        exсhange_planes_manager = Methadata1C(connection, "ПланыОбмена")
        self._node_exchange = exсhange_planes_manager.getmethod("ГлавныйУзел")()
        self.__logger.debug("Модуль обмена данными успешно инициализирован!")

        module = Methadata1C(connection, "ОбменДаннымиВызовСервера")
        self._method_journal_settings = module.getmethod("ДанныеОтбораЖурналаРегистрации")

        enums = Methadata1C(connection, "Перечисления")
        actions_enum = enums.getchild("ДействияПриОбмене")
        self._enum_action_load = actions_enum.getvariable("ЗагрузкаДанных")
        self._enum_action_upload = actions_enum.getvariable("ВыгрузкаДанных")
        self._method_get_journal_registration = connection.UnloadEventLog
        self._const_journal_error_level = connection.EventLogLevel.Error

    def load_exchange_file(self):
        parameters = self._method_get_exchange_parameters()

        self.__logger.debug("Начинаю загрузку")
        setattr(parameters, "ВыполнятьВыгрузку", False)
        setattr(parameters, "ВыполнятьЗагрузку", True)
        error = [True]
        self._method_start_exchange(self._node_exchange, parameters, error[0])
        self.__logger.debug("Результат загрузки. Успешно: %s", not error)

        return not error[0]

    def getloadingjournal(self, work_dir):
        journal_settings = self._method_journal_settings(self._node_exchange, self._enum_action_load)
        journal_settings.insert("Level", self._const_journal_error_level)

        journal = work_dir + "journal.xml"
        res = self._method_get_journal_registration(journal, journal_settings)

        return journal
