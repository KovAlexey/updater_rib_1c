import logging
import re
import subprocess
import configparser
import traceback
import zipfile
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

    def __init__(self):
        self._connectionParams = ConnectionParams("")
        self.readconfig()
        self._connector = ComConnector1C(ComConnector1C.V83_COMCONNECTOR)

    def getmessagenumber(self):
        return self._message_number

    def gethavechanges(self):
        return self._have_changes

    def testconnectiontoib(self):
        try:
            connection = self._connector.connect(self._connectionParams)
        except:
            traceback.print_exc()
            return False
        return True

    def parsefile(self, zip_file=False):
        self._message_number = 0
        self._have_changes = False

        if zip_file:
            zipname = self._exchange_directory + "Message_{0}_{1}.zip".format(self._central_node_name,
                                                                              self._node_name)
            print("Открываю архив ", zipname)
            try:
                archive = zipfile.ZipFile(zipname)
            except Exception as e:
                self.__logger.error("", exc_info=True)
                print("Ошибка при открытии архива")
                traceback.print_exc()
                return False
            filename = "Message_{0}_{1}.xml".format(self._central_node_name,
                                                                               self._node_name)
        else:
            filename = self._exchange_directory + "Message_{0}_{1}.xml".format(self._central_node_name,
                                                                               self._node_name)

        print("Открываю файл: ", filename)
        try:
            if zip_file:
                message_file_io = archive.open(filename)
            else:
                message_file_io = self._open_file(filename)
        except Exception as e:
            self.__logger.error("", exc_info=True)
            traceback.print_exc()
            return False

        self._parse_exchange_file(filename, message_file_io)

        message = "Номер сообщения: {msg_num}\n" \
                  "Наличие изменений: {have_changes}".format(msg_num=self._message_number,
                                                             have_changes=self._have_changes
                                                             )
        print(message)
        self.__logger.debug("Номер сообщения: %s", self._message_number)
        self.__logger.debug("Наличие изменений: %s", self._have_changes)
        self.__logger.debug("Завершение парсинга")
        return True

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
        print(command)
        self.__logger.debug(command)

        try:
            result = subprocess.check_call(command)
        except Exception as e:
            self.__logger.error("Ошибка при выгрузке копии!", exc_info=True)
            #traceback.print_exc()
            result = -1

        if result == 0:
            print("Файл успешно выгружен: ", self._working_directory, dt_name)
        else:
            print("Произошла ошибка при выгрузке:")

        try:
            log = open(self._working_directory + "log.txt", 'r', encoding="utf-8")
            res = log.read()
            self.__logger.debug(res.encode("utf-8").decode("cp1251"))
            print(res)
        except Exception as e:
            self.__logger.error("Ошибка при чтении лога!", exc_info=True)
        finally:
            log.close()

        if result == 0:
            return True
        else:
            return False

    def update_cfg(self):
        self.__logger.debug("Начинаю обновление")
        command = "{bin}1cv8.exe DESIGNER {connectionparams} " \
                  "/UpdateDBCfg -Dynamic- " \
                  "/DisableStartupMessages /DisableStartupDialogs " \
                  "/DumpResult {working_dir}{result_name} /out {working_dir}{log_name}"

        command = command.format(bin=self._bin_directory,
                                 connectionparams=self._connectionParams.getdesignerconnectionstring(),
                                 working_dir=self._working_directory,
                                 result_name="result.txt",
                                 log_name="log.txt"
                                 )
        print(command)
        try:
            result = subprocess.check_call(command)
            print("Обновление выполнено успешно")
        except Exception as e:
            print("Ошибка при обновлении БД!")
            self.__logger.error("Ошибка при обновлении БД!", exc_info=True)
            traceback.print_exc()
            return False

        try:
            log = open(self._working_directory + "log.txt", 'r', encoding="utf-8")
            res = log.read()
            # self.__logger.debug(res.encode("utf-8").decode("cp1251"))
            print(res)
        except Exception as e:
            print("Ошибка при чтении лога!")
            traceback.print_exc()
            self.__logger.error("Ошибка при чтении лога!", exc_info=True)
        finally:
            log.close()

        return True

    LOAD_EXCHANGE_OK = 0
    LOAD_EXCHANGE_EXC = -1
    LOAD_EXCHANGE_ERROR_OPENED_DESIGNER = 1
    LOAD_EXCHANGE_ERROR_NEED_UPDATE = 2
    LOAD_EXCHANGE_ERROR_UKNOWN = 3

    def makeupdateenterprise(self, connection=None):
        if connection is None:
            connection = self._connector.connect(self._connectionParams)
        module = getattr(connection, "ОбновлениеИнформационнойБазы")
        method = getattr(module, "ВыполнитьОбновлениеИнформационнойБазы")
        self.__logger.debug("Начинаю выполнение обработчиков обновления")
        print("Выполнение обработчиков...")
        result = method(True)
        print("Закончили выполнение обработчиков...")
        self.__logger.debug("Закончили выполнение обработчиков обновления")
        return result

    def make_exchange(self, load):
        connection = self._connector.connect(self._connectionParams)
        module = CommonModuleExchange(connection)
        print("Выполняю обмен")
        result = module.make_exchange(load)
        del connection

        if not result:
            filename = module.getloadingjournal(self._working_directory, load)
            file_io = self._open_file(filename)
            try:
                error = self._parse_journal_file(filename, file_io)
            except Exception as e:
                self.__logger.error("Ошибка при парсинге", exc_info=True)
                return self.LOAD_EXCHANGE_EXC
            print(error)
            if "Ошибка блокировки информационной базы для конфигурирования." in error:
                return self.LOAD_EXCHANGE_ERROR_OPENED_DESIGNER
            elif "Необходимо выполнить обновление конфигурации базы данных." in error:
                return self.LOAD_EXCHANGE_ERROR_NEED_UPDATE
            else:
                return self.LOAD_EXCHANGE_ERROR_UKNOWN
        print("Обмен выполнен успешно")
        return self.LOAD_EXCHANGE_OK

    def readconfig(self):
        config = configparser.ConfigParser()
        files = config.read("config.ini", encoding="utf-8")
        if len(files) == 0:
            print("Нет файла настроек. будут созданы новые")
            self.saveconfig()
            return False

        section = "DIR"
        self._working_directory = config.get(section, "working_dir")
        self._exchange_directory = config.get(section, "exchange_dir")
        self._bin_directory = config.get(section, "1cv8_dir")

        section = "NODE"
        self._central_node_name = config.get(section, "central_node")
        self._node_name = config.get(section, "node_name")

        section = "connection"
        connectionparams = self._connectionParams
        connectionparams.file = config.getboolean(section, "file_base")
        connectionparams.servername = config.get(section, "server_name")
        connectionparams.bd_name = config.get(section, "bd_name")
        connectionparams.path_to_base = config.get(section, "path_to_filebase")
        connectionparams.login = config.get(section, "login")
        connectionparams.pwd = config.get(section, "pwd")

        return True

    def saveconfig(self):
        config = configparser.ConfigParser()
        section = "DIR"
        config.add_section(section)
        config.set(section, "working_dir", self._working_directory)
        config.set(section, "exchange_dir", self._exchange_directory)
        config.set(section, "1cv8_dir", self._bin_directory)

        section = "NODE"
        config.add_section(section)
        config.set(section, "central_node", self._central_node_name)
        config.set(section, "node_name", self._node_name)

        section = "connection"
        config.add_section(section)
        config.set(section, "file_base", str(self._connectionParams.file))
        config.set(section, "server_name", self._connectionParams.servername)
        config.set(section, "bd_name", self._connectionParams.bd_name)
        config.set(section, "path_to_filebase", self._connectionParams.path_to_base)
        config.set(section, "login", self._connectionParams.login)
        config.set(section, "pwd", self._connectionParams.pwd)
        with open("config.ini", "w", encoding="utf-8") as configfile:
            config.write(configfile)
            configfile.close()

    def __del__(self):
        self.__logger.debug('del updater("' + self._exchange_directory + '")')
