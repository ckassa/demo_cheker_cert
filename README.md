# demo_cheker_cert
Консольный скрипт для автоматического тестирования методов для рекуррентных платежей, анонимных платежей и фискализации наличных. 
Может быть использован в качестве примера кода для работы с платежами в ващших приложениях.

# Зависимости
- python 3 +
- requirements.txt

Установите зависимости командой 

`pip3 install -r requirements.txt`

В папке src разместите файл сертификата и расшифрованный публичный ключ. Как извлечь эти данные указано комментарием в коде. 

# Запуск
`python3 app.py`

# Фискализация наличных

Для тестирования функцоионала используется: 
- Тестовая услуга `15636-15727-1`
- Тестовый ЛС, который заведомо пройдет валидацию `9523238186`

# Анонимные платежи

Используется тестовая услуга `1000-13864-2` переменная объявлена в файле config.py
Для удобства оплата анонимным платежом реализована без фронтов. 
В ваших кейсах до отправки POST запроса с данными типа `application/x-www-form-urlencoded` должен предшествовать шаг, в котором вы редиректите пользователя на форму заполнения карточных данных.

# Рекуррентные платежи

Аналогично рекуррентным. Не используется кейс со вводом карточных данных. 
