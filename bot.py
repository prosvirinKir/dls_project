import asyncio
import logging
from style_transfer import * 
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, InputFile

from config import TOKEN

logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

one_photo_flg = 1

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Привет!\nИспользуй /help, '
                        'чтобы узнать список доступных команд!')


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message): 
    msg = text('Я могу сделать одну фотографии в стиле другой! Для этого нужно прислать мне две фотографии:',  
        'Первая -- это та, у которой будет изменен стиль,', 'Вторая -- это та, в каком стиле все будет.', sep='\n')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)

    
@dp.message_handler(content_types=['photo'])
async def process_photo_command(message: types.Message):
    global one_photo_flg, cnn, cnn_normalization_mean, cnn_normalization_std

    path1 = 'content/'+ str(message.from_user.id) + '.png'
    path2 = 'style/'+ str(message.from_user.id) + '.png'
    path3 = str(message.from_user.id) + '.png'

    if one_photo_flg == 1:
        one_photo_flg = 0
        await message.photo[-1].download(path1)
        message_text = 'Вот это фоточка!\nСохранил ее. Теперь скидывай вторую.'
        await bot.send_message(message.from_user.id, message_text)
        return

    one_photo_flg = 1
    await message.photo[-1].download(path2)

    content_img = image_loader(path1)
    style_img = image_loader(path2)

    await bot.send_chat_action(message.from_user.id, ChatActions.UPLOAD_DOCUMENT)
    make_magic(cnn, cnn_normalization_mean,cnn_normalization_std, content_img, style_img, path3)

    message_text = 'Вот это фоточка!\nСохранил ее. Теперь скидывай вторую.'
    await bot.send_photo(message.from_user.id, InputFile('generated/' + path3))


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    message_text = text(emojize('Я не знаю, что с этим делать :astonished:'),
                        italic('\nЯ просто напомню,'), 'что есть',
                        code('команда'), '/help')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp)