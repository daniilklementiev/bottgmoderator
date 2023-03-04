import logging
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta
import config as cfg
import pymysql
from aiogram.types import ParseMode

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)

connection = pymysql.connect(
    host="us-east.connect.psdb.cloud",
    user="ndm1sfdozsx2lrlyuk6h",
    password="pscale_pw_oJSJsF9a7vPjCXmXgJt7V237A0lOzzd0nbTHCBrolX5",
    db="pythonbot",
    cursorclass=pymysql.cursors.DictCursor,
    ssl={"rejectUnauthorized": True}
)

async def execute_query(query, *args):
    with connection.cursor() as cursor:
        await cursor.execute(query, args)
        result = await cursor.fetchall()
        return result

@dp.message_handler(content_types=['new_chat_members'])
async def new_chat_member(message):
    # extract relevant information from the chat_member object
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # insert the user into the MySQL table
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Users (user_id, chat_id, username, first_name, last_name) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (user_id, chat_id, username, first_name, last_name))
        connection.commit()
        print(f"User {username} added to database.")
    except Exception as e:
        print(f"Error inserting user into database: {e}")


@dp.message_handler(commands=['мут', 'mute'], commands_prefix='./', is_chat_admin=True)
async def mute(message):
      name1 = message.from_user.get_mention(as_html=True)
      if not message.reply_to_message:
         await message.reply("Эта команда должна быть ответом на сообщение!")
         return
      try:
         muteint = int(message.text.split()[1])
         mutetype = message.text.split()[2]
         comment = " ".join(message.text.split()[3:])
      except IndexError:
         await message.reply('Не хватает аргументов! Пример:`/мут 1 ч причина.`')
         return
      except:
         await message.reply('Он админ лол чел')
         return
      if mutetype == "ч" or mutetype == "часов" or mutetype == "час":
         dt = datetime.now() +timedelta(hours=muteint)
         timestamp = dt.timestamp()
         until_date = dt.strftime('%d.%m.%Y %H:%M:%S')
         await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=timestamp)
         await message.reply(f'<b>Решение было принято:</b> {name1}. <b>Нарушитель:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a> заключен под стражу. <b>До:</b> {until_date}. <b>Причина:</b> {comment}.',  parse_mode='html')
         await bot.delete_message(message.chat.id, message.message_id)
         await add_mute(message.reply_to_message.from_user.id, until_date)
      elif mutetype == "м" or mutetype == "минут" or mutetype == "минуты":
         dt = datetime.now() + timedelta(minutes=muteint)
         timestamp = dt.timestamp()
         until_date = dt.strftime('%d.%m.%Y %H:%M:%S')
         await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=timestamp)
         await message.reply(f'<b>Решение было принято:</b> {name1}. <b>Нарушитель:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a> заключен под стражу <b>До:</b> {until_date}. <b>Причина:</b> {comment}.',  parse_mode='html')
         await bot.delete_message(message.chat.id, message.message_id)
         await add_mute(message.reply_to_message.from_user.id, until_date)
      elif mutetype == "д" or mutetype == "дней" or mutetype == "день":
         dt = datetime.now() + timedelta(days=muteint)
         timestamp = dt.timestamp()
         until_date = dt.strftime('%d.%m.%Y %H:%M:%S')
         await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=timestamp)
         # удалить текущее
         await bot.delete_message(message.chat.id, message.reply_to_message.from_user.id)
         await message.reply(f'<b>Решение было принято:</b> {name1}. <b>Нарушитель:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a> заключен под стражу <b>До:</b> {until_date}. <b>Причина:</b> {comment}.',  parse_mode='html')
         await bot.delete_message(message.chat.id, message.message_id)
         await add_mute(message.reply_to_message.from_user.id, until_date)


@dp.message_handler(commands=['бан', 'ban'], commands_prefix='./', is_chat_admin=True)
async def ban_user_command(message: types.Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        try:
            ban_reason = ' '.join(message.text.split()[2:])
        except IndexError:
            ban_duration = None
            ban_reason = ' '.join(message.text.split()[1:])

        await bot.kick_chat_member(message.chat.id, user_id, until_date=None)
        await message.reply(f'<b>Решение было принято:</b> {message.from_user.get_mention(as_html=True)}. <b>Нарушитель:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a> отправился в след за русским кораблем.',  parse_mode='html')
        await add_ban(user_id)
    else:
        await message.reply('Команда должна быть ответом на сообщение!')



@dp.message_handler(commands=['анмут', 'unmute'], commands_prefix='./', is_chat_admin=True)
async def mute(message):
      name1 = message.from_user.get_mention(as_html=True)
      if not message.reply_to_message:
         await message.reply("Эта команда должна быть ответом на сообщение!")
         return
      try:
         await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(True,True,True,True,True,True,True,True,True), until_date = 0)
         await message.reply(f'<b>Решение было принято:</b> {name1}. <b>Пользователь:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a> освобожден из-под стражи.',  parse_mode='html')
         await bot.delete_message(message.chat.id, message.message_id)
         await remove_mute(message.reply_to_message.from_user.id)
      except:
         await message.reply("У меня нет прав на это действие!")


# Разблокировать пользователя по id введенному в аргумента
@dp.message_handler(commands=['unban', 'анбан'], commands_prefix='./', is_chat_admin=True)
async def unban(message):
      name1 = message.from_user.get_mention(as_html=True)
      if not message.reply_to_message:
         await message.reply("Эта команда должна быть ответом на сообщение!")
         return
      try:
         await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
         await message.reply(f'<b>Решение было принято:</b> {name1}. <b>Пользователь:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a> разблокирован.',  parse_mode='html')
         await remove_ban(message.reply_to_message.from_user.id)
      except:
         await message.reply("У меня нет прав на это действие!")


# Add mute to user
async def add_mute(user_id: int, duration: int):
    try:
        with connection.cursor() as cursor:
            mute_expiration = datetime.now() + timedelta(minutes=duration)
            await cursor.execute(
                """
                UPDATE Users SET mute = 1, duration = %s, mute_expiration = %s
                WHERE id = %s
                """,
                (duration, mute_expiration, user_id)
            )
            await connection.commit()
    except Exception as e:
        print(e)

# Remove mute from user
async def remove_mute(user_id: int):
    async with connection.cursor() as cursor:
        await cursor.execute(
            """
            UPDATE Users SET mute = 0, duration = null, mute_expiration = null
            WHERE id = %s
            """,
            (user_id,)
        )
        await connection.commit()


# Add ban to user
async def add_ban(user_id: int):
    async with connection.cursor() as cursor:
        await cursor.execute(
            """
            UPDATE Users SET ban = 1, duration = 1, ban_expiration = 1
            WHERE id = %s
            """,
            (user_id)
        )
        await connection.commit()

async def remove_ban(user_id: int):
    async with connection.cursor() as cursor:
        await cursor.execute(
            """
            UPDATE Users SET ban = 0, duration = null, ban_expiration = null
            WHERE id = %s
            """,
            (user_id,)
        )
        await connection.commit()



#dp.loop.create_task(create_users_table())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
