from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_calc = KeyboardButton(text='Рассчитать')
button_info = KeyboardButton(text='Информация')
button_buy = KeyboardButton(text='Купить')
kb.add(button_calc)
kb.add(button_info)
kb.add(button_buy)

inline_kb = InlineKeyboardMarkup(resize_keyboard=True)
inline_button_calc = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
inline_button_formula = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb.add(inline_button_calc)
inline_kb.add(inline_button_formula)

inline_kb_product = InlineKeyboardMarkup(resize_keyboard=True)
inline_button_product1 = InlineKeyboardButton('Product1', callback_data="product_buying")
inline_button_product2 = InlineKeyboardButton('Product2', callback_data="product_buying")
inline_button_product3 = InlineKeyboardButton('Product3', callback_data="product_buying")
inline_button_product4 = InlineKeyboardButton('Product4', callback_data="product_buying")
inline_kb_product.add(inline_button_product1)
inline_kb_product.add(inline_button_product2)
inline_kb_product.add(inline_button_product3)
inline_kb_product.add(inline_button_product4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=inline_kb)


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Посчитай сколько нужно кушать каллорий в день, а так же можете приобрести витамины.')


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i in range(1, 5):
        await message.answer(f'Название: Product{i}| Описание: описание{i}| Цена: {i * 100}')
        with open(f'picture/{i}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=inline_kb_product)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5 \n ДЛЯ МУЖЧИН."
                              "\n ******************* \n"
                              "10 * масса тела (кг) + 6,25 * рост (см) – 5 * возраст (лет) — 161 \n ДЛЯ ЖЕНЩИН."
                              )
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    result_men = int(10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5)
    result_women = int(10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161)
    await message.answer(f'Ваша норма калорий {result_men} день - для мужчин')
    await message.answer(f'Ваша норма калорий {result_women} день - для женщин')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
