from faker import Faker
import psycopg2
from psycopg2 import sql

# Настройки подключения к базе данных
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'postgres',  # Замените на имя вашей БД
    'user': 'postgres',           # Замените на ваш username
    'password': '12345'        # Замените на ваш пароль
}

fake_ru = Faker('ru_RU')

# Ручное создание тестовых данных clients
clients = [
    {"CLIENT_ID": "1", "NAME": "ИП Шолохов", "CATEGORY": "Малый бизнес"},
    {"CLIENT_ID": "2", "NAME": 'ООО "Звездочка"', "CATEGORY": "Средний бизнес"}]

# Генерация тестовых данных clients
def generate_test_clients(count=6000):
    for i in range(3, count + 3):  # начинаем с 3, чтобы уникальные ID не конфликтовали
        client = {
            "CLIENT_ID": str(i),
            "NAME": fake_ru.company(),
            "CATEGORY": fake_ru.random_element(["Малый бизнес", "Средний бизнес"])
        }
        clients.append(client)
    return clients

# # Вывод результата clients
# test_clients = generate_test_clients(n)
# clients.extend(test_clients)
# print("Все задачи (ручные + сгенерированные):")
# print(f"Всего клиентов: {len(clients)}")
# print(clients)



def insert_clients_to_db(clients_data):
    """Вставляет данные клиентов в таблицу test.clients"""
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Очищаем таблицу перед вставкой (опционально)
        cursor.execute("TRUNCATE TABLE test.clients RESTART IDENTITY CASCADE;")
        print("Таблица test.clients очищена")

        # Подготавливаем запрос на вставку
        insert_query = sql.SQL("""
            INSERT INTO test.clients ("CLIENT_ID", "NAME", "CATEGORY")
            VALUES (%s, %s, %s)
        """)

        # Вставляем данные
        for user in clients_data:
            cursor.execute(insert_query, [
                user['CLIENT_ID'],
                user['NAME'],
                user['CATEGORY']
            ])

        # Подтверждаем транзакцию
        conn.commit()
        print(f"Успешно вставлено {len(clients_data)} записей в таблицу test.clients")

        # Проверяем результат
        cursor.execute("SELECT COUNT(*) FROM test.clients")
        count = cursor.fetchone()[0]
        print(f"Всего записей в таблице: {count}")

        # Показываем несколько примеров
        cursor.execute("SELECT * FROM test.clients LIMIT 5")
        rows = cursor.fetchall()
        print("\nПримеры добавленных записей:")
        for row in rows:
            print(f"CLIENT_ID: {row[0]}, NAME: {row[1]}, CATEGORY: {row[2]}")

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
    # Количество клиентов для генерации
    n = int(input("Укажите количество клиентов для генерации: "))
    print(f"Будет сгенерировано {n} клиентов")

    print("Генерация данных клиентов...")
    clients_data = generate_test_clients(n)

    print(f"Сгенерировано {len(clients_data)} записей клиентов")


    # Вставляем данные в базу
    print("\nПодключение к базе данных...")
    insert_clients_to_db(clients_data)


if __name__ == "__main__":
    main()