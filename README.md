# CharCreator бэкенд 

## О проекте
CharCreator - сайт для создания аватара своего персонажа в настольной игре ДНД.
В этом репозитории находится серверная часть проекта CharCreator, связанная также с репозиторием базы данных.

## Инструкция к запуску с помощью Docker
1. Скопировать файл .envexample в .env
    ```shell
    cp .envexample .env
    ```
2. Установить новые значения переменных окружения в .env
3. Запустить сборку контейнеров с помощью docker-compose
    ```shell
    docker compose up -d
    ```
4. Если это первый запуск приложения, то необходимо проверить файл config.json, сгенерированный автоматически при первом запуске
5. Когда вы убедились, что данные были сгенерированы правильно, запустите предыдущую команду заново