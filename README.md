Этот проект содержит два сервиса на FastAPI:

1. **Todo Service** – сервис для управления списком задач.

- REST API для создания, редактирования и удаления задач  
- Swagger документация доступна по `/docs`

3. **Short URL Service** – сервис для сокращения ссылок.

- REST API для сокращения длинных URL  
- Генерирует короткий ID и выполняет редирект на исходный URL  
- Swagger документация доступна по `/docs`

##  Требования
- Docker  
- Python 3.11+ (для локального запуска без Docker)

Оба сервиса упакованы в Docker и могут запускаться независимо друг от друга:
1.https://hub.docker.com/repository/docker/qwemiracle12344/todo-service/general
2.https://hub.docker.com/repository/docker/qwemiracle12344/short_url-service/general

## 🐳 Запуск через Docker

### 1. Создать тома для хранения данных
```bash
docker volume create todo_data
docker volume create shorturl_data
```
Для Todo Service:```docker run -d -p 8000:80 -v todo_data:/app/data qwemiracle12344/todo-service:latest```
Для Short URL Service:```docker run -d -p 8001:80 -v shorturl_data:/app/data qwemiracle12344/short_url-service:latest```

Проверка работы

Todo Service: http://localhost:8000/docs
Short URL Service: http://localhost:8001/docs


