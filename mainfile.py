import logging
import time
import traceback
from nodeupteader1c import Node1CUpdater



def updater_daemon(updater:Node1CUpdater):
    last_load_message_number = 0
    while True:
        print("Ожидаем изменений...")
        result = updater.parsefile(True)
        if not updater.gethavechanges() or not result:
            print("Ожидаем изменений 60 секунд")
            time.sleep(60)
            continue

        if last_load_message_number == updater.getmessagenumber():
            print("Изменения найдены. Но мы их уже загрузили. Ждем 60 секунд")
            time.sleep(60)
            continue

        print("Делаю бэкап")
        while not updater.make_copy():
            print("Произошла ошибка при создании бэкапа. Через минуту попробуем еще раз.")
            time.sleep(60)

        needupdate = False

        while True:
            print("Начинаем загрузку файла обмена")
            result = updater.make_exchange(True)
            if result == updater.LOAD_EXCHANGE_ERROR_NEED_UPDATE:
                print("Нужно обновить БД")
                needupdate = True
                break
            elif result == updater.LOAD_EXCHANGE_ERROR_OPENED_DESIGNER:
                print("Закройте конфигуратор!")
                time.sleep(60)
            elif result == updater.LOAD_EXCHANGE_OK:
                break


        print("Загружено сообщение: ", updater.getmessagenumber())

        if not needupdate:
            last_load_message_number = updater.getmessagenumber()
            continue

        print("Начинаю обновление БД...")
        while not updater.update_cfg():
            print("Произошла ошибка обновления БД")
            time.sleep(30)


        while True:
            print("Выполняю отложенные обработчики")
            result = updater.makeupdateenterprise()
            if "Успешно" in result:
                print("Успешное обновление")
                break
            elif "НеТребуется" in result:
                print("Не требуется")
                break
            elif "ОшибкаУстановкиМонопольногоРежима" in result:
                print("Ошибка установки монопольного режима! Нужно выгнать всех пользователей!")
                time.sleep(60)
        print("Выполняю выгрузку данных")
        while updater.make_exchange(False) != updater.LOAD_EXCHANGE_OK:
            print("Ошибка при выгрузке")
            time.sleep(60)
        last_load_message_number = updater.getmessagenumber()


def main():

    try:
        updater = Node1CUpdater()
    except Exception as e:
        traceback.print_exc()
        print("Нажмите клюбую клавишу...")
        input()
        raise

    while True:
        print("Введите команду\n"
              "1 - Проверить подключение\n"
              "2 - Запустить демона\n"
              "3 - Выполнить команды вручную\n"
              "q - Выход\n")
        command = input()
        if command == "1":
            result = updater.testconnectiontoib()
            if result:
                print("Подключение успешно")
            else:
                print("Подключение неудачно")
        elif command == "2":
            try:
                updater_daemon(updater)
            finally:
                print("Выход")
        if command == "3":
            while True:
                print("1 - Сделать бэкап\n"
                      "2 - Проверить файл обмена на изменения\n"
                      "3 - Выполнить загрузку данных\n" 
                      "4 - Выполнить выгрузку данных\n"
                      "5 - Обновить конфигурацию БД\n"
                      "6 - Выполнить обработчики обновления\n"
                      "0 - Выход обратно")
                command = input()
                if command == "1":
                    updater.make_copy()
                elif command == "2":
                    updater.parsefile(True)
                elif command == "3":
                    updater.make_exchange(True)
                elif command == "4":
                    updater.make_exchange(False)
                elif command == "5":
                    updater.update_cfg()
                elif command == "6":
                    updater.makeupdateenterprise()
                elif command == "0":
                    break
        elif command == "q":
            break

    return

    updater.parsefile()
    if not updater.make_copy():
        print("error")
        return -1

    result = updater.make_exchange(True)
    if result == updater.LOAD_EXCHANGE_ERROR_NEED_UPDATE:
         updater.update_cfg()
    updater.makeupdateenterprise()
    updater.make_exchange(True)
    updater.make_exchange(False)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(msecs)d %(asctime)-15s %(levelname)s %(module)s:%(lineno)d"
                                                    " (%(funcName)s): %(message)s", filename="log.txt")
    main()
