import logging
import re
from lxml import etree
from comconnector1c import ComConnector1C, ConnectionParams

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

    def __init__(self, working_directory: str, bin_directory, exhange_directory: str, centralnodename: str, nodename: str,
                 connectionparams: ConnectionParams):
        self.__logger.debug('init updater("%s", "%s", "%s")', exhange_directory, centralnodename, nodename)
        self._working_directory = working_directory
        self._bin_directory = bin_directory
        self._exchange_directory = exhange_directory
        self._central_node_name = centralnodename
        self._node_name = nodename
        self._connectionParams = connectionparams

    def parsefile(self):
        self._message_number = 0
        self._have_changes = False

        filename = self._exchange_directory + "Message_{0}_{1}.xml".format(self._central_node_name,
                                                                           self._node_name)

        # noinspection PyBroadException
        try:
            self.__logger.debug('Открываю файл "%s"', filename)
            message_file_io = open(filename, "rb")
        except Exception as e:
            self.__logger.error("Ошибка при открытии файла", exc_info=True)
            raise

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

        self.__logger.debug("Номер сообщения: %s", self._message_number)
        self.__logger.debug("Наличие изменений: %s", self._have_changes)
        self.__logger.debug("Завершение парсинга")


    def make_copy(self):
        command = self._bin_directory + "1cv8.exe"
        command += " DESIGNER  "


    def __del__(self):
        self.__logger.debug('del updater("' + self._exchange_directory + '")')