import logging
import re
import subprocess
from datetime import datetime
from lxml import etree
from comconnector1c import ComConnector1C, ConnectionParams
from commonmoduleexchange import CommonModuleExchange


class Node1CUpdater:
    __logger = logging.getLogger("Node1CUpdater")
    _exchange_directory = ""
    _working_directory = ""
    _bin_directory = ""
    _node_name = ""
    _central_node_name = ""
    _tree: etree.ElementTree
    _message_number = 0
    _have_changes = False
    _connector: ComConnector1C
    _connectionParams: ConnectionParams

    def __init__(self, working_directory: str, bin_directory, exhange_directory: str, centralnodename: str,
                 nodename: str,
                 connectionparams: ConnectionParams):
        self.__logger.debug('init updater("%s", "%s", "%s")', exhange_directory, centralnodename, nodename)
        self._working_directory = working_directory
        self._bin_directory = bin_directory
        self._exchange_directory = exhange_directory
        self._central_node_name = centralnodename
        self._node_name = nodename
        self._connectionParams = connectionparams
        self._connector = ComConnector1C(ComConnector1C.V83_COMCONNECTOR)


    def parsefile(self):
        self._message_number = 0
        self._have_changes = False

        filename = self._exchange_directory + "Message_{0}_{1}.xml".format(self._central_node_name,
                                                                           self._node_name)

        message_file_io = self._open_file(filename)
        self._parse_exchange_file(filename, message_file_io)

        self.__logger.debug("Номер сообщения: %s", self._message_number)
        self.__logger.debug("Наличие изменений: %s", self._have_changes)
        self.__logger.debug("Завершение парсинга")

    def _parse_journal_file(self, filename: str, message_file_io):
        error = ""
        # noinspection PyBroadException
        try:
            itparser = etree.iterparse(message_file_io, events={"start"})
            for action, element in itparser:
                tag = re.sub(r'{.*}', '', element.tag)
                if tag == "Comment":
                    self.__logger.debug("Найден комментарий: " + element.text)
                    error += element.text

        except Exception as e:
            self.__logger.error("Ошибка при парсинге файла", exc_info=True)
            raise
        finally:
            self.__logger.debug("Закрываю файл %s", filename)
            message_file_io.close()

        return error

    def _parse_exchange_file(self, filename: str, message_file_io):
        # noinspection PyBroadException
        try:
            itparser = etree.iterparse(message_file_io, huge_tree=True, events={"start"})
            for action, element in itparser:
                tag = re.sub(r'{.*}', '', element.tag)
                if tag == "MessageNo":
                    self.__logger.debug("Найден номер сообщения")
                    # noinspection PyBroadException
                    try:
                        self._message_number = int(element.text)
                    except Exception is e:
                        self.__logger.error("Не удалось преобразовать номер сообщения в число")
                        raise
                elif tag == "Changes":
                    self.__logger.debug("Найдены изменения")
                    self._have_changes = True
                    break
                elif tag == "Parameters":
                    self.__logger.debug("Начались данные. Завершаю цикл")
                    break
        except Exception as e:
            self.__logger.error("Ошибка при парсинге файла", exc_info=True)
            raise
        finally:
            self.__logger.debug("Закрываю файл %s", filename)
            message_file_io.close()

    def _open_file(self, filename: str):
        # noinspection PyBroadException
        try:
            self.__logger.debug('Открываю файл "%s"', filename)
            message_file_io = open(filename, "rb")
        except Exception as e:
            self.__logger.error("Ошибка при открытии файла", exc_info=True)
            raise
        return message_file_io

    def make_copy(self):
        self.__logger.debug("Начинаю делать копию")
        command = "{bin}1cv8.exe DESIGNER {connectionparams} " \
                  "/DumpIB {working_dir}{dt_name} /out {working_dir}{log_name} " \
                  "/DumpResult {working_dir}{result_name} " \
                  "/DisableStartupMessages /DisableStartupDialogs"

        dt_name = datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + '.dt'
        command = command.format(bin=self._bin_directory,
                                 connectionparams=self._connectionParams.getdesignerconnectionstring(),
                                 working_dir=self._working_directory,
                                 dt_name=dt_name,
                                 result_name="result.txt",
                                 log_name="log.txt"
                                 )
        self.__logger.debug(command)

        try:
            result = subprocess.check_call(command)
        except Exception as e:
            self.__logger.error("Ошибка при выгрузке копии!", exc_info=True)
            return False

        try:
            log = open(self._working_directory + "log.txt", 'r', encoding="utf-8")
            res = log.read()
            self.__logger.debug(res)
        except Exception as e:
            self.__logger.error("Ошибка при чтении лога!", exc_info=True)
        finally:
            log.close()

        return True

    def update_cfg(self):
        self.__logger.debug("Начинаю обновление")
        command =   "{bin}1cv8.exe DESIGNER {connectionparams} " \
                    "/UpdateDBCfg -Dynamic- " \
                    "/DisableStartupMessages /DisableStartupDialogs " \
                    "/DumpResult {working_dir}{result_name} /out {working_dir}{log_name}"

        command = command.format(bin=self._bin_directory,
                                 connectionparams=self._connectionParams.getdesignerconnectionstring(),
                                 working_dir=self._working_directory,
                                 result_name="result.txt",
                                 log_name="log.txt"
                                 )

        try:
            result = subprocess.check_call(command)
        except Exception as e:
            self.__logger.error("Ошибка при обновлении БД!", exc_info=True)
            return False

        try:
            log = open(self._working_directory + "log.txt", 'r', encoding="utf-8")
            res = log.read()
            self.__logger.debug(res)
        except Exception as e:
            self.__logger.error("Ошибка при чтении лога!", exc_info=True)
        finally:
            log.close()

        return True

    LOAD_EXCHANGE_OK = 0
    LOAD_EXCHANGE_EXC = -1
    LOAD_EXCHANGE_ERROR_OPENED_DESIGNER = 1
    LOAD_EXCHANGE_ERROR_NEED_UPDATE = 2
    LOAD_EXCHANGE_ERROR_UKNOWN = 3

    def loadexchangefile(self):
        connection = self._connector.connect(self._connectionParams)
        module = CommonModuleExchange(connection)
        result = module.load_exchange_file()
        if not result:
            filename = module.getloadingjournal(self._working_directory)
            file_io = self._open_file(filename)
            try:
                error = self._parse_journal_file(filename, file_io)
            except Exception as e:
                self.__logger.error("Ошибка при парсинге", exc_info=True)
                return self.LOAD_EXCHANGE_EXC

            if "Ошибка блокировки информационной базы для конфигурирования." in error:
                return self.LOAD_EXCHANGE_ERROR_OPENED_DESIGNER
            elif "Необходимо выполнить обновление конфигурации базы данных." in error:
                return self.LOAD_EXCHANGE_ERROR_NEED_UPDATE
            else:
                return self.LOAD_EXCHANGE_ERROR_UKNOWN

        return self.LOAD_EXCHANGE_OK

    def __del__(self):
        self.__logger.debug('del updater("' + self._exchange_directory + '")')
