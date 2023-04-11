#!/usr/bin/env python3

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.filters.text import Text
from config_reader import config
from question import Question, read_questions

QUESTION_FILE = '.questions'


class GameState:
    def __init__(self, question_file=QUESTION_FILE):
        self.correct_answer = None
        self.question_tuple = None
        self.current_question = None
        self.questions = read_questions(question_file)
        self.game_started = False
        self.game_ended = False

    def is_game_started(self):
        return self.game_started

    def start_game(self):
        self.current_question = 0
        self.question_tuple = self.questions[self.current_question].create_question()
        self.correct_answer = self.question_tuple[5]
        self.game_started = True
        self.game_ended = False

    def next_question(self):
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.game_started = False
            self.game_ended = True
            return
        self.question_tuple = self.questions[self.current_question].create_question()
        self.correct_answer = self.question_tuple[5]

    def is_game_ended(self) -> bool:
        return self.current_question >= len(self.questions)

    def check_answer(self, answer: int) -> bool:
        return answer == self.correct_answer

    def end_game(self):
        self.current_question = len(self.questions)
        self.game_started = False
        self.game_ended = True


START_GAME = 'Начать'
VARIANT_A = 'A'
VARIANT_B = 'B'
VARIANT_C = 'C'
VARIANT_D = 'D'

logging.basicConfig(level=logging.INFO)
bot = Bot(config.bot_token.get_secret_value())
dp = Dispatcher()


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    kb = [[types.KeyboardButton(text="Начать")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer('Добро пожаловать в игру "Кто хочет стать миллионером"! ' +
                         'Вам предстоит ответить на пять вопросов, у каждого из которых четыре варианта ответа. ' +
                         'Выберите ответ, который вы считаете правильным. ' +
                         'Если вы ответили неправильно, игра прекращается.\n' +
                         'Для начала нажмите кнопку "Начать"',
                         reply_markup=keyboard)


async def show_question(message: types.Message, game_state: GameState):
    kb = [[
        types.KeyboardButton(text="A"),
        types.KeyboardButton(text="B"),
        types.KeyboardButton(text="C"),
        types.KeyboardButton(text="D")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb,
                                         resize_keyboard=True)

    text = (game_state.question_tuple[0]
            + f'\n<b>A: </b>{game_state.question_tuple[1]}'
            + f'\n<b>B: </b>{game_state.question_tuple[2]}'
            + f'\n<b>C: </b>{game_state.question_tuple[3]}'
            + f'\n<b>D: </b>{game_state.question_tuple[4]}')

    await message.answer(text, parse_mode='HTML', reply_markup=keyboard)


async def correct_answer(message: types.Message, game_state: GameState):
    keyboard_remove = types.ReplyKeyboardRemove()
    game_state.next_question()
    await message.reply('Правильный ответ!')
    if game_state.is_game_ended():
        await message.answer('Вы ответили правильно на все вопросы!', reply_markup=keyboard_remove)
    else:
        await message.answer('Следующий вопрос:')
        await show_question(message, game_state)


async def incorrect_answer(message: types.Message, game_state: GameState):
    keyboard_remove = types.ReplyKeyboardRemove()
    game_state.end_game()
    await message.reply('Ответ неправильный. Игра закончена', reply_markup=keyboard_remove)


async def check_answer(message: types.Message, game_state: GameState, answer: int):
    if not game_state.is_game_started():
        return

    if game_state.check_answer(answer):
        await correct_answer(message, game_state)
    else:
        await incorrect_answer(message, game_state)


@dp.message(Text(START_GAME))
async def cmd_start_game(message: types.Message, game_state: GameState):
    game_state.start_game()
    await message.answer('Приступим!')
    await show_question(message, game_state)


@dp.message(Text(VARIANT_A))
async def cmd_variant_a(message: types.Message, game_state: GameState):
    await check_answer(message, game_state, 0)


@dp.message(Text(VARIANT_B))
async def cmd_variant_b(message: types.Message, game_state: GameState):
    await check_answer(message, game_state, 1)


@dp.message(Text(VARIANT_C))
async def cmd_variant_c(message: types.Message, game_state: GameState):
    await check_answer(message, game_state, 2)


@dp.message(Text(VARIANT_D))
async def cmd_variant_d(message: types.Message, game_state: GameState):
    await check_answer(message, game_state, 3)


async def main():
    game_state = GameState()
    await dp.start_polling(bot, game_state=game_state)


if __name__ == "__main__":
    asyncio.run(main())
