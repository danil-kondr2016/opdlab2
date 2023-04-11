#!/usr/bin/env python3

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import config
from game import GameState, GameFSM, show_question, check_answer

START_GAME = 'Начать'
VARIANT_A = 'A'
VARIANT_B = 'B'
VARIANT_C = 'C'
VARIANT_D = 'D'

logging.basicConfig(level=logging.INFO)
router = Router()


@router.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = [[types.KeyboardButton(text="Начать")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer('Добро пожаловать в игру "Кто хочет стать миллионером"! ' +
                         'Вам предстоит ответить на пять вопросов, у каждого из которых четыре варианта ответа. ' +
                         'Выберите ответ, который вы считаете правильным. ' +
                         'Если вы ответили неправильно, игра прекращается.\n' +
                         'Для начала нажмите кнопку "Начать"',
                         reply_markup=keyboard)


@router.message(Text(START_GAME))
async def cmd_start_game(message: types.Message, state: FSMContext):
    await message.answer('Приступим!')
    await state.set_state(GameFSM.wait_answer.state)
    await state.set_data({'game_state': GameState()})

    data = await state.get_data()
    game_state = data["game_state"]
    game_state.start_game()
    await state.update_data(game_state=game_state)
    await show_question(message, game_state.question_tuple)


@router.message(GameFSM.wait_answer, Text(VARIANT_A))
async def cmd_variant_a(message: types.Message, state: FSMContext):
    data = await state.get_data()
    game_state = data["game_state"]
    await check_answer(message, state, game_state, 0)


@router.message(GameFSM.wait_answer, Text(VARIANT_B))
async def cmd_variant_b(message: types.Message, state: FSMContext):
    data = await state.get_data()
    game_state = data["game_state"]
    await check_answer(message, state, game_state, 1)


@router.message(GameFSM.wait_answer, Text(VARIANT_C))
async def cmd_variant_c(message: types.Message, state: FSMContext):
    data = await state.get_data()
    game_state = data["game_state"]
    await check_answer(message, state, game_state, 2)


@router.message(GameFSM.wait_answer, Text(VARIANT_D))
async def cmd_variant_d(message: types.Message, state: FSMContext):
    data = await state.get_data()
    game_state = data["game_state"]
    await check_answer(message, state, game_state, 3)


async def main():
    bot = Bot(config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
