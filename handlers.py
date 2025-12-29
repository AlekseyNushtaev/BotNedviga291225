import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import CHANEL_ID, ADMIN_IDS
from keyboard import create_kb, subscribe_kb, main_menu_kb, request_action_kb, contact_type_kb, confirm_kb
import logging

router = Router()
logger = logging.getLogger(__name__)


# Определяем состояния
class Form(StatesGroup):
    menu_option = State()
    waiting_for_question = State()
    waiting_for_contact_type = State()
    waiting_for_phone = State()
    waiting_for_username = State()
    waiting_for_confirmation = State()


@router.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды /start"""
    try:
        full_name = message.from_user.full_name if message.from_user.full_name else ""
        greeting = f"👋 Привет, {full_name}!\n\n📢 Чтобы продолжить, подпишитесь на наш канал."

        # Отправляем сообщение с клавиатурой
        await message.answer(
            greeting,
            reply_markup=subscribe_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка в start_handler: {e}")
        await message.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")


@router.callback_query(F.data == "sub_check")
async def check_subscription_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Я подписался' - проверка подписки"""
    try:
        user_id = callback.from_user.id

        # Отправляем уведомление о проверке
        await callback.answer("🔍 Проверяем подписку...")
        await asyncio.sleep(2)

        # Проверяем подписку пользователя
        try:
            # Получаем информацию о пользователе в канале
            member = await callback.bot.get_chat_member(
                chat_id=CHANEL_ID,
                user_id=user_id
            )

            # Проверяем статус пользователя
            if member.status in ["member", "administrator", "creator"]:
                # Редактируем сообщение на "Главное меню"
                try:
                    await callback.message.edit_text(
                        "📋 Выберите услугу:",
                        reply_markup=main_menu_kb()
                    )
                except:
                    await callback.message.answer(
                        "📋 Выберите услугу:",
                        reply_markup=main_menu_kb()
                    )
            else:
                # Пользователь не подписан
                try:
                    await callback.message.edit_text(
                        "❌ Вижу, подписки нет. Подпишитесь и нажмите 'Я подписался'.",
                        reply_markup=subscribe_kb()
                    )
                except:
                    await callback.message.answer(
                        "❌ Вижу, подписки нет. Подпишитесь и нажмите 'Я подписался'.",
                        reply_markup=subscribe_kb()
                    )

        except Exception as channel_error:
            logger.error(f"Ошибка при проверке подписки: {channel_error}")
            await callback.message.edit_text(
                "⚠️ Произошла ошибка при проверке подписки. Пожалуйста, попробуйте позже.",
                reply_markup=create_kb(2,
                                       sub_check="✅ Я подписался",
                                       subscribe="📢 Подписаться на канал")
            )

    except Exception as e:
        logger.error(f"Ошибка в check_subscription_handler: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)


@router.message(F.text == "Главное меню")
async def menu_handler(message: Message, state: FSMContext):
    """Обработчик главного меню"""
    await state.clear()
    await message.answer("📋 Выберите услугу:", reply_markup=main_menu_kb())


# Обработчики для кнопок главного меню
@router.callback_query(F.data.startswith("menu_"))
async def menu_option_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора пункта меню"""
    menu_options = {
        "menu_buy_sell": "💰 Купля-продажа",
        "menu_selection": "🔍 Подбор объекта",
        "menu_new_buildings": "🏗️ Новостройки",
        "menu_deal_60": "👴 Сделка 60+",
        "menu_assistance": "🤝 Помощь / сопровождение",
        "menu_consultation": "💬 Консультация",
        "menu_other": "❔ Другое"
    }

    option = callback.data
    option_text = menu_options.get(option, "❓ Неизвестный пункт")

    # Сохраняем выбранный пункт в состоянии
    await state.set_state(Form.menu_option)
    await state.update_data(selected_option=option_text)

    try:
        # Редактируем сообщение
        await callback.message.edit_text(
            f"📄 Заявка: {option_text}\n\n🎯 Выберите действие:",
            reply_markup=request_action_kb()
        )
    except:
        await callback.message.answer(
            f"📄 Заявка: {option_text}\n\n🎯 Выберите действие:",
            reply_markup=request_action_kb()
        )


@router.callback_query(F.data == "action_back")
async def back_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Назад в меню'"""
    # Сбрасываем состояние
    await state.clear()

    # Возвращаемся в главное меню
    try:
        await callback.message.edit_text(
            "📋 Выберите услугу:",
            reply_markup=main_menu_kb()
        )
    except:
        await callback.message.answer(
            "📋 Выберите услугу:",
            reply_markup=main_menu_kb()
        )


# Обработчик кнопки "Задать вопрос"
@router.callback_query(F.data == "action_question")
async def ask_question_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Задать вопрос'"""
    try:
        # Переходим в состояние ожидания вопроса
        await state.set_state(Form.waiting_for_question)

        try:
            # Редактируем сообщение
            await callback.message.edit_text(
                "❓ Напишите свой вопрос:"
            )
        except:
            await callback.message.answer(
                "❓ Напишите свой вопрос:"
            )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в ask_question_handler: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)


# Обработчик для получения вопроса от пользователя
@router.message(Form.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    """Обработчик получения вопроса"""
    try:
        # Сохраняем вопрос в состоянии
        await state.update_data(question=message.text)

        # Переходим к выбору типа контакта
        await state.set_state(Form.waiting_for_contact_type)
        await message.answer(
            "📇 Оставьте контактные данные:",
            reply_markup=contact_type_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_question: {e}")
        await message.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик кнопки "Оставить заявку"
@router.callback_query(F.data == "action_request")
async def leave_request_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Оставить заявку'"""
    try:
        # Устанавливаем пустой вопрос для заявки
        await state.update_data(question=None)

        # Переходим в состояние выбора типа контакта
        await state.set_state(Form.waiting_for_contact_type)

        try:
            # Редактируем сообщение
            await callback.message.edit_text(
                "📇 Оставьте контактные данные:",
                reply_markup=contact_type_kb()
            )
        except:
            await callback.message.answer(
                "📇 Оставьте контактные данные:",
                reply_markup=contact_type_kb()
            )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в leave_request_handler: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)


# Обработчик выбора типа контакта (Телефон)
@router.callback_query(F.data == "contact_phone")
async def phone_contact_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Телефон'"""
    try:
        # Переходим в состояние ожидания телефона
        await state.set_state(Form.waiting_for_phone)
        await state.update_data(contact_type="phone")

        try:
            # Редактируем сообщение
            await callback.message.edit_text(
                "📞 Напишите номер телефона:"
            )
        except:
            await callback.message.answer(
                "📞 Напишите номер телефона:"
            )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в phone_contact_handler: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)


# Обработчик выбора типа контакта (Telegram)
@router.callback_query(F.data == "contact_telegram")
async def telegram_contact_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Telegram'"""
    try:
        # Переходим в состояние ожидания username
        await state.set_state(Form.waiting_for_username)
        await state.update_data(contact_type="telegram")

        try:
            # Редактируем сообщение
            await callback.message.edit_text(
                "✈️ Напишите @username:"
            )
        except:
            await callback.message.answer(
                "✈️ Напишите @username:"
            )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в telegram_contact_handler: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)


# Обработчик для получения номера телефона
@router.message(Form.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработчик получения номера телефона"""
    try:
        # Сохраняем телефон в состоянии
        await state.update_data(contact_value=message.text)

        # Переходим к подтверждению
        await show_confirmation(message, state)
    except Exception as e:
        logger.error(f"Ошибка в process_phone: {e}")
        await message.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик для получения username
@router.message(Form.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    """Обработчик получения username"""
    try:
        # Сохраняем username в состоянии
        await state.update_data(contact_value=message.text)

        # Переходим к подтверждению
        await show_confirmation(message, state)
    except Exception as e:
        logger.error(f"Ошибка в process_username: {e}")
        await message.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")


# Функция для показа подтверждения
async def show_confirmation(message: Message, state: FSMContext):
    """Показать подтверждение данных"""
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        selected_option = data.get("selected_option", "неизвестно")
        question = data.get("question")
        contact_type = data.get("contact_type")
        contact_value = data.get("contact_value")

        # Формируем текст подтверждения
        confirmation_text = "🔍 Проверьте все данные и если все верно, нажмите кнопку Отправить:\n\n"

        # Определяем тип (Заявка или Вопрос)
        if question:
            confirmation_text += f"📝 Вопрос: {selected_option}\n"
            confirmation_text += f"📄 Текст вопроса: {question}\n"
        else:
            confirmation_text += f"📄 Заявка: {selected_option}\n"

        # Добавляем контактные данные
        if contact_type == "phone":
            confirmation_text += f"📞 Телефон: {contact_value}"
        else:
            confirmation_text += f"✈️ Username: {contact_value}"

        # Переходим в состояние подтверждения
        await state.set_state(Form.waiting_for_confirmation)

        # Отправляем сообщение с подтверждением
        await message.answer(
            confirmation_text,
            reply_markup=confirm_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка в show_confirmation: {e}")
        await message.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик кнопки "Отправить"
@router.callback_query(F.data == "confirm_send")
async def confirm_send_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Отправить'"""
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        selected_option = data.get("selected_option", "неизвестно")
        question = data.get("question")
        contact_type = data.get("contact_type")
        contact_value = data.get("contact_value")

        # Формируем сообщение для админов
        admin_message = "🆕 НОВАЯ ЗАЯВКА\n\n"

        if question:
            admin_message += f"📝 Вопрос: {selected_option}\n"
            admin_message += f"📄 Текст вопроса: {question}\n"
        else:
            admin_message += f"📄 Заявка: {selected_option}\n"

        if contact_type == "phone":
            admin_message += f"📞 Телефон: {contact_value}"
        else:
            admin_message += f"✈️ Username: {contact_value}"

        # Отправляем сообщение всем админам
        for admin_id in ADMIN_IDS:
            try:
                await callback.bot.send_message(admin_id, admin_message)
            except Exception as e:
                logger.error(f"Ошибка при отправке админу {admin_id}: {e}")

        # Отправляем подтверждение пользователю
        try:
            await callback.message.edit_text(
                "✅ Спасибо! Мы вернёмся с обратной связью в ближайшее время!"
            )
        except:
            await callback.answer("✅ Спасибо! Мы вернёмся с обратной связью в ближайшее время!")

        # Ждем немного и показываем главное меню
        await asyncio.sleep(1)

        # Сбрасываем состояние
        await state.clear()

        # Показываем главное меню
        await callback.message.answer(
            "📋 Выберите услугу:",
            reply_markup=main_menu_kb()
        )

        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в confirm_send_handler: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)


# Обработчик кнопки "В главное меню" из состояния подтверждения
@router.callback_query(F.data == "confirm_to_menu")
async def confirm_to_menu_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'В главное меню' из подтверждения"""
    try:
        # Сбрасываем состояние
        await state.clear()

        # Возвращаемся в главное меню
        try:
            await callback.message.edit_text(
                "📋 Выберите услугу:",
                reply_markup=main_menu_kb()
            )
        except:
            await callback.message.answer(
                "📋 Выберите услугу:",
                reply_markup=main_menu_kb()
            )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в confirm_to_menu_handler: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)
