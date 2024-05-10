import locale
import os
import time
import pdfkit
import telebot
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import psycopg2

#(api токен бота)
bot = telebot.TeleBot('6411012518:AAGh59TrB_12VPlgZbByBunp4Mdy6JOapHU')


#функция, которая будет вызываться при получении сообщения от пользователя
@bot.message_handler(content_types=['text'])
def id_student(message):
    try:
        # запрашиваем айди студента
        bot.send_message(message.chat.id, "Введите табельный номер студента:")
        bot.register_next_step_handler(message, surname_message)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка')

def surname_message(message):
    try:
        # сохраняем id пользователя
        id_stu = message.text
        #запрашиваем у пользователя данные
        bot.send_message(message.chat.id, "Введите фамилию:")
        bot.register_next_step_handler(message, ask_first_name, id_stu)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка')

#функция для обработки фамилии
def ask_first_name(message, id_stu):
    try:
        #сохраняем фамилию пользователя
        fio = message.text

        #запрашиваем имя пользователя
        bot.send_message(message.chat.id, "Введите имя:")
        bot.register_next_step_handler(message, ask_middle_name, id_stu, fio)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка')

#функция для обработки имени
def ask_middle_name(message, id_stu, fio):
    try:
        # сохраняем имя пользователя
        fio += " " + message.text

        # запрашиваем отчество пользователя
        bot.send_message(message.chat.id, "Введите отчество:")
        bot.register_next_step_handler(message, ask_birth_date, id_stu, fio)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка')

# функция для обработки отчества
def ask_birth_date(message, id_stu, fio):
    try:
        # сохраняем отчество пользователя
        fio += " " + message.text

        # запрашиваем дату рождения пользователя
        bot.send_message(message.chat.id, "Введите дату рождения (в формате ДД.ММ.ГГГГ):")
        bot.register_next_step_handler(message, ask_institute, id_stu, fio)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка')

# функция для обработки института
def ask_institute(message, id_stu, fio):
    try:
        # сохраняем дату рождения пользователя
        birth_date = message.text

        # запрашиваем институт пользователя
        bot.send_message(message.chat.id, "Введите институт:")
        bot.register_next_step_handler(message, ask_group, id_stu, fio, birth_date)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка')

# функция для обработки группы
def ask_group(message, id_stu, fio, birth_date):
    try:
        # сохраняем институт пользователя
        institute = message.text

        # запрашиваем группу пользователя
        bot.send_message(message.chat.id, "Введите группу:")
        bot.register_next_step_handler(message, ask_course, id_stu, fio, birth_date, institute)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка')

# функция для обработки курса
def ask_course(message, id_stu, fio, birth_date, institute):
    try:
        # сохраняем группу пользователя
        group = message.text

        # запрашиваем курс пользователя
        bot.send_message(message.chat.id, "Введите курс:")
        bot.register_next_step_handler(message, ask_place_and_quantity, id_stu, fio, birth_date, institute, group)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка')

# функция для обработки места предоставления
def ask_place_and_quantity(message, id_stu, fio, birth_date, institute, group):
    try:
        # сохраняем курс пользователя
        course = message.text

        # запрашиваем место предоставления
        bot.send_message(message.chat.id, "Введите место предоставления:")
        bot.register_next_step_handler(message, generate_pdf, id_stu, fio, birth_date, institute, group, course)
    except Exception as e:
        bot.reply_to(message, 'Данные введены некорректно')


# функция для генерации и отправки pdf-файла
def generate_pdf(message, id_stu, fio, birth_date, institute, group, course):
    try:
        # сохраняем место предоставления
        place = message.text

        folder = os.path.abspath('.')

        # получаем html-шаблон
        template = Environment(loader=FileSystemLoader('.')).get_template('шаблон_справки.html')

        # Подключение к базе данных
        conn = psycopg2.connect(database='5semproekt', user='postgres', password='0000', host='localhost', port='5432')
        cursor = conn.cursor()

        # Функция для выполнения проверки пользователя
        def check_user(tabel_student):
            # Выполнение SQL-запроса для проверки пользователя
            query = f"SELECT * FROM Студент WHERE id_Студента='{id_stu}'"
            cursor.execute(query)
            user = cursor.fetchone()
            return user is not None

        if check_user(id_stu):
        #если такой студент найден в бд
            query = f"select TRIM(Студент.Фамилия), TRIM(Студент.Имя), TRIM(Студент.Отчество), Студент.Дата_рождения, TRIM(Студент.Год_поступления)," \
                    f"TRIM(Специальность.Уровень_образования), TRIM(Специальность.Форма_обучения), TRIM(Специальность.Институт), TRIM(Специальность.Наименование_специальности), " \
                    f"Приказы.* from Студент " \
                    f"right join Группа as г ON г.id_Группы = Студент.id_Группы " \
                    f"right join Специальность ON Специальность.id_Специальности = г.id_Специальности" \
                    f" right join Студент_Приказы ON Студент_Приказы.id_Студента = Студент.id_Студента" \
                    f" right join Приказы on Приказы.id_Приказа = Студент_Приказы.id_Приказа " \
                    f"where Студент.id_Студента = '{id_stu}'"
            cursor.execute(query)
            result = cursor.fetchone()  # Получение строки результата запроса
            if result:
                surname = result[0]  # Доступ к столбцу из строки результата
                name = result[1]
                patronic = result[2]
                date_of_birth = result[3]
                year = result[4]
                level_edu = result[5]
                form_edu = result[6]
                inst = result[7]
                name_spec = result[8]
                id_prik = result[9]
                date_prik = result[10].strftime("%d.%m.%Y")

            #считаем год окончания обучения
            if level_edu == 'Бакалавриат':
                date_end_university = int(year) + 4
            else:
                date_end_university = int(year) + 5

            # обработка времени получения справки
            locale.setlocale(locale.LC_TIME, "ru_RU")
            month = time.strftime("%B", time.localtime())

            # склонение месяца в родительный падеж для даты получения справки
            if month.endswith('ь'):
                month_genitive = month[:-1] + 'я'
            else:
                month_genitive = month + 'а'

            # собираем дату получения справки
            date = str(datetime.now().day) + ' ' + month_genitive + ' ' + str(datetime.now().year)

            # меняем падеж у формы обучения
            form_edu = form_edu[:-2] + 'ой'

            # рендерим шаблон с введёнными значениями
            rendered_template = template.render(fio=fio, birth_date=birth_date, institute=institute, group=group,
                                                course=course, place=place, date=date, year=year, level_edu=level_edu.lower(), form_edu=form_edu.lower(),
                                                id_prik=id_prik, date_prik=date_prik, date_end_university=date_end_university, folder=folder)


            # задаем опции для сохранения в pdf (в данном случае размер страницы)
            options = {
                'page-height': '794px',
                'page-width': '559px',
                'enable-local-file-access': ''
            }

            # сохраняем результат в pdf-файл
            pdfkit.from_string(rendered_template, 'result.pdf', options)

            # отправляем сгенерированный pdf-файл пользователю
            bot.send_document(message.chat.id, open('result.pdf', 'rb'))

            cursor.close()
            conn.close()

        # если пользователь не найден
        else:
            bot.reply_to(message, 'Студент не найден')

    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка!!!")

# запускаем бота
bot.polling()