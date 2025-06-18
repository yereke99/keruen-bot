#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiogram import types
import datetime
from load import bot
from database import Database

class Button:
    def __init__(self) -> None:
        pass

    def _create_keyboard(self, btns):

        button = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for btn in btns:
            button.add(btn)

        return button
    
    def payment(self):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("💳 Төлем жасау", url="https://pay.kaspi.kz/pay/z1qefmoe"))
        
        return keyboard
    
    def buy_cinema(self):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("💳 Керуен өнімін сатып алу", callback_data="buy_cinema"))
        
        return keyboard
    
    def typeOfSocks(self):
        return self._create_keyboard([
            "👕 Киім (Таңдау бар)",
            "🧦 Ұзын қара түсті шұлық 5 дана",
            "🧦 Ұзын ақ түсті шұлық 5 дана",
            "🧦 Қысқа қара түсті шұлық 7 дана",
            "🧦 Қысқа ақ түсті шұлық 7 дана",
        ])

    def menu(self):
        return self._create_keyboard([
            "🧧 Ұтыс билеттерім",
            "💳 Қайтадан керуен өнімін сатып алу",
            "📨 Әкімшіге хабарлама",
            "📲 Байланыс номері",  
        ])
    
    def tg_link(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("💳 Керуен 🧦 шұлығын сатып алу", url="https://t.me/keruen_shop_bot"))
        
        return keyboard

    def again(self):
        return self._create_keyboard([
            "💳 Қайтадан керуен өнімін сатып алу",
        ])
       

    def loto(self):
        return self._create_keyboard([
            "🧧 Ұтыс билеттерім"
       ])
    
    def digits_and_cancel(self):
        buttons = [str(i) for i in range(1, 10)] + ["🔕 Бас тарту"]
        return self._create_keyboard(buttons)
    
    def menu_not_paid(self):

        return self._create_keyboard([
            #"🎬 Киноны сатып алу",
            "📨 Әкімшіге хабарлама",  
            "📲 Байланыс номері", 
        ])
    
    def admin(self):

        return self._create_keyboard([
            "📈 Статистика",
            "💸 Money",
            "👇 Just Clicked",
            "👥 Қолданушылар саны",
            "📑 Лото",
            "📨 Хабарлама жіберу",
            #"🎞 Кино беру",
            "🎁 Сыйлықтар",
        ])
    
    def gift(self):
        return self._create_keyboard([
            "🧦 1 дана шұлық",
            "🧦 2 дана шұлық",
            "🧦 3 дана шұлық",
            "🧦 4 дана шұлық",
            "🧦 5 дана шұлық",
            "🧦 6 дана шұлық",
            "🧦 7 дана шұлық",
            "🧦 8 дана шұлық",
            "🧦 9 дана шұлық",
            "🧦 10 дана шұлық",
            "💸 10 000 теңге",
            "💸 20 000 теңге",
            "💸 30 000 теңге",
            "💨 Dyson плюсесі",
            "🧼 Химчистка плюсесі",
            "◀️ Кері",
        ])



    def typeMsg(self):

        return self._create_keyboard([
            "🖋 Текстік хабарлама",
            "🖼 Картинкалық хабарлама",
            "🗣 Аудио хабарлама",
            "📹 Бейне хабарлама",
            "🔕 Бас тарту",
        ])
    
    def typeUsers(self):

        return self._create_keyboard([
            "📑 Жалпы қолданушыларға",
            "💳 Төлем 🟢 жасаған 📊 қолданушаларға",
            "🔕 Бас тарту",
        ])
    
    
    def message(self):

        return self._create_keyboard([
            "📩 Жеке хабарлама",
            "📑 Жалпы қолданушыларға",
            "👇 Just Clicked",
            "💳 Төлем 🟢 жасаған 📊 қолданушаларға",
            "💳 Төлем 🔴 жасамаған 📊 қолданушаларға",
            "⬅️ Кері",
        ])
    
    def study(self):

        return self._create_keyboard([
            "💽 Бейне сабақтарды енгізу",
            "📋 Сабақтар тізімі",
            "⬅️  Кері",
        ])
    
    def cancel(self):

        return self._create_keyboard([
            "🔕 Бас тарту",
        ])
    
    def offerta(self):

        return self._create_keyboard([
            "🟢 Келісімімді беремін",
            "🔴 Жоқ, келіспеймін",
            "🔕 Бас тарту",
        ])
    
    def agreement(self):

        return self._create_keyboard([
            "🟢 Әрине",
            "🔴 Жоқ сенімді емеспін",
            "🔕 Бас тарту",
        ])
    
    def send_contact(self):

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(types.KeyboardButton("📱 Контактімен бөлісу", request_contact=True))

        return keyboard
