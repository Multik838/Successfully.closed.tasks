# Анализ успешно закрытых задач

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Проект по анализу данных о задачах, клиентах и менеджерах. Основная цель — выявление закономерностей в успешности выполнения задач, оценка эффективности менеджеров и определение клиентов, ведущих внешнеэкономическую деятельность.

## 📋 Постановка задачи

1. **Определить топ-5 менеджеров** по доле успешно закрытых задач.
2. **Выявить менеджеров с показателями хуже среднего**: для каждой категории бизнеса найти менеджеров, у которых доля неуспешных задач выше, чем в среднем по всем менеджерам и категориям.
3. **Определить факт ведения ВЭД** клиентами на основе открытых/банковских данных.

## 🏗️ Структура репозитория
Successfully.closed.tasks/
├── SQL_Юдаков.txt # SQL-скрипт создания БД и таблиц
├── test_batch_insert_users.py # Генерация и вставка пользователей (пакетно)
├── test_insert_clients.py # Генерация и вставка клиентов
├── test_insert_tasks.py # Генерация и вставка задач
├── clients_data.csv # Данные о клиентах
├── tasks_data.csv # Данные о задачах
├── users_data.csv # Данные о пользователях (менеджерах)
└── README.md # Описание проекта

## 🗄️ Модель данных

Проект использует базу данных **PostgreSQL** со следующей структурой:

### Таблица `users` (менеджеры)
| Поле       | Тип      | Описание                    |
|------------|----------|-----------------------------|
| `USER_ID`  | integer  | Уникальный идентификатор    |
| `LAST_NAME`| text     | Фамилия менеджера           |
| `START_WORK`| integer | Час начала рабочего дня     |
| `END_WORK` | integer  | Час окончания рабочего дня  |

### Таблица `clients` (клиенты)
| Поле        | Тип      | Описание                       |
|-------------|----------|--------------------------------|
| `CLIENT_ID` | integer  | Уникальный идентификатор       |
| `NAME`      | text     | Наименование клиента           |
| `CATEGORY`  | text     | Категория бизнеса              |

### Таблица `tasks` (задачи)
| Поле         | Тип      | Описание                           |
|--------------|----------|------------------------------------|
| `TASK_ID`    | integer  | Уникальный идентификатор задачи    |
| `CLIENT_ID`  | integer  | Внешний ключ → `clients`           |
| `USER_ID`    | integer  | Внешний ключ → `users`             |
| `STATUS`     | text     | Статус (`success` / `fail`)        |
| `START_DATE` | text     | Дата и время начала задачи         |
| `END_DATE`   | text     | Дата и время завершения задачи     |

> **Примечание:** Подробный SQL-скрипт создания таблиц и базы данных находится в файле [`SQL_Юдаков.txt`](SQL_Юдаков.txt).

## ⚙️ Установка и настройка

### 1. Клонирование репозитория
```bash```
'git clone https://github.com/Multik838/Successfully.closed.tasks.git'
'cd Successfully.closed.tasks'

### 2. Установка зависимостей

  pip install faker translate psycopg2

### 3. Настройка базы данных
- Установите и запустите PostgreSQL.
- Выполните скрипт из файла SQL_Юдаков.txt для создания базы данных и таблиц.
- В каждом Python-скрипте укажите свои параметры подключения в переменной DB_CONFIG:

    DB_CONFIG = {
      'host': 'localhost',
      'port': '5432',
      'database': 'postgres',  # ваша БД
      'user': 'postgres',      # ваш пользователь
      'password': '12345'      # ваш пароль
  }

### 4. Генерация и загрузка тестовых данных
- Клиенты: python test_insert_clients.py (запросит количество)
- Пользователи: python test_batch_insert_users.py (генерирует 100 записей, можно изменить в коде)
- Задачи: python test_insert_tasks.py (генерирует 7000 записей, можно изменить в коде)

**Аналитические запросы SQL**
- Ниже приведены примеры SQL-запросов для решения поставленных задач:
  Топ-5 менеджеров по доле успешных задач
      sql
      SELECT 
          u."LAST_NAME",
          COUNT(DISTINCT t."TASK_ID") AS total_tasks,
          SUM(CASE WHEN t."STATUS" = 'success' THEN 1 ELSE 0 END) AS success_tasks,
          (SUM(CASE WHEN t."STATUS" = 'success' THEN 1 ELSE 0 END) / COUNT(DISTINCT t."TASK_ID")::float) * 100 AS success_rate
      FROM test.tasks t
      JOIN test.users u ON t."USER_ID" = u."USER_ID"
      GROUP BY u."LAST_NAME"
      ORDER BY success_rate DESC
      LIMIT 5;
