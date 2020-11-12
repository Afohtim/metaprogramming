# Metaprogarmming lab 1
Для запуску програми потрібно зайти у теку lab1 у консолі та виконати для запуску
`python main.py`

Для отримання інструкцій:
`python main.py -help`

Для перевірки фоматування:
`python main.py -verify -(d|f) path`

Для форматування:
`python main.py -format -(d|f) path`

`-d` - для форматування теки
`-f` - для форматування файлу
`path` - шлях до файлу або теки

Для того, щоб ввімкнути або вимкнути логування помилок форматування

`python main.py -logs -(true|false)`

Логи доступні у файлі `errors.log`