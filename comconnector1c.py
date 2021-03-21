import win32com.client
import pythoncom
import logging


class ComConnectorInterface:
    def Connect(self, connectstring: str):
        return object


class ConnectionParams:
    file: bool = False
    servername: str = ""
    bd_name: str = ""
    path_to_base: str = ""
    login: str = ""
    pwd: str = ""

    def __init__(self, servername, bd_name, login, pwd):
        self.file = False
        self.servername = servername
        self.bd_name = bd_name
        self.login = login
        self.pwd = pwd

    def __init__(self, filename, login, pwd):
        self.file = False
        self.path_to_base = filename
        self.login = login
        self.pwd = pwd

    def getconnectionstring(self):
        if self.file:
            connectstring = 'File="{path}";'.format(path=self.path_to_base)
        else:
            connectstring = 'Srvr="{server}";Ref="{bd}";'.format(server=self.servername, bd=self.bd_name)
        connectstring += ''


class ComConnector1C:
    __component: ComConnectorInterface
    _connection = None
    __component_name = ""
    __logger = logging.getLogger("ComConnector")
    V83_APPLICATION = "V83.Application"
    V83_THINK_CLIENT = "V83c.Application"
    V83_COMCONNECTOR = "V83.ComConnector"

    def __init__(self, componentname):
        pythoncom.CoInitialize()
        self.__component = win32com.client.gencache.EnsureDispatch(componentname)
        self.__component_name = componentname
        self.__logger.debug("Инициализация %s", componentname)

    def _connect(self, connectstring, usr="", pwd=""):
        loginformatstring = 'Usr = "{user}";pwd = "{pwd}"'
        connectstring += loginformatstring.format(user=usr, pwd=pwd)
        self.__logger.debug('Подключаюсь к "%s"', connectstring)
        self._connection = self.__component.Connect(connectstring)
        self.__logger.debug('Подключение выполнено успешно')

    def connect(self, server: str, bd: str, usr="", pwd=""):
        connectformatstring = 'Srvr="{server}";Ref="{bd}";'
        self._connect(connectformatstring.format(server=server, bd=bd), usr, pwd)

    def getconnection(self):
        return self._connection

    def connect(self, path: str, usr="", pwd=""):
        connectformatstring = 'File="{path}";'
        self._connect(connectformatstring.format(path=path), usr, pwd)
