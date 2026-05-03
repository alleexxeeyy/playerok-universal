import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import Game, GameCategory
from playerokapi.enums import ReviewStatuses

from .. import callback_datas as calls


def reviews_filter_kb(filter, last_page=0):
    st1 = "・" if filter["status"] == ReviewStatuses.APPROVED else ""
    st2 = "・" if filter["status"] == ReviewStatuses.DELETED else ""
    st3 = "・" if filter["status"] == None else ""
    
    cr = "❌" if filter["comment_required"] else "✅"
    rt = f"{filter['rating']} ⭐" if filter["rating"] != None else "Любая"
    rt_val = ((filter["rating"] or 0) + 1) if (filter["rating"] or 0) < 5 else 0

    game = filter["game_name"] if filter["game_name"] else "🎮 Выбрать"
    ga1 = "・" if len(filter["game_id"] or "") > 0 else ""
    ga2 = "・" if filter["game_id"] == None else ""

    cat = filter["category_name"] if filter["category_name"] else "📂 Выбрать" if ga1 else "❌ Выберите игру"
    ca1 = "・" if len(filter["category_id"] or "") > 0 else ""
    ca2 = "・" if filter["category_id"] == None else ""
    
    min_sym = "・" if (filter["min_item_price"] or 0) > 0 else ""
    min_pr = f"{filter['min_item_price']}₽" if (filter["min_item_price"] or 0) > 0 else "❌"
    max_sym = "・" if (filter["max_item_price"] or 0) > 0 else ""
    max_pr = f"{filter['max_item_price']}₽" if (filter["max_item_price"] or 0) > 0 else "❌"
    val = "・" if not any((filter["min_item_price"], filter["max_item_price"])) else ""

    rows = [
        [InlineKeyboardButton(text="━━━  СТАТУС  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{st1} Активный {st1}", callback_data=calls.ChangeReviewsFilter(st=1).pack()), 
        InlineKeyboardButton(text=f"{st2} Удалённый {st2}", callback_data=calls.ChangeReviewsFilter(st=2).pack()),
        ],
        [InlineKeyboardButton(text=f"{st3} Любой {st3}", callback_data=calls.ChangeReviewsFilter(st=3).pack())],
        [InlineKeyboardButton(text="━━━  СОДЕРЖИМОЕ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"Текст обязателен: {cr}", callback_data=calls.ChangeReviewsFilter(cr=1).pack()),
        InlineKeyboardButton(text=f"Оценка: {rt}", callback_data=calls.ChangeReviewsFilter(rt=rt_val).pack())
        ],
        [InlineKeyboardButton(text="━━━  ИГРА  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{ga1} {game} {ga1}", callback_data="enter_reviews_filter_game_name"), 
        InlineKeyboardButton(text=f"{ga2} Любая {ga2}", callback_data=calls.ChangeReviewsFilter(ga_id="all").pack()),
        ],
        [InlineKeyboardButton(text="━━━  КАТЕГОРИЯ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{ca1} {cat} {ca1}", callback_data="sel_reviews_filter_category"), 
        InlineKeyboardButton(text=f"{ca2} Любая {ca2}", callback_data=calls.ChangeReviewsFilter(ca_id="all").pack()),
        ],
        [InlineKeyboardButton(text="━━━  ЦЕНА ТОВАРА  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{min_sym} От: {min_pr} {min_sym}", callback_data="enter_reviews_filter_min_item_price"), 
        InlineKeyboardButton(text=f"{max_sym} До: {max_pr} {max_sym}", callback_data="enter_reviews_filter_max_item_price"), 
        ],
        [InlineKeyboardButton(text=f"{val} Любая {val}", callback_data=calls.ChangeReviewsFilter(min_pr=0, max_pr=0).pack())],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ReviewsPagination(page=last_page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def reviews_filter_games_kb(games: list[Game], page=0):
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
            callback_data=calls.ChangeReviewsFilter(ga_id=game.id).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ReviewsPagination(page=page).pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def reviews_filter_categories_kb(cats: list[GameCategory], page=0):
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
            callback_data=calls.ChangeReviewsFilter(ca_id=cat.id).pack())
        )
    for i in range(0, len(dynamic_btns), items_per_row):
        rows.append(dynamic_btns[i:i+items_per_row])

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ReviewsPagination(page=page).pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb