from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message
from ..callback_handlers.pagination import PAGES


router = Router()


@router.message(states.PageStates.waiting_for_page, F.text)
async def handler_waiting_for_page(message: types.Message, state: FSMContext):
    data = await state.get_data()
    enter = data.get("page_enter")
    render, float_text = PAGES[enter["to"]]
    try:
        await state.set_state(enter["state"])

        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")

        page = max(int(message.text.strip()), 1) - 1
        if enter["total"]:
            page = min(page, enter["total"] - 1)
        await render(message, state, page)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=float_text(e),
            reply_markup=templ.back_kb(calls.PageBack(to=enter["to"], page=enter["page"]).pack())
        )
