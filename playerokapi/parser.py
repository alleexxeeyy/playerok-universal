from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import *

from .enums import *


def file(data: dict) -> "FileObject":
    from .types import FileObject

    if not data:
        return None
    return FileObject(
        id=data.get("id"),
        url=data.get("url"),
        filename=data.get("filename"),
        mime=data.get("mime"),
    )


def sbp_bank_member(data: dict) -> "SBPBankMember":
    from .types import SBPBankMember

    if not data:
        return None
    return SBPBankMember(
        id=data.get("id"),
        name=data.get("name"),
        icon=data.get("icon")
    )


def transaction_payment_method(data: dict) -> "TransactionPaymentMethod":
    from .types import TransactionPaymentMethod

    if not data:
        return None
    return TransactionPaymentMethod(
        
    )


def transaction_payment_method(data: dict) -> "TransactionPaymentMethod":
    from .types import TransactionPaymentMethod
    from .parser import transaction_provider_props, transaction_provider_limits

    if not data:
        return None
    return TransactionPaymentMethod(
        id=TransactionPaymentMethodIds.__members__.get(data.get("id")),
        name=data.get("name"),
        fee=data.get("fee"),
        provider_id=TransactionProviderIds.__members__.get(data.get("provider_id")),
        account=account_profile(data.get("account")),
        props=transaction_provider_props(data.get("props")),
        limits=transaction_provider_limits(data.get("limits"))
    )


def transaction_provider_limit_range(data: dict) -> "TransactionProviderLimitRange":
    from .types import TransactionProviderLimitRange

    if not data:
        return None
    return TransactionProviderLimitRange(
        min=data.get("min"),
        max=data.get("max")
    )


def transaction_provider_limits(data: dict) -> "TransactionProviderLimits":
    from .types import TransactionProviderLimits

    if not data:
        return None
    return TransactionProviderLimits(
        incoming=transaction_provider_limit_range(data.get("incoming")),
        outgoing=transaction_provider_limit_range(data.get("outgoing"))
    )


def transaction_provider_required_user_data(data: dict) -> "TransactionProviderRequiredUserData":
    from .types import TransactionProviderRequiredUserData

    if not data:
        return None
    return TransactionProviderRequiredUserData(
        email=data.get("email"),
        phone_number=data.get("phoneNumber"),
        erip_account_number=data.get("eripAccountNumber")
    )


def transaction_provider_props(data: dict) -> "TransactionProviderProps":
    from .types import TransactionProviderProps

    if not data:
        return None
    return TransactionProviderProps(
        required_user_data=transaction_provider_required_user_data(data.get("requiredUserData")),
        tooltip=data.get("tooltip")
    )


def transaction_provider(data: dict) -> "TransactionProvider":
    from .types import TransactionProvider
    from .parser import account_profile

    if not data:
        return None
    return TransactionProvider(
        id=TransactionProviderIds.__members__.get(data.get("id")),
        name=data.get("name"),
        fee=data.get("fee"),
        min_fee_amount=data.get("minFeeAmount"),
        description=data.get("description"),
        account=account_profile(data.get("account")),
        props=transaction_provider_props(data.get("props")),
        limits=transaction_provider_limits(data.get("limits")),
        payment_methods=[transaction_payment_method(method) for method in data.get("paymentMethods")]
    )


def transaction(data: dict) -> "Transaction":
    from .types import Transaction

    if not data:
        return None
    return Transaction(
        id=data.get("id"),
        operation=TransactionOperations.__members__.get(data.get("operation")),
        direction=TransactionDirections.__members__.get(data.get("direction")),
        provider_id=TransactionProviderIds.__members__.get(data.get("providerId")),
        provider=transaction_provider(data.get("provider")),
        user=user_profile(data.get("user")),
        creator=user_profile(data.get("creator")),
        status=TransactionStatuses.__members__.get(data.get("status")),
        status_description=data.get("statusDescription"),
        status_expiration_date=data.get("statusExpirationDate"),
        value=data.get("value"),
        fee=data.get("fee"),
        created_at=data.get("createdAt"),
        verified_at=data.get("verified_at"),
        verified_by=data.get("verified_by"),
        completed_at=data.get("completed_at"),
        completed_by=data.get("completed_by"),
        payment_method_id=data.get("paymentMethodId"), 
        is_suspicious=data.get("is_suspicious"), 
        sbp_bank_name=data.get("spb_bank_name")
    )


def transaction_page_info(data: dict) -> "TransactionPageInfo":
    from .types import TransactionPageInfo

    if not data:
        return None
    return TransactionPageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage")
    )


def transaction_list(data: dict) -> "TransactionList":
    from .types import TransactionList

    if not data:
        return None
    return TransactionList(
        transactions=[transaction(edge.get("node")) for edge in data.get("edges")],
        page_info=transaction_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount")
    )


def user_bank_card(data: dict) -> "UserBankCard":
    from .types import UserBankCard

    if not data:
        return None
    return UserBankCard(
        id=data.get("id"),
        card_first_six=data.get("cardFirstSix"),
        card_last_four=data.get("cardLastFour"),
        card_type=BankCardTypes.__members__.get(data.get("cardType")),
        is_chosen=data.get("isChosen")
    )


def user_bank_card_page_info(data: dict) -> "UserBankCardPageInfo":
    from .types import UserBankCardPageInfo

    if not data:
        return None
    return UserBankCardPageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage")
    )


def user_bank_card_list(data: dict) -> "UserBankCardList":
    from .types import UserBankCardList

    if not data:
        return None
    return UserBankCardList(
        bank_cards=[user_bank_card(edge.get("node")) for edge in data.get("edges")],
        page_info=user_bank_card_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount")
    )


def game_category_data_field(data: dict) -> "GameCategoryDataField":
    from .types import GameCategoryDataField

    if not data:
        return None
    return GameCategoryDataField(
        id=data.get("id"),
        label=data.get("label"),
        type=GameCategoryDataFieldTypes.__members__.get(data.get("type")),
        input_type=GameCategoryDataFieldInputTypes.__members__.get(
            data.get("inputType")
        ),
        copyable=data.get("copyable"),
        hidden=data.get("hidden"),
        required=data.get("required"),
        value=data.get("value"),
    )


def game_category_data_field_page_info(data: dict) -> "GameCategoryDataFieldPageInfo":
    from .types import GameCategoryDataFieldPageInfo

    if not data:
        return None
    return GameCategoryDataFieldPageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def game_category_data_field_list(data: dict) -> "GameCategoryDataFieldList":
    from .types import GameCategoryDataFieldList

    if not data:
        return None
    data_fields = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            data_fields.append(game_category_data_field(edge.get("node")))
    return GameCategoryDataFieldList(
        data_fields=data_fields,
        page_info=game_category_data_field_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def game_category_props(data: dict) -> "GameCategoryProps":
    from .types import GameCategoryProps

    if not data:
        return None
    return GameCategoryProps(
        min_reviews=data.get("minTestimonials"),
        min_reviews_for_seller=data.get("minTestimonialsForSeller"),
    )


def game_category_option(data: dict) -> "GameCategoryOption":
    from .types import GameCategoryOption

    if not data:
        return None
    return GameCategoryOption(
        id=data.get("id"),
        group=data.get("group"),
        label=data.get("label"),
        type=GameCategoryOptionTypes.__members__.get(data.get("type")),
        field=data.get("field"),
        value=data.get("value"),
        value_range_limit=data.get("valueRangeLimit"),
    )


def game_category_agreement(data: dict) -> "GameCategoryAgreement":
    from .types import GameCategoryAgreement

    if not data:
        return None
    return GameCategoryAgreement(
        id=data.get("id"),
        description=data.get("description"),
        icontype=GameCategoryAgreementIconTypes.__members__.get(data.get("iconType")),
        sequence=data.get("sequence"),
    )


def game_category_agreement_page_info(data: dict) -> "GameCategoryAgreementPageInfo":
    from .types import GameCategoryAgreementPageInfo

    if not data:
        return None
    return GameCategoryAgreementPageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def game_category_agreement_list(data: dict) -> "GameCategoryAgreementList":
    from .types import GameCategoryAgreementList

    if not data:
        return None
    agreements = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            agreements.append(game_category_agreement(edge.get("node")))
    return GameCategoryAgreementList(
        agreements=agreements,
        page_info=game_category_agreement_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def game_category_obtaining_type(data: dict) -> "GameCategoryObtainingType":
    from .types import GameCategoryObtainingType

    if not data:
        return None
    agrs = []
    data_agrs = data.get("agreements")
    if data_agrs:
        for agr in data_agrs:
            agrs.append(game_category_agreement(agr))
    return GameCategoryObtainingType(
        id=data.get("id"),
        name=data.get("name"),
        description=data.get("description"),
        game_category_id=data.get("gameCategoryId"),
        no_comment_from_buyer=data.get("noCommentFromBuyer"),
        instruction_for_buyer=data.get("instructionForBuyer"),
        instruction_for_seller=data.get("instructionForSeller"),
        sequence=data.get("sequence"),
        fee_multiplier=data.get("feeMultiplier"),
        agreements=agrs,
        props=game_category_props(data.get("props")),
    )


def game_category_obtaining_type_page_info(
    data: dict,
) -> "GameCategoryObtainingTypePageInfo":
    from .types import GameCategoryObtainingTypePageInfo

    if not data:
        return None
    return GameCategoryObtainingTypePageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def game_category_obtaining_type_list(data: dict) -> "GameCategoryObtainingTypeList":
    from .types import GameCategoryObtainingTypeList

    if not data:
        return None
    types = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            types.append(game_category_obtaining_type(edge.get("node")))
    return GameCategoryObtainingTypeList(
        obtaining_types=types,
        page_info=game_category_obtaining_type_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def game_category_instruction(data: dict) -> "GameCategoryInstruction":
    from .types import GameCategoryInstruction

    if not data:
        return None
    return GameCategoryInstruction(id=data.get("id"), text=data.get("text"))


def game_category_instruction_page_info(
    data: dict,
) -> "GameCategoryInstructionPageInfo":
    from .types import GameCategoryInstructionPageInfo

    if not data:
        return None
    return GameCategoryInstructionPageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def game_category_instruction_list(data: dict) -> "GameCategoryInstructionList":
    from .types import GameCategoryInstructionList

    if not data:
        return None
    instructions = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            instructions.append(game_category_instruction(edge.get("node")))
    return GameCategoryInstructionList(
        instructions=instructions,
        page_info=game_category_instruction_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def game_category(data: dict) -> "GameCategory":
    from .types import GameCategory

    if not data:
        return None
    options = []
    data_options = data.get("options")
    if data_options:
        for option in data_options:
            options.append(game_category_option(option))
    agrs = []
    data_agrs = data.get("agreements")
    if data_agrs:
        for agr in data_agrs:
            agrs.append(game_category_agreement(agr))
    return GameCategory(
        id=data.get("id"),
        slug=data.get("slug"),
        name=data.get("name"),
        category_id=data.get("categoryId"),
        game_id=data.get("gameId"),
        obtaining=data.get("obtaining"),
        options=options,
        props=game_category_props(data.get("props")),
        no_comment_from_buyer=data.get("noCommentFromBuyer"),
        instruction_for_buyer=data.get("instructionForBuyer"),
        instruction_for_seller=data.get("instructionForSeller"),
        use_custom_obtaining=data.get("useCustomObtaining"),
        auto_confirm_period=GameCategoryAutoConfirmPeriods.__members__.get(
            data.get("autoConfirmPeriod")
        ),
        auto_moderation_mode=data.get("autoModerationMode"),
        agreements=agrs,
        fee_multiplier=data.get("feeMultiplier"),
    )


def game(data: dict) -> "Game":
    from .types import Game

    if not data:
        return None
    cats = []
    data_cats = data.get("categories")
    if data_cats:
        for cat in data_cats:
            cats.append(game_category(cat))
    return Game(
        id=data.get("id"),
        slug=data.get("slug"),
        name=data.get("name"),
        type=GameTypes.__members__.get(data.get("type")),
        logo=file(data.get("logo")),
        banner=file(data.get("banner")),
        categories=cats,
        created_at=data.get("createdAt"),
    )


def game_profile(data: dict) -> "GameProfile":
    from .types import GameProfile

    if not data:
        return None
    return GameProfile(
        id=data.get("id"),
        slug=data.get("slug"),
        name=data.get("name"),
        type=GameTypes.__members__.get(data.get("type")),
        logo=file(data.get("logo")),
    )


def game_page_info(data: dict) -> "GamePageInfo":
    from .types import GamePageInfo

    if not data:
        return None
    return GamePageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def game_list(data: dict) -> "GameList":
    from .types import GameList

    if not data:
        return None
    games = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            games.append(game(edge.get("node")))
    return GameList(
        games=games,
        page_info=game_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def user_profile(data: dict) -> "UserProfile":
    from .types import UserProfile

    if not data:
        return None
    u = UserProfile(
        id=data.get("id"),
        username=data.get("username"),
        role=UserTypes.__members__.get(data.get("role")),
        avatar_url=data.get("avatarURL"),
        is_online=data.get("isOnline"),
        is_blocked=data.get("isBlocked"),
        rating=data.get("rating"),
        reviews_count=data.get("testimonialCounter"),
        created_at=data.get("createdAt"),
        support_chat_id=data.get("supportChatId"),
        system_chat_id=data.get("systemChatId"),
    )
    return u


def account_items_stats(data: dict) -> "AccountItemsStats":
    from .types import AccountItemsStats

    if not data:
        return None
    return AccountItemsStats(total=data.get("total"), finished=data.get("finished"))


def account_incoming_deals_stats(data: dict) -> "AccountIncomingDealsStats":
    from .types import AccountIncomingDealsStats

    if not data:
        return None
    return AccountIncomingDealsStats(
        total=data.get("total"), finished=data.get("finished")
    )


def account_outgoing_deals_stats(data: dict) -> "AccountOutgoingDealsStats":
    from .types import AccountOutgoingDealsStats

    if not data:
        return None
    return AccountOutgoingDealsStats(
        total=data.get("total"), finished=data.get("finished")
    )


def account_deals_stats(data: dict) -> "AccountDealsStats":
    from .types import AccountDealsStats

    if not data:
        return None
    return AccountDealsStats(
        incoming=account_incoming_deals_stats(data.get("incoming")),
        outgoing=account_outgoing_deals_stats(data.get("outgoing")),
    )


def account_stats(data: dict) -> "AccountStats":
    from .types import AccountStats

    if not data:
        return None
    items = account_items_stats(data.get("items"))
    deals = account_deals_stats(data.get("deals"))
    return AccountStats(items=items, deals=deals)


def account_balance(data: dict) -> "AccountBalance":
    from .types import AccountBalance

    if not data:
        return None
    return AccountBalance(
        id=data.get("id"),
        value=data.get("value"),
        frozen=data.get("frozen"),
        available=data.get("available"),
        withdrawable=data.get("withdrawable"),
        pending_income=data.get("pendingIncome"),
    )


def account_profile(data: dict) -> "AccountProfile":
    from .types import AccountProfile

    if not data:
        return None
    profile: dict = data.get("profile", {})
    return AccountProfile(
        id=data.get("id"),
        username=profile.get("username"),
        email=data.get("email"),
        balance=account_balance(data.get("balance")),
        stats=account_stats(data.get("stats")),
        role=UserTypes.__members__.get(data.get("role")),
        avatar_url=profile.get("avatarURL"),
        is_online=profile.get("isOnline"),
        is_blocked=data.get("isBlocked"),
        is_blocked_for=data.get("isBlockedFor"),
        is_verified=data.get("isVerified"),
        rating=profile.get("rating"),
        reviews_count=profile.get("testimonialCounter"),
        created_at=profile.get("createdAt"),
        support_chat_id=profile.get("supportChatId"),
        system_chat_id=profile.get("systemChatId"),
        has_frozen_balance=data.get("hasFrozenBalance"),
        has_enabled_notifications=data.get("hasEnabledNotifications"),
    )


def item_priority_status_price_range(data: dict) -> "ItemPriorityStatusPriceRange":
    from .types import ItemPriorityStatusPriceRange

    if not data:
        return None
    return ItemPriorityStatusPriceRange(min=data.get("min"), max=data.get("max"))


def item_priority_status(data: dict) -> "ItemPriorityStatus":
    from .types import ItemPriorityStatus

    if not data:
        return None
    return ItemPriorityStatus(
        id=data.get("id"),
        price=data.get("price"),
        name=data.get("name"),
        type=PriorityTypes.__members__.get(data.get("type")),
        period=data.get("period"),
        price_range=item_priority_status_price_range(data.get("priceRange")),
    )


def item_log(data: dict) -> "ItemLog":
    from .types import ItemLog

    if not data:
        return None
    return ItemLog(
        id=data.get("id"),
        event=ItemLogEvents.__members__.get(data.get("event")),
        created_at=data.get("createdAt"),
        user=user_profile(data.get("user")),
    )


def item(data: dict) -> "Item":
    from .types import Item

    if not data:
        return None
    attachments = []
    data_attachments = data.get("attachments")
    if data_attachments:
        for att in data_attachments:
            attachments.append(file(att))
    data_fields = []
    data_data_fields = data.get("dataFields")
    if data_data_fields:
        for field in data_data_fields:
            data_fields.append(game_category_data_field(field))
    return Item(
        id=data.get("id"),
        slug=data.get("slug"),
        name=data.get("name"),
        description=data.get("description"),
        obtaining_type=game_category_obtaining_type(data.get("obtainingType")),
        price=data.get("price"),
        raw_price=data.get("rawPrice"),
        priority_position=data.get("priorityPosition"),
        attachments=attachments,
        attributes=data.get("attributes"),
        category=game_category(data.get("category")),
        comment=data.get("comment"),
        data_fields=data_fields,
        fee_multiplier=data.get("feeMultiplier"),
        game=game_profile(data.get("game")),
        seller_type=data.get("sellerType"),
        status=ItemStatuses.__members__.get(data.get("status")),
        user=user_profile(data.get("user")),
    )


def my_item(data: dict) -> "MyItem":
    from .types import MyItem

    if not data:
        return None
    attachments = []
    data_attachments = data.get("attachments")
    if data_attachments:
        for att in data_attachments:
            attachments.append(file(att))
    data_fields = []
    data_data_fields = data.get("dataFields")
    if data_data_fields:
        for field in data_data_fields:
            data_fields.append(game_category_data_field(field))

    return MyItem(
        id=data.get("id"),
        slug=data.get("slug"),
        name=data.get("name"),
        description=data.get("description"),
        obtaining_type=game_category_obtaining_type(data.get("obtainingType")),
        price=data.get("price"),
        prev_price=data.get("prevPrice"),
        raw_price=data.get("rawPrice"),
        priority_position=data.get("priorityPosition"),
        attachments=attachments,
        attributes=data.get("attributes"),
        buyer=user_profile(data.get("buyer")),
        category=game_category(data.get("category")),
        comment=data.get("comment"),
        data_fields=data_fields,
        fee_multiplier=data.get("feeMultiplier"),
        prev_fee_multiplier=data.get("prevFeeMultiplier"),
        seller_notified_about_fee_change=data.get("sellerNotifiedAboutFeeChange"),
        game=game_profile(data.get("game")),
        seller_type=data.get("sellerType"),
        status=ItemStatuses.__members__.get(data.get("status")),
        user=user_profile(data.get("user")),
        priority=PriorityTypes.__members__.get(data.get("priority")),
        priority_price=data.get("priorityPrice"),
        status_expiration_date=data.get("statusExpirationDate"),
        status_description=data.get("statusDescription"),
        status_payment=transaction(data.get("statusPayment")),
        views_counter=data.get("viewsCounter"),
        is_editable=data.get("isEditable"),
        approval_date=data.get("approvalDate"),
        deleted_at=data.get("deletedAt"),
        updated_at=data.get("updatedAt"),
        created_at=data.get("createdAt"),
    )


def item_profile(data: dict) -> "ItemProfile":
    from .types import ItemProfile

    if not data:
        return None
    return ItemProfile(
        id=data.get("id"),
        slug=data.get("slug"),
        priority=PriorityTypes.__members__.get(data.get("priority")),
        status=ItemStatuses.__members__.get(data.get("status")),
        name=data.get("name"),
        price=data.get("price"),
        raw_price=data.get("rawPrice"),
        seller_type=UserTypes.__members__.get(data.get("sellerType")),
        attachment=file(data.get("attachment")),
        user=user_profile(data.get("user")),
        approval_date=data.get("approvalDate"),
        priority_position=data.get("priorityPosition"),
        views_counter=data.get("viewsCounter"),
        fee_multiplier=data.get("feeMultiplier"),
        created_at=data.get("createdAt"),
    )


def item_profile_page_info(data: dict) -> "ItemProfilePageInfo":
    from .types import ItemProfilePageInfo

    if not data:
        return None
    return ItemProfilePageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def item_profile_list(data: dict) -> "ItemProfileList":
    from .types import ItemProfileList

    if not data:
        return None
    items = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            items.append(item_profile(edge.get("node")))
    return ItemProfileList(
        items=items,
        page_info=item_profile_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def moderator(data: dict) -> "Moderator": ...  # TODO: Сделать парсинг класса Moderator


def event(data: dict): ...  # TODO: Сделать парсинг класса Event


def chat(data: dict) -> "Chat":
    from .types import Chat

    if not data:
        return None
    users = []
    data_users = data.get("participants")
    if data_users:
        for user in data_users:
            users.append(user_profile(user))
    deals = []
    data_deals = data.get("deals")
    if data_deals:
        for deal in data_deals:
            deals.append(item_deal(deal))
    return Chat(
        id=data.get("id"),
        type=ChatTypes.__members__.get(data.get("type")),
        status=ChatStatuses.__members__.get(data.get("status")),
        unread_messages_counter=data.get("unreadMessagesCounter"),
        bookmarked=data.get("bookmarked"),
        is_texting_allowed=data.get("isTextingAllowed"),
        owner=user_profile(data.get("owner")),
        deals=deals,
        started_at=data.get("startedAt"),
        finished_at=data.get("finishedAt"),
        last_message=chat_message(data.get("lastMessage")),
        users=users,
    )


def chat_page_info(data: dict) -> "ChatPageInfo":
    from .types import ChatPageInfo

    if not data:
        return None
    return ChatPageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def chat_list(data: dict) -> "ChatList":
    from .types import ChatList

    if not data:
        return None
    chats = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            chats.append(chat(edge.get("node")))
    return ChatList(
        chats=chats,
        page_info=chat_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def review(data: dict) -> "Review":
    from .types import Review

    if not data:
        return None
    return Review(
        id=data.get("id"),
        status=ReviewStatuses.__members__.get(data.get("status")),
        text=data.get("text"),
        rating=data.get("rating"),
        created_at=data.get("createdAt"),
        updated_at=data.get("updatedAt"),
        deal=item_deal(data.get("deal")),
        creator=user_profile(data.get("creator")),
        moderator=moderator(data.get("moderator")),
        user=user_profile(data.get("user")),
    )


def review_page_info(data: dict) -> "ReviewPageInfo":
    from .types import ReviewPageInfo

    if not data:
        return None
    return ReviewPageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def review_list(data: dict) -> "ReviewList":
    from .types import ReviewList

    if not data:
        return None
    reviews = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            reviews.append(review(edge.get("node")))
    return ReviewList(
        reviews=reviews,
        page_info=review_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def item_deal(data: dict) -> "ItemDeal":
    from .types import ItemDeal

    if not data:
        return None
    logs = []
    data_logs: dict[dict] = data.get("logs")
    if data_logs:
        for log in data_logs:
            logs.append(item_log(log))
    obtaining_fields = []
    data_obtaining_fields = data.get("obtainingFields")
    if data_obtaining_fields:
        for field in data_obtaining_fields:
            obtaining_fields.append(game_category_data_field(field))
    return ItemDeal(
        id=data.get("id"),
        status=ItemDealStatuses.__members__.get(data.get("status")),
        status_expiration_date=data.get("statusExpirationDate"),
        status_description=data.get("statusDescription"),
        direction=ItemDealDirections.__members__.get(data.get("direction")),
        obtaining=data.get("obtaining"),
        has_problem=data.get("hasProblem"),
        report_problem_enabled=data.get("reportProblemEnabled"),
        completed_user=user_profile(data.get("completedBy")),
        props=data.get("props"),
        previous_status=data.get("prevStatus"),
        completed_at=data.get("completedAt"),
        created_at=data.get("createdAt"),
        logs=logs,
        transaction=transaction(data.get("transaction")),
        user=user_profile(data.get("user")),
        chat=chat(data.get("chat")),
        item=item(data.get("item")),
        review=review(data.get("testimonial")),
        obtaining_fields=obtaining_fields,
        comment_from_buyer=data.get("commentFromBuyer"),
    )


def item_deal_page_info(data: dict) -> "ItemDealPageInfo":
    from .types import ItemDealPageInfo

    if not data:
        return None
    return ItemDealPageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def item_deal_list(data: dict) -> "ItemDealList":
    from .types import ItemDealList

    if not data:
        return None
    deals = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            deals.append(item_deal(edge.get("node")))
    return ItemDealList(
        deals=deals,
        page_info=item_deal_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )


def chat_message_button(data: dict) -> "ChatMessageButton":
    from .types import ChatMessageButton

    if not data:
        return None
    return ChatMessageButton(
        type=ChatMessageButtonTypes.__members__.get(data.get("type")),
        url=data.get("url"),
        text=data.get("text"),
    )


def chat_message(data: dict) -> "ChatMessage":
    from .types import ChatMessage

    if not data:
        return None
    btns = []
    data_btns = data.get("buttons")
    if data_btns:
        for btn in data_btns:
            btns.append(chat_message_button(btn))
    return ChatMessage(
        id=data.get("id"),
        text=data.get("text"),
        created_at=data.get("createdAt"),
        deleted_at=data.get("deletedAt"),
        is_read=data.get("isRead"),
        is_suspicious=data.get("isSuspicious"),
        is_bulk_messaging=data.get("isBulkMessaging"),
        file=file(data.get("file")),
        game=game(data.get("game")),
        user=user_profile(data.get("user")),
        deal=item_deal(data.get("deal")),
        item=item(data.get("item")),
        transaction=transaction(data.get("transaction")),
        moderator=moderator(data.get("moderator")),
        event=event(data.get("event")),
        event_by_user=user_profile(data.get("eventByUser")),
        event_to_user=user_profile(data.get("eventToUser")),
        is_auto_response=data.get("isAutoResponse"),
        buttons=btns,
    )


def chat_message_page_info(data: dict) -> "ChatMessagePageInfo":
    from .types import ChatMessagePageInfo

    if not data:
        return None
    return ChatMessagePageInfo(
        start_cursor=data.get("startCursor"),
        end_cursor=data.get("endCursor"),
        has_previous_page=data.get("hasPreviousPage"),
        has_next_page=data.get("hasNextPage"),
    )


def chat_message_list(data: dict) -> "ChatMessageList":
    from .types import ChatMessageList

    if not data:
        return None
    messages = []
    edges: dict[dict] = data.get("edges")
    if edges:
        for edge in edges:
            messages.append(chat_message(edge.get("node")))
    return ChatMessageList(
        messages=messages,
        page_info=chat_message_page_info(data.get("pageInfo")),
        total_count=data.get("totalCount"),
    )
