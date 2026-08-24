from faker import Faker
import psycopg2
from psycopg2 import sql
import random
from datetime import datetime

# Настройки подключения к базе данных
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'postgres',  # Замените на имя вашей БД
    'user': 'postgres',           # Замените на ваш username
    'password': '12345'        # Замените на ваш пароль
}

fake_ru = Faker('ru_RU')

# Ручное создание тестовых данных tasks
tasks = [
    {"TASK_ID": "1", "CLIENT_ID": "1", "USER_ID": "1", "STATUS": "success", "START_DATE": "2023-05-01 09:17:00",
     "END_DATE": "2023-05-21 17:23:00"},
    {"TASK_ID": "2", "CLIENT_ID": "2", "USER_ID": "1", "STATUS": "fail", "START_DATE": "2023-05-01 10:19:00",
     "END_DATE": "2023-05-21 15:39:00"}
]

insert_query = sql.SQL("""
    INSERT INTO test.tasks ("TASK_ID", "CLIENT_ID", "USER_ID", "STATUS", "START_DATE", "END_DATE")
    VALUES 
    ("TASK_ID": "1", "CLIENT_ID": "1", "USER_ID": "1", "STATUS": "success", "START_DATE": "2023-05-01 09:17:00",
     "END_DATE": "2023-05-21 17:23:00"),
    ("TASK_ID": "2", "CLIENT_ID": "2", "USER_ID": "1", "STATUS": "fail", "START_DATE": "2023-05-01 10:19:00",
     "END_DATE": "2023-05-21 15:39:00")
""")

# Для генерации данных нужно определить tasks и users
clients = [{"CLIENT_ID": str(i)} for i in range(1, 6002)]  # 6002 задач
users = [{"USER_ID": str(i)} for i in range(1, 500)]  # 500 пользователей


# Генерация тестовых данных tasks
def generate_test_tasks(count=7000):
    generated_tasks = []
    end_limit = datetime(2026, 2, 25, 12, 3, 0)  # Преобразуем строку в datetime

    for i in range(3, count + 3):  # Начинаем с 3, чтобы уникальные ID не конфликтовали
        start_date = fake_ru.date_time_this_year()  # Generates random datetime this year

        # Убедимся, что end_date не раньше start_date
        try:
            end_date = fake_ru.date_time_between(start_date=start_date, end_date=end_limit)
        except:
            # Если start_date позже end_limit, используем start_date как end_date
            end_date = start_date

        # Format the datetime according to your desired output
        formatted_start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        formatted_end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        task = {
            "TASK_ID": str(i),
            "CLIENT_ID": str(random.randint(1, len(clients))),
            "USER_ID": str(random.randint(1, len(users))),
            "STATUS": random.choice(["success", "fail"]),
            "START_DATE": formatted_start_date,
            "END_DATE": formatted_end_date
        }
        generated_tasks.append(task)

    return generated_tasks


# #Генерация данных
# test_tasks = generate_test_tasks(n)
# 
# # Добавляем сгенерированные данные к существующему списку tasks
# tasks.extend(test_tasks)
# print("Все задачи (ручные + сгенерированные):")
# print(f"Всего задач: {len(tasks)}")
# # Если нужно вывести все задачи, раскомментируйте следующую строку:
# print(tasks)

def insert_tasks_to_db(tasks_data):
    """Вставляет данные задач в таблицу test.tasks"""
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Очищаем таблицу перед вставкой (опционально)
        cursor.execute("TRUNCATE TABLE test.tasks RESTART IDENTITY CASCADE;")
        print("Таблица test.tasks очищена")

        # Подготавливаем запрос на вставку
        insert_query = sql.SQL("""
            INSERT INTO test.tasks ("TASK_ID", "CLIENT_ID", "USER_ID", "STATUS", "START_DATE", "END_DATE")
            VALUES (%s, %s, %s, %s, %s, %s)
        """)

        # Вставляем данные
        for task in tasks_data:
            cursor.execute(insert_query, [
                task['TASK_ID'],
                task['CLIENT_ID'],
                task['USER_ID'],
                task['STATUS'],
                task['START_DATE'],
                task['END_DATE']
            ])

        # Подтверждаем транзакцию
        conn.commit()
        print(f"Успешно вставлено {len(tasks_data)} записей в таблицу test.tasks")

        # Проверяем результат
        cursor.execute("SELECT COUNT(*) FROM test.tasks")
        count = cursor.fetchone()[0]
        print(f"Всего записей в таблице: {count}")

        # Показываем несколько примеров
        cursor.execute("SELECT * FROM test.tasks LIMIT 5")
        rows = cursor.fetchall()
        print("\nПримеры добавленных записей:")
        for row in rows:
            print(f"TASK_ID: {row[0]}, CLIENT_ID: {row[1]}, USER_ID: {row[2]}, STATUS: {row[3]}, START_DATE{row[4]}, END_DATE{row[5]}")

    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Соединение с БД закрыто")


def main():
    # Количество задач для генерации
    n = int(input("Укажите количество задач для генерации: "))
    print(f"Будет сгенерировано {n} задач")

    print("Генерация данных задач...")
    tasks_data = generate_test_tasks(n)

    print(f"Сгенерировано {len(tasks_data)} записей задач")


    # Вставляем данные в базу
    print("\nПодключение к базе данных...")
    insert_tasks_to_db(tasks_data)


if __name__ == "__main__":
    main()
