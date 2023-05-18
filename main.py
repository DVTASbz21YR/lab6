import telebot
from peewee import *        # импортируем все классы и объекты из peewee
from telebot import types   # используется здесь для создания кнопок

# Подключаемся к БД
db = SqliteDatabase('database.db')


# Создаем класс "пост" и характеристика
class Post(Model):
    post_id = IntegerField()
    username = CharField()
    text = CharField()
    likes = IntegerField()

    # связываем класс Post с БД
    class Meta:
        database = db


# создается таблица (если ее нет)
db.create_tables([Post])


# получаем доступ к боту
bot = telebot.TeleBot('5872856683:AAE-gcdryoBHk0fONGyycZtC7jI-FrgjiGk')


# Начало работы бота после отправки /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_1 = types.KeyboardButton('➕ Новый пост')
    button_2 = types.KeyboardButton('📱 Лента')
    button_3 = types.KeyboardButton('❌ Удалить пост')
    button_4 = types.KeyboardButton('✏ Редактировать пост')
    markup.add(button_1, button_2, button_3, button_4)
    bot.reply_to(message, "Это бот для работы с постами", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '➕ Новый пост')
def handle_add(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Введите данные в формате: № поста, ник, текст, лайки")
    bot.register_next_step_handler(msg, process_add_step)


def process_add_step(message):
    chat_id = message.chat.id
    data = message.text.split(', ')
    if len(data) == 4:
        try:
            # Новая запись в БД
            Post.create(post_id=int(data[0]), username=data[1], text=data[2], likes=data[3])
            bot.send_message(chat_id, "Данные успешно добавлены")
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка при добавлении поста: {e}")
    else:
        bot.send_message(chat_id, "Неверный формат данных")


@bot.message_handler(func=lambda message: message.text == '📱 Лента')
def handle_list(message):
    chat_id = message.chat.id
    rows = Post.select()
    data = ''
    for row in rows:
        data += f"№ поста: {row.post_id}\nНик: {row.username}\nТекст: {row.text}\nЛайки: {row.likes}\n\n"
    if data:
        bot.send_message(chat_id, data)
    else:
        bot.send_message(chat_id, "Постов нет")


@bot.message_handler(func=lambda message: message.text == '❌ Удалить пост')
def handle_delete(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Введите номер поста для удаления:")
    bot.register_next_step_handler(msg, process_delete_step)


def process_delete_step(message):
    chat_id = message.chat.id
    number = message.text
    try:
        # Есть ли пост с таким ID?
        post = Post.get(Post.post_id == number)
        post.delete_instance()
        bot.send_message(chat_id, "Пост удален")
    except Post.DoesNotExist:
        bot.send_message(chat_id, "Поста с таким номером не существует")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при удалении поста: {e}")


@bot.message_handler(func=lambda message: message.text == '✏ Редактировать пост')
def handle_edit(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Введите номер поста")
    bot.register_next_step_handler(msg, process_edit_step)


def process_edit_step(message):
    chat_id = message.chat.id
    number = message.text
    try:
        # Есть ли пост с таким ID?
        post = Post.get(Post.post_id == number)
        msg = bot.send_message(chat_id, "Выбрана запись:\n"
                                        f"№ поста: {post.post_id}\n"
                                        f"Ник: {post.username}\n"
                                        f"Текст поста: {post.text}\n"
                                        f"Лайки: {post.likes}\n\n"
                                        "Введите новые данные в формате: ник, текст, лайки")
        bot.register_next_step_handler(msg, lambda msg: process_update_step(msg, post))
    except Post.DoesNotExist:
        bot.send_message(chat_id, "Запись с указанным номером не найдена.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при редактировании записи: {e}")


def process_update_step(message, post):
    chat_id = message.chat.id
    data = message.text.split(', ')
    if len(data) == 3:
        try:
            # Обновляем данные записи в базе данных
            post.username = data[0]
            post.text = data[1]
            post.likes = data[2]
            post.save()
            bot.send_message(chat_id, "Пост обновлен")
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка при обновлении данных: {e}")
    else:
        bot.send_message(chat_id, "Неверный формат данных")


# Запуск
bot.polling()
