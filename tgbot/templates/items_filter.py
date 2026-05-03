import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import Game, GameCategory
from playerokapi.enums import ItemStatuses

from .. import callback_datas as calls


def items_filter_kb(filter, last_page=0):
    st1 = "・" if ItemStatuses.PENDING_APPROVAL in filter["statuses"] else ""
    st2 = "・" if ItemStatuses.PENDING_MODERATION in filter["statuses"] else ""
    st3 = "・" if ItemStatuses.APPROVED in filter["statuses"] else ""
    st4 = "・" if ItemStatuses.DECLINED in filter["statuses"] else ""
    st5 = "・" if ItemStatuses.BLOCKED in filter["statuses"] else ""
    st6 = "・" if ItemStatuses.EXPIRED in filter["statuses"] else ""
    st7 = "・" if ItemStatuses.SOLD in filter["statuses"] else ""
    st8 = "・" if ItemStatuses.DRAFT in filter["statuses"] else ""
    st9 = "・" if filter["statuses"] == [] else ""

    game = filter["game_name"] if filter["game_name"] else "🎮 Выбрать"
    ga1 = "・" if len(filter["game_id"] or "") > 0 else ""
    ga2 = "・" if filter["game_id"] == None else ""

    cat = filter["category_name"] if filter["category_name"] else "📂 Выбрать" if ga1 else "❌ Выберите игру"
    ca1 = "・" if len(filter["category_id"] or "") > 0 else ""
    ca2 = "・" if filter["category_id"] == None else ""

    rows = [
        [InlineKeyboardButton(text="━━━  СТАТУСЫ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{st1} Ожидает принятия {st1}", callback_data=calls.ChangeItemsFilter(st=1).pack()), 
        InlineKeyboardButton(text=f"{st2} На модерации {st2}", callback_data=calls.ChangeItemsFilter(st=2).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{st3} Активен {st3}", callback_data=calls.ChangeItemsFilter(st=3).pack()), 
        InlineKeyboardButton(text=f"{st4} Отклонён {st4}", callback_data=calls.ChangeItemsFilter(st=4).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{st5} Заблокирован {st5}", callback_data=calls.ChangeItemsFilter(st=5).pack()), 
        InlineKeyboardButton(text=f"{st6} Истёкший {st6}", callback_data=calls.ChangeItemsFilter(st=6).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{st7} Продан {st7}", callback_data=calls.ChangeItemsFilter(st=7).pack()), 
        InlineKeyboardButton(text=f"{st8} Черновик {st8}", callback_data=calls.ChangeItemsFilter(st=8).pack()),
        ],
        [InlineKeyboardButton(text=f"{st9} Все {st9}", callback_data=calls.ChangeItemsFilter(st=9).pack())],
        [InlineKeyboardButton(text="━━━  ИГРА  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{ga1} {game} {ga1}", callback_data="enter_items_filter_game_name"), 
        InlineKeyboardButton(text=f"{ga2} Любая {ga2}", callback_data=calls.ChangeItemsFilter(ga_id="all").pack()),
        ],
        [InlineKeyboardButton(text="━━━  КАТЕГОРИЯ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{ca1} {cat} {ca1}", callback_data="sel_items_filter_category"), 
        InlineKeyboardButton(text=f"{ca2} Любая {ca2}", callback_data=calls.ChangeItemsFilter(ca_id="all").pack()),
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ItemsPagination(page=last_page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def items_filter_games_kb(games: list[Game], page=0):
    rows = []
    items_per_page = 24
    items_per_row = 2
    
    total_pages = math.ceil(len(games) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for game in list(games)[start_offset:end_offset]:
        dynamic_btns.append(InlineKeyboardButton(
            text=game.name, 
            callback_data=calls.ChangeItemsFilter(ga_id=game.id).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ItemsPagination(page=page).pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def items_filter_categories_kb(cats: list[GameCategory], page=0):
    rows = []
    items_per_page = 24
    items_per_row = 2
    
    total_pages = math.ceil(len(cats) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for cat in list(cats)[start_offset:end_offset]:
        dynamic_btns.append(InlineKeyboardButton(
            text=cat.name, 
            callback_data=calls.ChangeItemsFilter(ca_id=cat.id).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ItemsPagination(page=page).pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb