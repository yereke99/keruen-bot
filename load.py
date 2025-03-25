#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from config import api_token

bot = Bot(token=api_token)
storage = MemoryStorage()

dp = Dispatcher(
    bot=bot,
    storage=storage,
)

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO,)