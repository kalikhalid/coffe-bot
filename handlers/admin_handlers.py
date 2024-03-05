from aiogram.enums import ParseMode
from db.controller import DbController
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from messages import *
from config import *

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
router = Router()
controller = DbController(DB_NAME)


@router.message(Command("addadmin"))
async def add_admin(message: Message) -> None:
    """
    adding a new admin
    example: /addadmin telegram_chat_id address_id
    """
    result = controller.dbadd_admin(message.text, message.chat.id)
    if not result:
        await message.answer(
            "Вы не имеете доступа или аргументы комманды введены не правильно."
        )
    else:
        await message.answer("Успешно!")


@router.message(Command("addressesid"))
async def addresses_id(message: Message):
    """
    list of addresses of our coffee shops with their id
    """
    msg = controller.get_addresses()
    await message.answer(text=msg)


@router.message(Command("complorder"))
async def complite_order(message: Message):
    """
    mark the order as completed
    example: /complorder order_id
    """
    if not controller.check_user(message.chat.id):
        return
    ordr_id = str(message.text.split("/complorder")[1][1:]).strip()
    print(ordr_id)
    if not ordr_id.isdigit():
        return
    user_id = controller.get_user_id_by_order_id(int(ordr_id))
    if user_id:
        await bot.send_message(
            chat_id=user_id, text="Ваш заказа готов. Скорее забирайте!"
        )
        controller.complite_order(ordr_id)
        await message.answer("Успешно!")
        return
    await message.answer("Такого заказа нет или он уже выполнен.")
