from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CHANEL_LINK


def create_kb(width: int,
              *args: str,
              **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        pass
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def kb_button(button_text, button_url):
    button = InlineKeyboardButton(text=button_text, url=button_url)
    kb = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return kb


def subscribe_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📢 Подписаться на канал', url=CHANEL_LINK)],
        [InlineKeyboardButton(text='✅ Я подписался', callback_data='sub_check')]
    ])


def main_menu_kb():
    """Клавиатура главного меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='💰 Купля-продажа', callback_data='menu_buy_sell')],
        [InlineKeyboardButton(text='🔍 Подбор объекта', callback_data='menu_selection')],
        [InlineKeyboardButton(text='🏗️ Новостройки', callback_data='menu_new_buildings')],
        [InlineKeyboardButton(text='👴 Сделка 60+', callback_data='menu_deal_60')],
        [InlineKeyboardButton(text='🤝 Помощь / сопровождение', callback_data='menu_assistance')],
        [InlineKeyboardButton(text='💬 Консультация', callback_data='menu_consultation')],
        [InlineKeyboardButton(text='❔ Другое', callback_data='menu_other')]
    ])


def request_action_kb():
    """Клавиатура действий после выбора пункта меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📝 Оставить заявку', callback_data='action_request')],
        [InlineKeyboardButton(text='❓ Задать вопрос', callback_data='action_question')],
        [InlineKeyboardButton(text='⬅️ Назад в меню', callback_data='action_back')]
    ])


def contact_type_kb():
    """Клавиатура выбора типа контакта"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📞 Телефон', callback_data='contact_phone')],
        [InlineKeyboardButton(text='✈️ Telegram', callback_data='contact_telegram')]
    ])


def confirm_kb():
    """Клавиатура подтверждения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📤 Отправить', callback_data='confirm_send')],
        [InlineKeyboardButton(text='🏠 В главное меню', callback_data='confirm_to_menu')]
    ])