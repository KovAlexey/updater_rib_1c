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
                 connectionParams: ConnectionParams):
        self.__logger.debug('init updater("%s", "%s", "%s")', exhange_directory, centralnodename, nodename)
        self._working_directory = working_directory
        self._bin_directory = bin_directory
        self._exchange_directory = exhange_directory
        self._central_node_name = centralnodename
        self._node_name = nodename
        self._connectionParams = connectionParams


    def make_copy(self):
        command = self._bin_directory + "1cv8.exe"
        command += " DESIGNER  "


    def __del__(self):
        self.__logger.debug('del updater("' + self._exchange_directory + '")')