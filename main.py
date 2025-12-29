import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import handlers
from bot import bot

from typing import NoReturn

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


async def main() -> None:
    """
    Основная функция запуска бота
    """
    try:
        # Отправляем сообщение о запуске бота
        try:
            await bot.send_message(1012882762, 'Бот запущен!!!')
        except:
            pass

        logger.info("Инициализация таблиц базы данных завершена")

        # Создание диспетчера для обработки событий с хранилищем состояний
        storage = MemoryStorage()
        dp: Dispatcher = Dispatcher(storage=storage)

        # Регистрация роутеров
        dp.include_router(handlers.router)
        logger.info("Роутеры успешно зарегистрированы")

        # Удаление вебхука для очистки ожидающих обновлений
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Ожидающие обновления очищены")

        # Запуск бота в режиме long-polling
        logger.info("Запуск бота в режиме long-polling...")
        await dp.start_polling(bot)


    except Exception as e:
        logger.exception(f"Критическая ошибка: {str(e)}")
        raise


def run_app() -> NoReturn:
    """
    Точка входа для запуска приложения
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Работа бота принудительно завершена пользователем")
    finally:
        logger.info("Приложение завершило работу")


# Точка входа при запуске скрипта
if __name__ == '__main__':
    run_app()
