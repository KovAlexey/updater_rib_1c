import logging
from methadata1c import Methadata1C, CommonModuleExchange
from nodeupteader1c import Node1CUpdater
from comconnector1c import ComConnector1C


def main():
    updater = Node1CUpdater("D:\\temp\\", "C:\\Program Files\\1cv8\\8.3.18.1289\\bin\\", "D:\\temp\\exchange\\",
                            "РТ", "РУ")
    updater.parsefile()
    connector = ComConnector1C(ComConnector1C.V83_COMCONNECTOR)
    bd_name = "D:\\1C Base\\RT rib"
    connector.connect(bd_name)
    connection = connector.getconnection()

    exchange_module = CommonModuleExchange(connection)
    # exchange_module.start_loading()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(msecs)d %(asctime)-15s %(levelname)s %(module)s:%(lineno)d"
                                                    " (%(funcName)s): %(message)s")
    main()
