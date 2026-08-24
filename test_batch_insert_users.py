from faker import Faker
from translate import Translator
import psycopg2
from psycopg2 import sql
import time
import math

# Настройки подключения к базе данных
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': '12345'
}


def translate_russian_to_english(text):
    translator = Translator(from_lang='ru', to_lang='en')
    translation = translator.translate(text)
    return translation


fake_ru = Faker('ru_RU')


def generate_test_users(count=100, batch_size=25):
    """
    Генерирует тестовые данные users с отображением прогресса
    """
    users = []

    # Добавляем двух ручных пользователей
    users.append({"USER_ID": "1", "LAST_NAME": "Ivanov", "START_WORK": "8", "END_WORK": "19"})
    users.append({"USER_ID": "2", "LAST_NAME": "Petrov", "START_WORK": "1", "END_WORK": "10"})

    total_to_generate = count - 2  # минус ручные записи
    batches = math.ceil(total_to_generate / batch_size)

    print(f"\nГенерация {total_to_generate} новых пользователей:")

    for batch in range(batches):
        start_idx = batch * batch_size
        end_idx = min(start_idx + batch_size, total_to_generate)
        batch_users = []

        for i in range(start_idx, end_idx):
            user = {
                "USER_ID": str(i + 3),  # +3 потому что уже есть 2 ручных (ID 1 и 2)
                "LAST_NAME": translate_russian_to_english(fake_ru.last_name()),
                "START_WORK": str(fake_ru.random_int(1, 24)),
                "END_WORK": str(fake_ru.random_int(1, 24))
            }
            batch_users.append(user)

        users.extend(batch_users)

        # Отображаем прогресс
        progress = ((batch + 1) / batches) * 100
        print(
            f"  Прогресс: {progress:.1f}% - Сгенерировано {len(batch_users)} пользователей (пакет {batch + 1}/{batches})")

    return users


def insert_users_to_db(users_data, batch_size=25):
    """Вставляет данные пользователей в таблицу test.users с отображением прогресса"""
    conn = None
    cursor = None
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Очищаем таблицу перед вставкой
        cursor.execute("TRUNCATE TABLE test.users RESTART IDENTITY CASCADE;")
        print("\nТаблица test.users очищена")

        # Вставляем данные пакетами
        total_records = len(users_data)
        batches = math.ceil(total_records / batch_size)

        print(f"\nВставка {total_records} записей в базу данных пакетами по {batch_size}:")
        start_time = time.time()

        for batch_num in range(batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_records)
            batch_data = users_data[start_idx:end_idx]

            # Подготавливаем запрос на вставку
            insert_query = sql.SQL("""
                INSERT INTO test.users ("USER_ID", "LAST_NAME", "START_WORK", "END_WORK")
                VALUES (%s, %s, %s, %s)
            """)

            # Вставляем пакет
            for user in batch_data:
                cursor.execute(insert_query, [
                    user['USER_ID'],
                    user['LAST_NAME'],
                    user['START_WORK'],
                    user['END_WORK']
                ])

            # Промежуточный commit для каждого пакета
            conn.commit()

            # Отображаем прогресс
            progress = ((batch_num + 1) / batches) * 100
            elapsed_time = time.time() - start_time
            records_per_second = (end_idx) / elapsed_time if elapsed_time > 0 else 0

            print(f"  Прогресс: {progress:.1f}% - Вставлено {end_idx}/{total_records} записей "
                  f"(пакет {batch_num + 1}/{batches}) - {records_per_second:.1f} записей/сек")

        total_time = time.time() - start_time
        print(f"\n✅ Успешно вставлено {total_records} записей в таблицу test.users за {total_time:.2f} секунд")

        # Проверяем результат
        cursor.execute("SELECT COUNT(*) FROM test.users")
        count = cursor.fetchone()[0]
        print(f"📊 Всего записей в таблице: {count}")

        # Показываем несколько примеров
        cursor.execute("SELECT * FROM test.users ORDER BY USER_ID LIMIT 5")
        rows = cursor.fetchall()
        print("\n📝 Примеры добавленных записей:")
        for row in rows:
            print(f"  USER_ID: {row[0]}, LAST_NAME: {row[1]}, START_WORK: {row[2]}, END_WORK: {row[3]}")

    except psycopg2.Error as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("\n🔌 Соединение с БД закрыто")


def main():
    try:
        # Количество пользователей для генерации
        n = int(input("Укажите количество пользователей для генерации (минимум 2): "))
        if n < 2:
            print("Количество пользователей должно быть не менее 2. Устанавливаю значение 2.")
            n = 2

        # Размер пакета для вставки
        batch_size = int(input("Укажите размер пакета для вставки (рекомендуется 25-50): ") or "25")

        print(f"\n🚀 Начинаем генерацию {n} пользователей...")
        print(f"📦 Размер пакета: {batch_size} записей")

        # Генерация данных
        users_data = generate_test_users(n, batch_size)
        print(f"\n✅ Сгенерировано {len(users_data)} записей пользователей")

        # Вставка в базу данных
        print("\n🔌 Подключение к базе данных...")
        insert_users_to_db(users_data, batch_size)

    except KeyboardInterrupt:
        print("\n\n⚠️ Процесс прерван пользователем")
    except ValueError as e:
        print(f"❌ Ошибка ввода: {e}")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()