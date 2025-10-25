from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()


class Status(StatesGroup):
    st = State()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    if not await state.get_state():
        await state.set_state(Status.st)
        await message.answer("✅")


@router.message(Command("stop"))
async def stop_handler(message: Message, state: FSMContext):
    if await state.get_state():
        await state.clear()
        await message.answer("❌")
