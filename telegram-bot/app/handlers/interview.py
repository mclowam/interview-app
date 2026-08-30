import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.clients.auth_client import AuthClient
from app.clients.interview_client import InterviewClient
from app.keyboards import LEVELS, POSITIONS, continue_keyboard, levels_keyboard, positions_keyboard
from app.states import InterviewFlow

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, auth_client: AuthClient) -> None:
    if message.from_user is None:
        return

    try:
        user = await auth_client.get_or_create(
            username=message.from_user.username or f"tg_{message.from_user.id}",
            tg_id=message.from_user.id,
        )
    except Exception:
        logger.exception("auth get_or_create failed")
        await message.answer("Не получилось войти. Попробуй /start ещё раз.")
        return

    await state.update_data(user_id=user["id"])
    await state.set_state(InterviewFlow.choosing_position)
    await message.answer(
        "Привет! Выбери позицию, к которой готовишься:",
        reply_markup=positions_keyboard(),
    )


@router.callback_query(InterviewFlow.choosing_position, F.data.startswith("position:"))
async def choose_position(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data is None or callback.message is None:
        await callback.answer()
        return

    position_key = callback.data.removeprefix("position:")
    position = POSITIONS.get(position_key, position_key)
    await state.update_data(position=position)
    await state.set_state(InterviewFlow.choosing_level)
    await callback.message.edit_text("Теперь выбери уровень:", reply_markup=levels_keyboard())
    await callback.answer()


@router.callback_query(InterviewFlow.choosing_level, F.data.startswith("level:"))
async def choose_level(
    callback: CallbackQuery, state: FSMContext, interview_client: InterviewClient
) -> None:
    await callback.answer()
    if callback.data is None or callback.message is None:
        return

    level, _label = LEVELS[callback.data.removeprefix("level:")]
    data = await state.get_data()

    try:
        interview = await interview_client.create_interview(
            user_id=data["user_id"], position=data["position"], level=level
        )
    except Exception:
        logger.exception("create_interview failed")
        await callback.message.answer("Не получилось создать собеседование. Попробуй /start.")
        return

    await state.update_data(interview_id=interview["id"])
    await callback.message.edit_text("Начинаем, генерирую вопрос...")
    await ask_next_question(callback.message, state, interview_client)


async def ask_next_question(
    message: Message, state: FSMContext, interview_client: InterviewClient
) -> bool:
    data = await state.get_data()
    try:
        turn = await interview_client.create_turn(data["interview_id"])
    except Exception:
        logger.exception("create_turn failed")
        await message.answer("Не получилось сгенерировать вопрос, попробуй ещё раз.")
        return False

    await state.update_data(turn_id=turn["id"])
    await state.set_state(InterviewFlow.waiting_answer)
    await message.answer(turn["question"])
    return True


@router.message(InterviewFlow.waiting_answer, F.text)
async def receive_answer(
    message: Message, state: FSMContext, interview_client: InterviewClient
) -> None:
    if not message.text:
        return

    data = await state.get_data()
    try:
        turn = await interview_client.submit_answer(data["turn_id"], message.text)
    except Exception:
        logger.exception("submit_answer failed")
        await message.answer("Не получилось оценить ответ, попробуй отправить его ещё раз.")
        return

    await state.set_state(InterviewFlow.choosing_next)
    await message.answer(
        f"Оценка: {turn['score']}/10\n{turn['feedback']}",
        reply_markup=continue_keyboard(),
    )


@router.callback_query(InterviewFlow.choosing_next, F.data == "continue")
async def continue_interview(
    callback: CallbackQuery, state: FSMContext, interview_client: InterviewClient
) -> None:
    await callback.answer()
    if callback.message is None:
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    ok = await ask_next_question(callback.message, state, interview_client)
    if not ok:
        await state.set_state(InterviewFlow.choosing_next)
        await callback.message.answer(
            "Можно повторить или закончить.",
            reply_markup=continue_keyboard(),
        )


@router.callback_query(InterviewFlow.choosing_next, F.data == "finish")
async def finish_interview(
    callback: CallbackQuery, state: FSMContext, interview_client: InterviewClient
) -> None:
    await callback.answer()
    if callback.message is None:
        return

    data = await state.get_data()
    try:
        await interview_client.finish_interview(data["interview_id"])
        turns = await interview_client.list_turns(data["interview_id"])
    except Exception:
        logger.exception("finish_interview failed")
        await callback.message.answer("Не получилось завершить собеседование, попробуй ещё раз.")
        return

    scored = [t["score"] for t in turns if t.get("score") is not None]
    average = sum(scored) / len(scored) if scored else 0

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Собес завершён. Вопросов: {len(turns)}, средняя оценка: {average:.1f}/10"
    )
    await state.clear()
