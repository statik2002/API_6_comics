# Урок 6 по API на Devman
 
### Скрипт для постинга комиксов в VK

## Общее описание

Скрипт скачивает рандомный комикс с сайта https://xkcd.com/ и публикует в VK на стену сообщества.

## Установка

- Скачать скрипт
- Создать в директории со скриптом файл `.env` внести туда `VK_GROUP_ID=ID` и `VK_TOKEN=Token`.
TOKEN нужно получить по [этой](https://vk.com/dev/implicit_flow_user) инструкции. VK_GROUP_ID можно получить [тут](https://regvk.com/id/)
- Создать виртуальное окружение. Например, командой `python -m venv env`
- Войти в виртуальное окружение. Например, командой `source env/bin/activate`
- Установить зависимости командой `pip install -r requirements.txt`

## Использование скрипта

Создайте приложение в VK

Запустить скрипт командой
> `python main.py`
