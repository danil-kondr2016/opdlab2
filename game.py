from question import read_questions
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

QUESTION_FILE = '.questions'


class GameFSM(StatesGroup):
    game_begin = State()
    wait_answer = State()
    game_end = State()


class GameState:
    def __init__(self, question_file=QUESTION_FILE):
        self.correct_answer = None
        self.question_tuple = None
        self.current_question = None
        self.questions = read_questions(question_file)
        self.game_started = False

    def is_game_started(self):
        return self.game_started

    def start_game(self):
        self.current_question = 0
        self.question_tuple = self.questions[self.current_question].create_question()
        self.correct_answer = self.question_tuple[5]
        self.game_started = True

    def next_question(self):
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.game_started = False
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


async def show_question(message: types.Message, question_tuple: tuple):
    kb = [[
        types.KeyboardButton(text="A"),
        types.KeyboardButton(text="B"),
        types.KeyboardButton(text="C"),
        types.KeyboardButton(text="D")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb,
                                         resize_keyboard=True)

    text = (question_tuple[0]
            + f'\n<b>A: </b>{question_tuple[1]}'
            + f'\n<b>B: </b>{question_tuple[2]}'
            + f'\n<b>C: </b>{question_tuple[3]}'
            + f'\n<b>D: </b>{question_tuple[4]}')

    await message.answer(text, parse_mode='HTML', reply_markup=keyboard)


async def correct_answer(message: types.Message, state: FSMContext, game_state: GameState):
    keyboard_remove = types.ReplyKeyboardRemove()
    game_state.next_question()
    await state.update_data(game_state=game_state)
    await message.reply('Правильный ответ!')
    if game_state.is_game_ended():
        await message.answer('Вы ответили правильно на все вопросы!', reply_markup=keyboard_remove)
        await state.clear()
    else:
        await message.answer('Следующий вопрос:')
        await show_question(message, game_state.question_tuple)


async def incorrect_answer(message: types.Message, state: FSMContext, game_state: GameState):
    keyboard_remove = types.ReplyKeyboardRemove()
    game_state.end_game()
    await message.reply('Ответ неправильный. Игра закончена', reply_markup=keyboard_remove)
    await state.clear()


async def check_answer(message: types.Message, state: FSMContext, game_state: GameState, answer: int):
    if game_state.check_answer(answer):
        await correct_answer(message, state, game_state)
    else:
        await incorrect_answer(message, state, game_state)
