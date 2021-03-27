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

    def __init__(self, servername, bd_name, login="", pwd=""):
        self.file = False
        self.servername = servername
        self.bd_name = bd_name
        self.login = login
        self.pwd = pwd

    def __init__(self, filename, login="", pwd=""):
        self.file = True
        self.path_to_base = filename
        self.login = login
        self.pwd = pwd

    def getconnectionstring(self):
        if self.file:
            connectstring = 'File="{path}";'
        else:
            connectstring = 'Srvr="{server}";Ref="{bd}";'
        connectstring += 'Usr = "{user}";pwd = "{pwd}"'

        connectstring = connectstring = self._formatstring(connectstring)

        return connectstring

    def _formatstring(self, connectstring: str):
        return connectstring.format(server=self.servername, bd=self.bd_name,
                                    path=self.path_to_base,
                                    user=self.login, pwd=self.pwd)

    def getdesignerconnectionstring(self):
        if self.file:
            connectstring = '/F "{path}" '
        else:
            connectstring = '/S "{server}\\{bd}" '

        connectstring += '/N "{user}" /P "{pwd}" '
        connectstring = self._formatstring(connectstring)
        return connectstring


class ComConnector1C:
    __component: ComConnectorInterface
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

    def connect(self, connectionparams: ConnectionParams):
        connectstring = connectionparams.getconnectionstring()
        self.__logger.debug('Подключаюсь к "%s"', connectstring)
        print("Подключаюсь к ", connectstring)
        connection = self.__component.Connect(connectstring)
        self.__logger.debug('Подключение выполнено успешно')

        return connection
