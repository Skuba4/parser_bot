from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.exceptions import TelegramNetworkError

from services.base import download, FileTooLargeError
from utils.validators import link_checking
from utils.description import build_info

router = Router()


@router.message(lambda msg: msg.text and "https://" in msg.text)
async def link_handler(message: Message, state: FSMContext):
    if not await state.get_state():
        return

    if not link_checking(message.text):
        await message.answer("⚠️ Данный ресурс не поддерживается.")
        return

    try:
        dm = await message.answer("⏳ Скачиваю...")
        output_path, info = download(message.text)

        await message.answer_video(
            FSInputFile(output_path),
            supports_streaming=True,
            duration=int(info.get("duration", 0)),
            width=info.get("width", 0),
            height=info.get("height", 0),
        )

        await message.answer(
            build_info(info),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    except FileTooLargeError as e:
        await message.answer(str(e))

    except TelegramNetworkError as e:
        await message.answer("⚠️ Ошибка при отправке видео.")
        print(f"[TELEGRAM ERROR] {e}")

    except Exception as e:
        await message.answer("❌ Произошла ошибка при обработке ссылки.")
        print(f"[ERROR] {e}")

    finally:
        await dm.delete()


@router.message(F.text)
async def other_handler(message: Message, state: FSMContext):
    if await state.get_state():
        await message.answer("Моя-Твоя не понимать")
