import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging

TOKEN = "7708977377:AAEy06Al4HcL2S8LNMg3rftgtMc8yLg5zck"
MANAGER_ID = "6315067806"  # ID менеджера, куди будуть приходити замовлення

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Стан для збереження даних замовлення
class OrderState(StatesGroup):
    full_name = State()
    phone = State()
    city = State()
    post_office = State()

# Головне меню
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛒 Оформити замовлення", callback_data="order")],
    [InlineKeyboardButton(text="💬 Задати питання", url=f"https://t.me/manager_smartonline")]
])

# Відповідь на старт
@dp.message(Command("start"))
async def start(message: types.Message):
    text = (
        "🔥 **Вітаю! Дякуємо, що перейшли за посиланням.** 🔥\n\n"
        "🧼 **Пароочисник**\n\n"
        "🌍 Виробник: Польща\n"
        "🛡 Гарантія: 12 місяців\n"
        "💰 **Ціна: 1699 грн**\n\n"
        "📌 **Технічні характеристики:**\n"
        "✅ Виробництво пари: до 44 г/хв\n"
        "✅ Температура пари: до 120 °C\n"
        "✅ Робочий тиск: 3.5 бара\n"
        "✅ Потужність: 2000 Вт (номінальна 1200 Вт)\n"
        "✅ Місткість бака: 450 мл\n"
        "✅ Довжина шнура: 2.78 м\n"
        "✅ Розміри: 31 x 14.5 x 22.2 см\n\n"
        "🎯 **Ідеально підходить для прибирання:**\n"
        "✔️ Підлога та настінна плитка\n"
        "✔️ Вікна\n"
        "✔️ Текстильні меблі\n"
        "✔️ Пластикові меблі\n"
        "✔️ Матраци (знищує до 80% кліщів)\n\n"
        "📦 **Комплектація:**\n"
        "🔹 Металева щітка\n"
        "🔹 Нейлонова щітка\n"
        "🔹 Гнучкий шланг\n"
        "🔹 3x подовжувачі (33 см)\n"
        "🔹 Велика насадка, плоский пензель\n"
        "🔹 Щітка для підлоги + тканини для прибирання\n\n"
        "👉 Оберіть опцію нижче:"
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

# Обробка натискання "Оформити замовлення"
@dp.callback_query(lambda c: c.data == "order")
async def process_order(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("✍️ Введіть ваше **прізвище та ім'я**:")
    await state.set_state(OrderState.full_name)

# Отримання прізвища та імені
@dp.message(StateFilter(OrderState.full_name))
async def get_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📞 Введіть ваш **номер телефону**:")
    await state.set_state(OrderState.phone)

# Отримання номера телефону
@dp.message(StateFilter(OrderState.phone))
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏙 Введіть ваше **місто**:")
    await state.set_state(OrderState.city)

# Отримання міста
@dp.message(StateFilter(OrderState.city))
async def get_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("📦 Введіть номер **відділення Нової Пошти**:")
    await state.set_state(OrderState.post_office)

# Отримання відділення Нової Пошти та надсилання замовлення менеджеру
@dp.message(StateFilter(OrderState.post_office))
async def get_post_office(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    order_text = (
        "🛍 **Нове замовлення!**\n\n"
        f"👤 **Ім'я та прізвище:** {user_data['full_name']}\n"
        f"📞 **Телефон:** {user_data['phone']}\n"
        f"🏙 **Місто:** {user_data['city']}\n"
        f"📦 **Відділення Нової Пошти:** {message.text}\n\n"
        "📌 **Товар:** Пароочисник Adler AD 7038\n"
        "💰 **Ціна:** 1699 грн\n\n"
        "🔔 Будь ласка, обробіть це замовлення!"
    )

    # Надсилання замовлення менеджеру
    await bot.send_message(MANAGER_ID, order_text, parse_mode="Markdown")

    await message.answer("✅ Ваше замовлення прийняте! Менеджер скоро зв'яжеться з вами.")
    await state.clear()

# Головна асинхронна функція
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
