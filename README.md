# RZHD

Этот проект представляет собой чат-бота поддержки. Бот принимает вопросы от пользователей, автоматически генерирует ответы с помощью API. Данная инструкция дает возможность протестировать бота локально

## Функционал

- **Пользовательский интерфейс**: Пользователь может задать вопрос, который будет обработан ботом.
- **API-ответы**: Бот отправляет запросы к API для генерации ответов на вопросы пользователей.

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/afarut/RZDTrainRAG.git
   cd RZDTrainRAG/web
2. Перейдите в docker-compose.yml и добавьте необходимые переменные окружения:

## Запуск бота
1. Перейдите в главную дерикторию
2. Если с windows:
   ```bash
   docker-compose up
2. Если с unix-подобной системы:
   ```bash 
   docker compose up
