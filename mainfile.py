import logging
from nodeupteader1c import Node1CUpdater
from comconnector1c import ConnectionParams


def main():
    bd_name = "D:\\1C Base\\RT rib"
    parameters = ConnectionParams(bd_name)

    updater = Node1CUpdater("D:\\temp\\", "C:\\Program Files\\1cv8\\8.3.18.1289\\bin\\", "D:\\temp\\exchange\\",
                            "РТ", "РУ", parameters)
    # updater.parsefile()
    # if not updater.make_copy():
    #     print("error")
    #     return -1

    updater.loadexchangefile()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(msecs)d %(asctime)-15s %(levelname)s %(module)s:%(lineno)d"
                                                    " (%(funcName)s): %(message)s")
    main()
