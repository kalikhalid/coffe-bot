import g4f
from aiogram import Router, F
from aiogram.filters import Command
from main import bot
from aiogram.types import ReplyKeyboardRemove, PreCheckoutQuery
from aiogram.enums.content_type import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, FSInputFile
from db.controller import DbController
from messages import *
from config import *


class SimpleState(StatesGroup):
    name = State()
    adress = State()


router = Router()
db_controller = DbController(DB_NAME)


@router.message(Command("history"))
async def get_history(message: Message):
    """
    user order history
    """
    await message.answer(text=db_controller.get_history_by_id(message.chat.id))


@router.message(Command("low"))
async def get_low(message: Message):
    photo = FSInputFile("photos/esspresso.jpg")
    await message.answer_photo(photo, reply_markup=keyboard_1, caption=LOW)


@router.message(Command("high"))
async def get_high(message: Message):
    """
    most popular drink or snack
    """
    max_item = db_controller.get_high()
    await message.answer(
        text=f"Самым популярным и любимом напитком в нашей кофейне является {max_item}. Его заказывают чаще всего."
    )


@router.message(Command("custom"))
async def get_custom(message: Message):
    """
    select a product for user using GPT 3
    """
    menu = db_controller.get_menu()
    text = message.text.split("/custom")[1][1:]
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Ты нейросеть внедренная в телеграм бот для заказа кофе. Пользователи будут спрашивать у тебя на счет кофе. Меню кофейни - {menu}. Ты ничего не должен делать кроме рекомендации кофе из меню кофейни.",
            },
            {"role": "assistant", "content": "Хорошо"},
            {"role": "user", "content": text},
        ],
        stream=False,
    )
    await message.answer(text=response)


@router.message(Command("help"))
async def help(message: Message) -> None:
    """
    help message
    """
    if not db_controller.check_user(message.chat.id):
        ani = FSInputFile("photos/AnimatedSticker.tgs")
        await message.answer_animation(ani)
        await message.answer(text=HELP, reply_markup=keyboard_1)
        return
    await message.answer(ADMIN_HELP)


@router.message(Command("start"))
async def start(message: Message):
    """
    start message
    """
    photo = FSInputFile("photos/logo.jpg")
    await message.answer_photo(photo, caption=START, reply_markup=keyboard_2)


@router.message(Command("order"))
async def order(message: Message, state: FSMContext):
    """
    make an order
    """
    a = ReplyKeyboardRemove()
    await message.answer("Введите ваше имя", reply_markup=a)
    await state.set_state(SimpleState.name)


@router.message(F.text == "Сделать заказ")
async def start_order(message: Message, state: FSMContext):
    """
    make an order
    """
    a = ReplyKeyboardRemove()
    await message.answer("Введите ваше имя", reply_markup=a)
    await state.set_state(SimpleState.name)


@router.message(SimpleState.name)
async def get_name(messages: Message, state: FSMContext):
    """
    getting name
    """
    await state.update_data(name=messages.text)
    await messages.answer(
        text="Выберите адрес кофейни в котором хотите получить заказ",
        reply_markup=adresses,
    )
    await state.set_state(SimpleState.adress)


@router.message(F.content_type.in_(ContentType.WEB_APP_DATA))
async def web_data(message: Message, state: FSMContext):
    """
    web app work
    """
    prc = [PRICES[i] for i in message.web_app_data.data.split()]
    await bot.send_invoice(
        message.chat.id,
        title="Оплата заказa",
        is_flexible=False,
        currency="RUB",
        description="oплата",
        payload="payload",
        prices=prc,
        provider_token=SBER_API,
    )
    result = db_controller.add_to_history(
        web_app_data=message.web_app_data.data, id=message.chat.id
    )
    await state.update_data(order=result)


@router.pre_checkout_query(lambda q: True)
async def pre_checkout_order(pp: PreCheckoutQuery):
    """
    pre checkout web app data
    """
    await bot.answer_pre_checkout_query(pp.id, ok=True)


@router.message(F.content_type.in_(ContentType.SUCCESSFUL_PAYMENT))
async def succsesful_payment(message: Message, state: FSMContext):
    """
    succsesful payment handler
    """
    msg = f"Оплата прошла успешно. Как только ваш заказ будет готов мы пришлем уведомление!"
    await message.answer(msg)
    cur_order = await state.get_data()
    ordr_id, admins_list = db_controller.make_order(message.from_user.id, cur_order)
    for admin in admins_list:
        await bot.send_message(
            chat_id=admin,
            text=f"Новый заказ:\n{cur_order['order']}\nId заказа - {ordr_id}",
        )

    await state.clear()


@router.message(SimpleState.adress)
async def get_addres(message: Message, state: FSMContext):
    """
    getting address
    """
    await state.update_data(adress=message.text)
    await message.answer(text="Делаем заказ?", reply_markup=keyboard_1)
