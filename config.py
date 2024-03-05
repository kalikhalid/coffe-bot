from aiogram import types
from aiogram.types import WebAppInfo
from os import getenv
import sqlite3

TOKEN = getenv("BOT_TOKEN")
DB_NAME = "sqlite:///main.db"
SBER_API = getenv("PAYMENT_TOKEN")
PRICES = {
    "1": types.LabeledPrice(label="Item1", amount=18000),
    "2": types.LabeledPrice(label="Item2", amount=10000),
    "3": types.LabeledPrice(label="Item3", amount=25000),
    "4": types.LabeledPrice(label="Item4", amount=25000),
}
keyboard_1 = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            types.KeyboardButton(
                web_app=WebAppInfo(
                    url="https://kalikhalid.github.io/finalwork.github.io/"
                ),
                text="🧋Сделать заказ",
            )
        ]
    ],
    input_field_placeholder="Сделаем заказ!",
)
keyboard_2 = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[[types.KeyboardButton(text="Сделать заказ")]],
    input_field_placeholder="Сделаем заказ!",
)
adrlist = []
with sqlite3.connect(DB_NAME[10:]) as con:
    cur = con.cursor()
    cur.execute("SELECT address FROM Addresses;")
    adrlist = [[types.KeyboardButton(text=i[0])] for i in cur.fetchall()]

adresses = types.ReplyKeyboardMarkup(
    resize_keyboard=True, keyboard=adrlist, input_field_placeholder="Сделаем заказ!"
)
