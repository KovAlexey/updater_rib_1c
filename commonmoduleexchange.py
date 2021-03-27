import logging
import pythoncom
from win32com.client import VARIANT

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

    def make_exchange(self, load: bool):
        parameters = self._method_get_exchange_parameters()

        self.__logger.debug("Начинаю загрузку")
        setattr(parameters, "ВыполнятьВыгрузку", not load)
        setattr(parameters, "ВыполнятьЗагрузку", load)

        error = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)

        self._method_start_exchange(self._node_exchange, parameters, error)
        error = error.value
        self.__logger.debug("Результат %s. Успешно: %s", "загрузки" if load else "выгрузки", not error)

        return not error

    def getloadingjournal(self, work_dir: str, load: bool):
        enum_action = self._enum_action_load if load else self._enum_action_upload
        journal_settings = self._method_journal_settings(self._node_exchange, enum_action)
        journal_settings.insert("Level", self._const_journal_error_level)

        journal = work_dir + "journal.xml"
        self._method_get_journal_registration(journal, journal_settings)

        return journal
