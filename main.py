import re
import json
import decouple
import logging
import requests
import html
import traceback
from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultPhoto,
    InlineQueryResultsButton,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    InlineQueryHandler,
    ChosenInlineResultHandler,
)
from api import (
    TMDB_search_response_bot,
    TMDB_get_movie_additional_detail,
    TMDB_get_tv_series_additional_detail,
    TMDB_get_trailer,
    TMDB_MOVIE_DETAIL,
    TMDB_TV_SERIES_DETAIL,
    TV_MEDIA_TYPE,
    MOVIE_MEDIA_TYPE,
    TMDB_IMG_URL,
    TMDB_MOVIE_PAGE,
    TMDB_TV_SERIES_PAGE,
)
from db import (
    users_lang_clt,
    trailers_clt,
    media_detail_clt,
)


TOKEN = decouple.config('TOKEN')
DEVELOPER_CHAT_ID = decouple.config('DEVELOPER_CHAT_ID', cast=int)
IMDB_IMG_URL = r"https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/IMDb_Logo_Square.svg/480px-IMDb_Logo_Square.svg.png"
ENG_LANG = "en-US"
FA_LANG = "fa-IR"

"""
function commands
"""
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.INFO)

logger = logging.getLogger(__name__)
lang_from_start = {}
lang_from_language_callback = {}
movie_and_tv_detail_lang = {
    "movie": {
        ENG_LANG: "Movie",
        FA_LANG: "فیلم",
    },
    "tv_series": {
        ENG_LANG: "Tv Series",
        FA_LANG: "سریال تلوزیونی",
    },
    "user_ratings": {
        ENG_LANG: "Usᴇʀ Rᴀᴛɪɴɢs",
        FA_LANG: "امتیاز کاربران",
    },
    "imdb_id": {
        ENG_LANG: "𝙸ᴍᴅʙ 𝙸ᴅ",
        FA_LANG: "آیدی آی‌ام‌دی‌بی",
    },
    "type": {
        ENG_LANG: "Type",
        FA_LANG: "نوع",
    },
    "released_date": {
        ENG_LANG: "Rᴇʟᴇᴀsᴇ Dᴀᴛᴇ",
        FA_LANG: "تاریخ انتشار",
    },
    "language": {
        ENG_LANG: "Lᴀɴɢᴜᴀɢᴇ",
        FA_LANG: "زبان",
    },
    "genre": {
        ENG_LANG: "Gᴇɴʀᴇ",
        FA_LANG: "ژانر",
    },
    "story_line": {
        ENG_LANG: "Sᴛᴏʀy Lɪɴᴇ",
        FA_LANG: "خلاصه داستان",
    },
    "director": {
        ENG_LANG: "Dɪʀᴇᴄᴛᴏʀ",
        FA_LANG: "کارگردان",
    },
    "writer": {
        ENG_LANG: "Wʀɪᴛᴇʀ",
        FA_LANG: "نویسنده",
    },
    "actors": {
        ENG_LANG: "Aᴄᴛᴏʀs",
        FA_LANG: "بازیگران",
    },
    "air_date": {
        ENG_LANG: "Air Dᴀᴛᴇ",
        FA_LANG: "تاریخ پخش",
    },
    "season": {
        ENG_LANG: "Season",
        FA_LANG: "فصل",
    },
    "episode": {
        ENG_LANG: "Episode",
        FA_LANG: "قسمت",
    },
    "official_trailer": {
        ENG_LANG: "Official trailer",
        FA_LANG: "تریلر رسمی",
    },
    "non_official_trailer": {
        ENG_LANG: "Non official trailer",
        FA_LANG: "تریلر غیر رسمی",
    },
}


def TMDB_MOVIE_or_TV_series_detail(item: dict, media_type: str, img_url=False, language=ENG_LANG) -> tuple:
    """
    Get details of a movie or TV series from TMDB API response.

    Args:
        item (dict): The dictionary containing the details of the movie or TV series.
        media_type (str): The type of media (movie or TV series).
        img_url (bool, optional): Flag indicating whether to include the image URL. Defaults to False.

    Returns:
        tuple: A tuple containing the image and the string formatted details of the movie or TV series.
    """
    img = b""
    if img_url:
        img = ""
    if img_url and item['poster_path']:
        img = IMDB_IMG_URL + item['poster_path']
    temp = []
    if media_type == MOVIE_MEDIA_TYPE:
        if item['poster_path']:
            if not img_url:
                img = requests.get(f"{TMDB_IMG_URL}{item['poster_path']}").content
        if item['poster_path'] and item["imdb_id"] and item['year']:
            temp.append(f"<a href='{TMDB_IMG_URL + item['poster_path']}'>🎪</a> {movie_and_tv_detail_lang['movie'][language]}: <a href='https://www.imdb.com/title/{item['imdb_id']}'>{item['title']}</a> <i>({item['year']})</i>")
        elif item["imdb_id"] and item['year']:
            temp.append(f"🎪 {movie_and_tv_detail_lang['movie'][language]}: <a href='https://www.imdb.com/title/{item['imdb_id']}'>{item['title']}</a> <i>({item['year']})</i>")
        elif item['year']:
            temp.append(f"🎪 {movie_and_tv_detail_lang['movie'][language]}: {item['title']} (<i>({item['year']})</i>")
        else:
            temp.append(f"🎪 {movie_and_tv_detail_lang['movie'][language]}: {item['title']}")
        if item['vote_average'] and item['vote_count']:
            if language == ENG_LANG:
                temp.append(f"🏆 {movie_and_tv_detail_lang['user_ratings'][language]}: {item['vote_average']:.1f} / 10  <code>({item['vote_average']:.1f} based on {item['vote_count']} user ratings)</code>")
            elif language == FA_LANG:
                temp.append(f"🏆 {movie_and_tv_detail_lang['user_ratings'][language]}: 10 / {item['vote_average']:.1f}  <code>({item['vote_average']:.1f} بر اساس امتیاز {item['vote_count']} کاربر)</code>")
        if item["imdb_id"]:
            temp.append(f"🚦 {movie_and_tv_detail_lang['imdb_id'][language]}: <code>{item['imdb_id']}</code>")
        temp.append(f"🎦 {movie_and_tv_detail_lang['type'][language]}: {movie_and_tv_detail_lang['movie'][language]}")
        if item["release_date"]:
            temp.append(f"🗓️ {movie_and_tv_detail_lang['released_date'][language]}: <a href='https://www.imdb.com/title/{item['imdb_id']}/releaseinfo'>{item['release_date']}</a>")
        if item['languages']:
            temp.append(f"💬 {movie_and_tv_detail_lang['language'][language]}: {' '.join(['#'+lang for lang in item['languages']])}")
        if item['genres']:
            temp.append(f"📟 {movie_and_tv_detail_lang['genre'][language]}: {' '.join(['#'+genre.replace(' ', '_').replace('&', 'and') for genre in item['genres']])}")
        if item['overview'] and item['imdb_id']:
            temp.append(f"📋 {movie_and_tv_detail_lang['story_line'][language]}: {item['overview'][:200]} <a href='https://www.imdb.com/title/{item['imdb_id']}/plotsummary/'>...</a>")
        elif item['overview']:
            temp.append(f"📋 {movie_and_tv_detail_lang['story_line'][language]}: {item['overview'][:200]}...")
        if item['directors']:
            temp.append(f"🎥 {movie_and_tv_detail_lang['director'][language]}: {' '.join([d for d in item['directors']])}")
        if item['writers']:
            temp.append(f"✍️ {movie_and_tv_detail_lang['writer'][language]}: {' '.join([w for w in item['writers']])}")
        if item['casts']:
            temp.append(f"🎎 {movie_and_tv_detail_lang['actors'][language]}: {' '.join([a for a in item['casts']])}")
    elif media_type == TV_MEDIA_TYPE:
        if item['poster_path']:
            if not img_url:
                img = requests.get(f"{TMDB_IMG_URL}{item['poster_path']}").content
        if item['poster_path'] and item['year1'] and item['year2']:
            temp.append(f"<a href='{TMDB_IMG_URL + item['poster_path']}'>🎪</a> {movie_and_tv_detail_lang['tv_series'][language]}: {item['name']} <i>({item['year1']} - {item['year2']})</i>")
        elif item['year1'] and item['year2']:
            temp.append(f"🎪 {movie_and_tv_detail_lang['tv_series'][language]}: {item['name']} <i>({item['year1']} - {item['year2']})</i>")
        elif item['year1']:
            temp.append(f"🎪 {movie_and_tv_detail_lang['tv_series'][language]}: {item['name']} <i>({item['year1']})</i>")
        else:
            temp.append(f"🎪 {movie_and_tv_detail_lang['tv_series'][language]}: {item['name']}")
        temp.append(f"📺 {movie_and_tv_detail_lang['type'][language]}: {movie_and_tv_detail_lang['tv_series'][language]}")
        try:
            if item['first_air_date'] and item['last_air_date']:
                if language == ENG_LANG:
                    temp.append(f"🗓️ {movie_and_tv_detail_lang['air_date'][language]}: {item['first_air_date']} to {item['last_air_date']}")
                elif language == FA_LANG:
                    temp.append(f"🗓️ {movie_and_tv_detail_lang['air_date'][language]}: {item['first_air_date']} تا {item['last_air_date']}")
        except KeyError:
            if item['first_air_date']:
                temp.append(f"🗓️ {movie_and_tv_detail_lang['air_date'][language]}: {item['first_air_date']}")
        if item['languages']:
            temp.append(f"💬 {movie_and_tv_detail_lang['language'][language]}: {' '.join(['#'+lang for lang in item['languages']])}")
        if item['genres']:
            temp.append(f"📟 {movie_and_tv_detail_lang['genre'][language]}: {' '.join(['#'+genre.replace(' ', '_').replace('&', 'and') for genre in item['genres']])}")
        try:
            if item['overview']:
                temp.append(f"📋 {movie_and_tv_detail_lang['story_line'][language]}: {item['overview'][:200]}...")
        except KeyError:
            if item['overview']:
                temp.append(f"📋 {movie_and_tv_detail_lang['story_line'][language]}: {item['overview'][:200]}...")
        if item['directors']:
            temp.append(f"🎥 {movie_and_tv_detail_lang['director'][language]}: {' '.join([d for d in item['directors']])}")
        if item['writers']:
            temp.append(f"✍️ {movie_and_tv_detail_lang['writer'][language]}: {' '.join([w for w in item['writers']])}")
        if item['casts']:
            temp.append(f"🎎 {movie_and_tv_detail_lang['actors'][language]}: {' '.join([a for a in item['casts']])}")

    return img, '\n'.join(temp)


def get_inline_keyboard_trailer(trailers: list, media_type: str, item: dict, language=ENG_LANG) -> list:
    """
    Generate inline keyboards for trailers.

    Args:
        trailers (list): List of trailers.
        media_type (str): The type of media (movie or TV series).
        item (dict): The dictionary containing the details of the movie or TV series.

    Returns:
        list: List of inline keyboards for trailers.
    """

    inline_keyboards = []
    if trailers:
        for trailer in trailers:
            year = ""
            if media_type == MOVIE_MEDIA_TYPE and item['year']:
                year = item['year']
            elif media_type == TV_MEDIA_TYPE and item['year1'] and item['year2']:
                year = f"{item['year1']}-{item['year2']}"
            elif media_type == TV_MEDIA_TYPE and item['year1']:
                year = f"{item['year1']}"

            text = f"📺 {trailer['name']}"
            if year:
                text += f" ({year})"
            if trailer['official']:
                text += f" [{movie_and_tv_detail_lang['official_trailer'][language]}]"
            elif not trailer['official'] and trailer['type'] == "Trailer":
                text += f" [{movie_and_tv_detail_lang['non_official_trailer'][language]}]"
            else:
                text += f" [{trailer['type']}]"
            inline_keyboards.append(
                [InlineKeyboardButton(text=text, url=trailer['url'])]
            )

    return inline_keyboards


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command.

    Args:
        update (telegram.Update): The update object.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object.
    """
    user = update.effective_chat
    name = user.first_name if user.first_name else user.last_name
    user_mention = f"<a href='tg://user?id={user.id}'>{name}</a>"

    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
    else:
        await language(update, context)
        lang_from_start[f"from-start---{user.id}"] = True
        return


    en_start_text = f"""Hi {user_mention}👋. This is <code>IMDB</code> bot!

You can type Movie Name and Year correctly in this chat

OR

Search InLine by clicking on the below buttons"""
    fa_start_text = f"""سلام {user_mention}👋. این ربات <code>IMDB</code> است!

شما می‌توانید اسم فیلم و سال آن را تایپ کنید و بفرستید

یا

روی دکمه زیر کلیک کنید و با حالت درون خطی فیلم موردنظر پیدا کنید"""
    en_inline_text = "🔍find me the movie"
    fa_inline_text = "🔍فیلم را برای من پیدا کن"

    if lang == ENG_LANG:
        start_text = en_start_text
        inline_text = en_inline_text
    elif lang == FA_LANG:
        start_text = fa_start_text
        inline_text = fa_inline_text

    inline_keyboards = [
        [InlineKeyboardButton(
        text=inline_text,
        switch_inline_query_current_chat="",)]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.message.id,
        text=start_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboards),
        parse_mode=ParseMode.HTML,
    )


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays a language selection message to the user and allows them to choose their preferred language.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.Context): The context object for the current update.

    Returns:
        None

    """
    user = update.effective_chat
    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
    else:
        lang = ENG_LANG

    en_text = "Please choose your language"
    fa_text = "لطفا زبان خود را انتخاب کنید"
    en_inline_text_english = "🇺🇸 English"
    en_inline_text_persian = "🇮🇷 Persian"
    fa_inline_text_english = "🇺🇸 انگلیسی"
    fa_inline_text_persian = "🇮🇷 فارسی"

    if lang == ENG_LANG:
        text = en_text
        eng_inline_text = en_inline_text_english
        fas_inline_text = en_inline_text_persian
    elif lang == FA_LANG:
        text = fa_text
        eng_inline_text = fa_inline_text_english
        fas_inline_text = fa_inline_text_persian
    inline_keyboards = [
        [InlineKeyboardButton(
            text=eng_inline_text,
            callback_data=f"userlang---{ENG_LANG}",),
        InlineKeyboardButton(
            text=fas_inline_text,
            callback_data=f"userlang---{FA_LANG}",)]
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.message.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboards),
        parse_mode=ParseMode.HTML,
    )


async def language_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the callback query for changing the language of the bot.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.Context): The context object for the current update.

    Returns:
        None

    """
    query = update.callback_query
    user = update.effective_chat
    _, lang = query.data.split('---')
    try:
        _ = users_lang_clt.update_one({"key": f"userlang---{user.id}"},
                                      {"$set": {"key": f"userlang---{user.id}",
                                                "value": lang}},
                                       upsert=True
        )
        start = lang_from_start.get(f"from-start---{user.id}", "")
        if lang == ENG_LANG and start:
            text = "The bot language is successfully selected as <b>English</b>."
        elif lang == FA_LANG and start:
            text = "زبان ربات با موفقیت <b>فارسی</b> فارسی انتخاب شد."
        elif lang == ENG_LANG:
            text = "The bot language has been successfully changed to <b>English</b>.\nClick on /help command to see bot commands."
        elif lang == FA_LANG:
            text = "زبان ربات با موفقیت به <b>فارسی</b> تغییر کرد.\nبرای دیدن دستورات ربات روی دستور /help بزنید."
        # for change help command
        lang_from_start[f"from-lang-callback---{user.id}"] = True
        await help(update, context)
    except:
        if lang == ENG_LANG:
            text = "Unfortunately, an error occurred and we could not change the language of the bot. Please try again later\nClick on /help command to see bot commands."
        elif lang == FA_LANG:
            text = "متاسفانه خطایی رخ داد و نتوانستیم زبان ربات را تغییر دهیم. لطفا بعدا تلاش فرمایید\nبرای دیدن دستورات ربات روی دستور /help بزنید."

    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
    )
    try:
        if start:
            del lang_from_start[f"from-start---{user.id}"]
            name = user.first_name if user.first_name else user.last_name
            user_mention = f"<a href='tg://user?id={user.id}'>{name}</a>"
            en_start_text = f"""Hi {user_mention}👋. This is <code>IMDB</code> bot!

You can type Movie Name and Year correctly in this chat

OR

Search InLine by clicking on the below buttons"""
            fa_start_text = f"""سلام {user_mention}👋. این ربات <code>IMDB</code> است!

شما می‌توانید اسم فیلم و سال آن را تایپ کنید و بفرستید

یا

روی دکمه زیر کلیک کنید و با حالت درون خطی فیلم موردنظر پیدا کنید"""
            en_inline_text = "🔍find me the movie"
            fa_inline_text = "🔍فیلم را برای من پیدا کن"

            if lang == ENG_LANG:
                start_text = en_start_text
                inline_text = en_inline_text
            elif lang == FA_LANG:
                start_text = fa_start_text
                inline_text = fa_inline_text

            inline_keyboards = [
                [InlineKeyboardButton(
                text=inline_text,
                switch_inline_query_current_chat="",)]
            ]

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=start_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboards),
                parse_mode=ParseMode.HTML,
            )
    except NameError:
        pass


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display the available commands and their descriptions.

    Args:
        update (telegram.Update): The update object.
        context (telegram.ext.callbackcontext.CallbackContext): The callback context object.

    Returns:
        None
    """
    user = update.effective_chat
    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
    else:
        lang = ENG_LANG

    en_start_desc = "Start the bot"
    fa_start_desc = "استارت ربات"
    en_language_desc = "Choose the language of the bot"
    fa_language_desc = "انتخاب کردن زبان ربات"
    en_help_desc = "Get help and commands"
    fa_help_desc = "دریافت کمک و دستورات ربات"
    en_search_desc = "Search for the name of a movie or TV series line => \"/search inception\""
    fa_search_desc = "جستجو برای نام فیلم یا سریال مثل => \"/search تلقین\""
    en_list_desc = "Get the list along with the search details of the name of the movie or TV series => \"/list inception\""
    fa_list_desc = "نتیجه نامی را جستجو کرده‌اید به صورت لیستی و به همراه جزئیات فیلم یا سریال دریافت کنید => \"/list تلقین\""

    if lang == ENG_LANG:
        start_desc = en_start_desc
        language_desc = en_language_desc
        help_desc = en_help_desc
        search_desc = en_search_desc
        list_desc = en_list_desc
    elif lang == FA_LANG:
        start_desc = fa_start_desc
        language_desc = fa_language_desc
        help_desc = fa_help_desc
        search_desc = fa_search_desc
        list_desc = fa_list_desc

    command_list = [
        BotCommand("start", start_desc),
        BotCommand("language", language_desc),
        BotCommand("help", help_desc),
        BotCommand("search", search_desc),
        BotCommand("list", list_desc),
    ]

    await context.bot.set_my_commands(command_list[:3])

    # for change command description with change language
    from_lang = lang_from_start.get(f"from-lang-callback---{user.id}", False)
    if from_lang:
        del lang_from_start[f"from-lang-callback---{user.id}"]
        return

    command_list_text = []
    for cmd in command_list:
        command_list_text.append(f"/{cmd.command} - {cmd.description}")

    command_list_text = '\n'.join(command_list_text)

    en_text = f"<b>Here are the available commands:</b>\n\n{command_list_text}"
    fa_text = f"<b>دستورات ربات که می‌توانید از آن استفاده کنید</b>:\n\n{command_list_text}"
    if lang == ENG_LANG:
        text = en_text
    elif lang == FA_LANG:
        text = fa_text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.message.id,
        text=text,
        parse_mode=ParseMode.HTML
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    if DEVELOPER_CHAT_ID:
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
        )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for unknown commands or messages.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.ContextTypes.Context): The context object for the handler.

    Returns:
        None
    """
    user = update.effective_chat
    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
        if lang == ENG_LANG:
            text = "Sorry, I didn't understand that command."
        elif lang == FA_LANG:
            text = "متاسفم، این دستور را متوجه نمیشوم."
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text)


async def movie_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Retrieves a list of movies based on user input and sends it as a message.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.ContextTypes.Context): The context object.

    Command:
        /list - Retrieves a list of movies and sends it as a message.

    Returns:
        None
    """
    message = ' '.join(context.args)

    user = update.effective_chat
    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
    else:
        lang = ENG_LANG

    en_wait_text = "Please wait. It may take a while"
    fa_wait_text = "لطفا صبر کنید. ممکن است این روند کمی طول بکشد"
    en_not_found_text = "Sorry. We could not find anything similar.\nPlease check <u>the spelling of the movie name</u> and send again!"
    fa_not_found_text = "متاسفیم. نتوانستیم چیزی شبیه این پیدا کنیم. لطفا به <u>املای اسم فیلم یا سریالی</u> که فرستاده‌اید دقت کنید و مجددا ارسال کنید!"

    if lang == ENG_LANG:
        wait_text = en_wait_text
        not_found_text = en_not_found_text
    elif lang == FA_LANG:
        wait_text = fa_wait_text
        not_found_text = fa_not_found_text

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_to_message_id=update.message.id,
                                   text=wait_text,
                                   parse_mode=ParseMode.HTML)

    results = TMDB_search_response_bot(message, language=lang)

    if not results:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       reply_to_message_id=update.message.id,
                                       text=not_found_text,
                                       parse_mode=ParseMode.HTML)
        return

    en_found_text = f"We found <b>{len(results)}</b> movies and TV series. And we will send you the details of each of them below."
    fa_found_text = f"ما <b>{len(results)}</b> فیلم و سریال تلویزیونی پیدا کردیم. و جزئیات هر یک را در زیر برای شما ارسال خواهیم کرد."
    if lang == ENG_LANG:
        found_text = en_found_text
    elif lang == FA_LANG:
        found_text = fa_found_text

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_to_message_id=update.message.id,
                                   text=found_text,
                                   parse_mode=ParseMode.HTML)

    results_message_list = []
    for i, item in enumerate(results, start=1):
        if item["poster_path"]:
            img_url = TMDB_IMG_URL + item['poster_path']
        _, text = TMDB_MOVIE_or_TV_series_detail(item, item['media_type'], img_url=False, language=lang)

        # get trailers
        media_type = item['media_type']
        ids = item['id']
        trailers_filter = {"key": f"trailers---{media_type}---{str(ids)}---{lang}"}
        trailers = trailers_clt.find_one(trailers_filter)
        if not trailers:
            trailers = TMDB_get_trailer(ids, media_type, language=lang)
            if lang == FA_LANG and not trailers:
                trailers = TMDB_get_trailer(ids, media_type, language=ENG_LANG)
            _ = trailers_clt.update_one(
                    trailers_filter,
                    {"$set": {"key": f"trailers---{media_type}---{str(ids)}---{lang}",
                              "value": trailers}},
                    upsert=True
            )
        else:
            trailers = trailers.get("value")
        inline_keyboards = get_inline_keyboard_trailer(trailers,
                                                       media_type,
                                                       item,
                                                       lang)

        results_message_list.append((
            f"{i}. {text}",
            img_url,
            inline_keyboards[::-1]))

    for item, img_url, keyboards in results_message_list:
        if not img_url:
            img_url = requests.get(IMDB_IMG_URL, stream=True).content
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=img_url,
            has_spoiler=True,
            caption=item,
            reply_to_message_id=update.message.id,
            reply_markup=InlineKeyboardMarkup(keyboards),
            parse_mode=ParseMode.HTML,
        )


async def movie_bot_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /search command and searches for movies based on the provided query.
    If the command is not used, it searches for movies directly using the message text.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.ContextTypes): The context object.

    Returns:
        None
    """
    user = update.effective_chat
    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
    else:
        lang = ENG_LANG

    search_cmd_regex = r"^\/search "
    movie_name = update.message.text
    movie_name = re.sub(search_cmd_regex, '', movie_name)

    en_wait_text = "Please wait. It may take a while"
    fa_wait_text = "لطفا صبر کنید. ممکن است این روند کمی طول بکشد"
    en_found_text = "We found these movies and TV series. please choose it!"
    fa_found_text = "ما این فیلم‌ها و سریال‌ها را پیدا کردیم. لطفا انتخاب کنید!"
    en_not_found_text = "Sorry. We could not find anything similar.\nPlease check <u>the spelling of the movie name</u> and send again!"
    fa_not_found_text = "متاسفیم. نتوانستیم چیزی شبیه این پیدا کنیم. لطفا به <u>املای اسم فیلم یا سریالی</u> که فرستاده‌اید دقت کنید و مجددا ارسال کنید!"

    if lang == ENG_LANG:
        wait_text = en_wait_text
        found_text = en_found_text
        not_found_text = en_not_found_text
    elif lang == FA_LANG:
        wait_text = fa_wait_text
        found_text = fa_found_text
        not_found_text = fa_not_found_text

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_to_message_id=update.message.id,
                                   text=wait_text)

    results = TMDB_search_response_bot(movie_name, language=lang)
    if not results:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       reply_to_message_id=update.message.id,
                                       text=not_found_text,
                                       parse_mode=ParseMode.HTML)
        return

    buttons = []
    for item in results:
        if item["media_type"] == MOVIE_MEDIA_TYPE:
            text = f"{item['title']}"
            if item["year"]:
                text += f" ({item['year']})"
            if item["casts"] and len(item["casts"]) >= 2:
                text += f" [{' '.join([a for a in item['casts'][:2]])}]"
            if item["casts"]:
                text += f" [{' '.join([a for a in item['casts']])}]"
            callback_data = f"{item['media_type']}-{item['id']}"
            buttons.append([InlineKeyboardButton(text=text,
                                                 callback_data=callback_data)])
        elif item["media_type"] == TV_MEDIA_TYPE:
            text = f"{item['name']}"
            if item["year1"] and item["year2"]:
                text += f" ({item['year1']}-{item['year2']})"
            if item["year1"]:
                text += f" ({item['year1']})"
            if item["casts"] and len(item["casts"]) >= 2:
                text += f" [{' '.join([a for a in item['casts'][:2]])}]"
            if item["casts"]:
                text += f" [{' '.join([a for a in item['casts']])}]"
            callback_data = f"{item['media_type']}-{item['id']}"
            buttons.append([InlineKeyboardButton(item["name"],
                                                 callback_data=callback_data)])

    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=IMDB_IMG_URL,
                                 caption=found_text,
                                 reply_to_message_id=update.message.id,
                                 reply_markup=InlineKeyboardMarkup(buttons),)


async def movie_inline_search_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the callback query from the search results when a user selects a movie.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.ContextTypes): The context object.

    Returns:
        None
    """
    # message format: "media_type-movie_or_series_id"
    query = update.callback_query
    media_type, ids = query.data.split('-')
    ids = int(ids)

    user = query.from_user
    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
    else:
        lang = ENG_LANG

    media_detail_filter = {"key": f"{media_type}---{str(ids)}---{lang}"}
    if media_type == MOVIE_MEDIA_TYPE:
        item = media_detail_clt.find_one(media_detail_filter)
        if not item:
            item = TMDB_get_movie_additional_detail(ids, detail=True, language=lang)
            _ = media_detail_clt.update_one(
                    media_detail_filter,
                    {"$set": {"key": media_detail_filter,
                              "value": item}},
                    upsert=True
            )
        else:
            item = item.get("value")
        img, caption = TMDB_MOVIE_or_TV_series_detail(item, MOVIE_MEDIA_TYPE, language=lang)
    elif media_type == TV_MEDIA_TYPE:
        item = media_detail_clt.find_one(media_detail_filter)
        if not item:
            item = TMDB_get_tv_series_additional_detail(ids, detail=True, language=lang)
            _ = media_detail_clt.update_one(
                    media_detail_filter,
                    {"$set": {"key": media_detail_filter,
                              "value": item}},
                    upsert=True
            )
        else:
            item = item.get("value")
        img, caption = TMDB_MOVIE_or_TV_series_detail(item, TV_MEDIA_TYPE, language=lang)

    # get trailers
    trailers_filter = {"key": f"trailers---{media_type}---{str(ids)}---{lang}"}
    trailers = trailers_clt.find_one(trailers_filter)
    if not trailers:
        trailers = TMDB_get_trailer(ids, media_type, language=lang)
        if lang == FA_LANG and not trailers:
            trailers = TMDB_get_trailer(ids, media_type, language=ENG_LANG)
        _ = trailers_clt.update_one(
                trailers_filter,
                {"$set": {"key": f"trailers---{media_type}---{str(ids)}---{lang}",
                          "value": trailers}},
                upsert=True
        )
    else:
        trailers = trailers.get("value")
    inline_keyboards = get_inline_keyboard_trailer(trailers, media_type, item, lang)
    inline_keyboards = inline_keyboards[::-1]

    if img:
        await query.edit_message_media(InputMediaPhoto(img,
                                                       has_spoiler=True))
    await query.edit_message_caption(caption=caption,
                                     parse_mode=ParseMode.HTML)
    if inline_keyboards:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboards),
        )


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle inline queries for the bot.
    This is run when you type: @botusername <query>

    This function is triggered when a user sends an inline query to the bot. It performs a search based on the query
    and returns relevant results as inline query results.

    Args:
        update (Update): The update object containing information about the inline query.
        context (ContextTypes): The context object containing the bot's context.

    Returns:
        None
    """

    # inline start message
    user = update.effective_user
    name = user.first_name if user.first_name else user.last_name
    user_mention = f"<a href='tg://user?id={user.id}'>{name}</a>"

    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
    else:
        lang = ENG_LANG
    en_start_text = f"Hi {user_mention}👋. This is <code>IMDB</code> bot!"
    fa_start_text = f"سلام {user_mention}👋. این ربات <code>IMDB</code> است!"
    en_search_text = "Enter Movie Name to Search"
    fa_search_text = "نام فیلم را برای جستجو وارد کنید"

    if lang == ENG_LANG:
        text = en_start_text
        search_text = en_search_text
    elif lang == FA_LANG:
        text = fa_start_text
        search_text = fa_search_text

    # message format: "media_type-movie_or_series_id"
    image_url = r"https://image.tmdb.org/t/p/w500"
    movie_name = update.inline_query.query
    button = InlineQueryResultsButton(
            text=search_text,
            start_parameter="start"
        )

    if not movie_name:  # empty query should be handled
        await update.inline_query.answer(results=[], button=button, cache_time=0)

    results = TMDB_search_response_bot(movie_name, ENG_LANG)

    en_found_text = f"IMDB: Found {len(results)} Results for '{movie_name}'"
    fa_found_text = f"آی‌ام‌دی‌بی: {len(results)} نتیجه برای '{movie_name}' پیدا شد"
    en_not_found_text = f"IMDB: Found 0 Results for '{movie_name}'"
    fa_not_found_text = f"آی‌ام‌دی‌بی: هیچ نتیجه‌ای برای '{movie_name}' پیدا نشد"
    en_search_title = "Enter a movie name to search IMDB"
    fa_search_title = "نام فیلم را برای جستجو در آی‌ام‌دی‌بی وارد کنید"
    en_search_desc = "This is Telegram IMDb Movie search bot"
    fa_search_desc = "این ربات جستجوی فیلم تلگرام آی‌ام‌دی‌بی است"
    en_inline_text = "🔍find me the movie"
    fa_inline_text = "🔍فیلم را برای من پیدا کن"
    en_open = "Open"
    fa_open = "باز کردن"
    if lang == ENG_LANG:
        found_text = en_found_text
        not_found_text = en_not_found_text
        search_title = en_search_title
        search_desc = en_search_desc
        inline_text = en_inline_text
        opn = en_open
    elif lang == FA_LANG:
        found_text = fa_found_text
        not_found_text = fa_not_found_text
        search_title = fa_search_title
        search_desc = fa_search_desc
        inline_text = fa_inline_text
        opn = fa_open

    if results:
        button = InlineQueryResultsButton(
            text=found_text,
            start_parameter="start"
        )
        inline_results = [
            InlineQueryResultArticle(
                id="start",
                title=search_title,
                input_message_content=InputTextMessageContent(
                    text,
                    parse_mode=ParseMode.HTML,),
                description=search_desc,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        text=inline_text,
                        switch_inline_query_current_chat="",)]]
                ),
            ),
        ]
        for item in results:
            if item["media_type"] == MOVIE_MEDIA_TYPE:
                if item['imdb_id']:
                    inline_ketboard_url = f"https://www.imdb.com/title/{item['imdb_id']}"
                    inline_ketboard_text = f"{opn} IMDB"
                elif item["media_type"] == MOVIE_MEDIA_TYPE:
                    inline_ketboard_url = TMDB_MOVIE_PAGE + str(item['id'])
                    inline_ketboard_text = f"{opn} TMDB"
            elif item["media_type"] == TV_MEDIA_TYPE:
                inline_ketboard_url = TMDB_TV_SERIES_PAGE + str(item['id'])
                inline_ketboard_text = f"{opn} TMDB"

            if item["media_type"] == MOVIE_MEDIA_TYPE:
                if item['year']:
                    caption = f"<a href='{TMDB_MOVIE_DETAIL}{item['id']}'>{item['title']} ({item['year']})</a>"
                else:
                    caption = f"<a href='{TMDB_MOVIE_DETAIL}{item['id']}'>{item['title']}</a>"
                if item['poster_path']:
                    inline_results.append(InlineQueryResultPhoto(
                        id=f"{item['media_type']}-{item['id']}",
                        photo_url=f"{image_url}{item['poster_path']}",
                        thumbnail_url=f"{image_url}{item['poster_path']}",
                        title=item['original_title'],
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                            text=inline_ketboard_text,
                            url=inline_ketboard_url)]])))
                else:
                    inline_results.append(InlineQueryResultPhoto(
                        id=f"{item['media_type']}-{item['id']}",
                        photo_url=f"{IMDB_IMG_URL}",
                        thumbnail_url=f"{IMDB_IMG_URL}",
                        title=item['title'],
                        photo_width=92,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                            text=inline_ketboard_text,
                            url=inline_ketboard_url)]])))
            elif item["media_type"] == TV_MEDIA_TYPE:
                if item['year1'] and item['year2']:
                    caption = f"<a href='{TMDB_TV_SERIES_DETAIL}{item['id']}'>{item['name']} ({item['year1']}-{item['year2']})</a>"
                elif item['year1']:
                    caption = f"<a href='{TMDB_TV_SERIES_DETAIL}{item['id']}'>{item['name']} ({item['year1']})</a>"
                else:
                    caption = f"<a href='{TMDB_TV_SERIES_DETAIL}{item['id']}'>{item['name']}</a>"
                if item['poster_path']:
                    inline_results.append(InlineQueryResultPhoto(
                        id=f"{item['media_type']}-{item['id']}",
                        photo_url=f"{image_url}{item['poster_path']}",
                        thumbnail_url=f"{image_url}{item['poster_path']}",
                        title=item['name'],
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                            text=inline_ketboard_text,
                            url=inline_ketboard_url)]])))
                else:
                    inline_results.append(InlineQueryResultPhoto(
                        id=f"{item['media_type']}-{item['id']}",
                        photo_url=f"{IMDB_IMG_URL}",
                        thumbnail_url=f"{IMDB_IMG_URL}",
                        title=item['name'],
                        photo_width=92,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                            text=inline_ketboard_text,
                            url=inline_ketboard_url)]])))
        try:
            await update.inline_query.answer(inline_results, button=button, cache_time=0)
        except BadRequest as e:
            # Ignore the "Query is too old" error
            if "Query is too old" in str(e):
                pass
            else:
                logger.error("BadRequest error: %s", e)
    else:
        button = InlineQueryResultsButton(
            text=not_found_text,
            start_parameter="start"
        )
        await update.inline_query.answer(results=[], button=button, cache_time=0)


async def inline_chosen_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the user selection when using the bot in inline mode.

    This function is called when a user selects a result from the inline query.
    It retrieves the selected result and performs the necessary actions based on the result type.

    Args:
        update (Update): The update object containing the chosen inline query result.
        context (ContextTypes.Context): The context object for accessing bot functionality.

    Returns:
        None
    """
    chosen_inline_result = update.chosen_inline_result
    user = update.chosen_inline_result.from_user
    lang = users_lang_clt.find_one({"key": f"userlang---{user.id}"})
    if lang:
        lang = lang.get("value")
    else:
        lang = ENG_LANG

    # get the deatil of movie by request and showing them
    if chosen_inline_result.result_id == "start":
        name = user.first_name if user.first_name else user.last_name
        user_mention = f"<a href='tg://user?id={user.id}'>{name}</a>"
        en_start_text = f"""Hi {user_mention}👋. This is <code>IMDB</code> bot!

You can type Movie Name and Year correctly in this chat

OR

Search InLine by clicking on the below buttons"""
        fa_start_text = f"""سلام {user_mention}👋. این ربات <code>IMDB</code> است!

شما می‌توانید اسم فیلم و سال آن را تایپ کنید و بفرستید

یا

روی دکمه زیر کلیک کنید و با حالت درون خطی فیلم موردنظر پیدا کنید"""
        en_inline_text = "🔍find me the movie"
        fa_inline_text = "🔍فیلم را برای من پیدا کن"

        if lang == ENG_LANG:
            start_text = en_start_text
            inline_text = en_inline_text
        elif lang == FA_LANG:
            start_text = fa_start_text
            inline_text = fa_inline_text

        inline_keyboards = [
            [InlineKeyboardButton(
                text=inline_text,
                switch_inline_query_current_chat="",)]
        ]
        if update.chosen_inline_result.inline_message_id:
            inline_message_id = chosen_inline_result.inline_message_id
            await context.bot.edit_message_text(
                inline_message_id=inline_message_id,
                text=start_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboards),
                parse_mode=ParseMode.HTML,
            )
        return

    media_type, ids = chosen_inline_result.result_id.split('-')
    media_detail_filter = {"key": f"{media_type}---{str(ids)}---{lang}"}
    if media_type == MOVIE_MEDIA_TYPE:
        item = media_detail_clt.find_one(media_detail_filter)
        if not item:
            item = TMDB_get_movie_additional_detail(ids, detail=True, language=lang)
            _ = media_detail_clt.update_one(
                        media_detail_filter,
                        {"$set": {"key": media_detail_filter,
                                  "value": item}},
                        upsert=True
            )
        else:
            item.get("value")
        img, caption = TMDB_MOVIE_or_TV_series_detail(item, MOVIE_MEDIA_TYPE, language=lang)
    elif media_type == TV_MEDIA_TYPE:
        item = media_detail_clt.find_one(media_detail_filter)
        if not item:
            item = TMDB_get_tv_series_additional_detail(ids, detail=True, language=lang)
            _ = media_detail_clt.update_one(
                        media_detail_filter,
                        {"$set": {"key": media_detail_filter,
                                  "value": item}},
                        upsert=True
            )
        else:
            item = item.get("value")
        img, caption = TMDB_MOVIE_or_TV_series_detail(item, TV_MEDIA_TYPE, language=lang)

    if not img:
        img = requests.get(IMDB_IMG_URL, stream=True).content

    # get trailers
    trailers_filter = {"key": f"trailers---{media_type}---{str(ids)}---{lang}"}
    trailers = trailers_clt.find_one(trailers_filter)
    if not trailers:
        trailers = TMDB_get_trailer(ids, media_type, language=lang)
        if lang == FA_LANG and not trailers:
            trailers = TMDB_get_trailer(ids, media_type, language=ENG_LANG)
        _ = trailers_clt.update_one(
                trailers_filter,
                {"$set": {"key": f"trailers---{media_type}---{str(ids)}---{lang}",
                          "value": trailers}},
                upsert=True
        )
    else:
        trailers = trailers.get("value")
    inline_keyboards = get_inline_keyboard_trailer(trailers, media_type, item, lang)
    inline_keyboards = inline_keyboards[::-1]

    if update.chosen_inline_result.inline_message_id:
        inline_message_id = chosen_inline_result.inline_message_id
        try:
            await context.bot.edit_message_media(
                inline_message_id=inline_message_id,
                media=InputMediaPhoto(
                    media=img,
                    has_spoiler=True,),
            )
        except BadRequest as e:
            if "Invalid message content specified" in str(e):
                pass
            else:
                logger.error("BadRequest error: %s", e)
        await context.bot.edit_message_caption(
            inline_message_id=inline_message_id,
            caption=caption,
            parse_mode=ParseMode.HTML
        )
        if inline_keyboards:
            await context.bot.edit_message_reply_markup(
                inline_message_id=inline_message_id,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboards),
            )


if __name__ == "__main__":
    # Build the Telegram bot application
    application = ApplicationBuilder().token(token=TOKEN).build()

    # Define command handlers
    start_handler = CommandHandler("start", start)
    language_handler = CommandHandler("language", language)
    help_handler = CommandHandler("help", help)
    search_handler = CommandHandler("search", movie_bot_search)
    movie_list_handler = CommandHandler("list", movie_list)

    # Define message handlers
    movie_list_inline_search_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND),
        movie_bot_search)

    # Define callback handler
    movie_inline_search_callback_query_handler = CallbackQueryHandler(
        movie_inline_search_callback_query, pattern=r"^(movie|tv)?\-\d+$")
    language_callback_query_handler = CallbackQueryHandler(
        language_callback_query,
        pattern=r"^userlang\-\-\-[\w-]+$"
    )

    # Define inline query handler
    inline_query_handler = InlineQueryHandler(inline_query)

    # Define chosen inline result handler
    inline_chosen_result_handler = ChosenInlineResultHandler(
        inline_chosen_result)

    # Define unknown command handler
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # Add handlers to the application
    application.add_handler(start_handler)
    application.add_handler(language_handler)
    application.add_handler(help_handler)
    application.add_handler(search_handler)
    application.add_handler(movie_list_handler)
    application.add_handler(movie_list_inline_search_handler)
    application.add_handler(movie_inline_search_callback_query_handler)
    application.add_handler(language_callback_query_handler)
    application.add_handler(inline_query_handler)
    application.add_handler(inline_chosen_result_handler)
    application.add_handler(unknown_handler)
    application.add_error_handler(error_handler)

    # Start the bot application
    application.run_polling()
