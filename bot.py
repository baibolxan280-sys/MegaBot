import asyncio
import logging
import re
import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)  # исправлено: __name__ вместо name

# ============================================
# ⚠️  ВАЖНО: ПОЛУЧИ НОВЫЙ ТОКЕН У @BotFather!
# ============================================
# Токен бота - ВСТАВЬ СВОЙ ТОКЕН ЗДЕСЬ!
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Вставь свой актуальный токен

# Username менеджера (без @) - ТОЛЬКО ДЛЯ ВНУТРЕННЕГО ИСПОЛЬЗОВАНИЯ!
MANAGER_USERNAME = "SSQLGF"

# Файл для хранения состояния
STATE_FILE = "bot_state.json"


# Загружаем состояние из файла
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"manager_active": False, "manager_chat_id": None}
    return {"manager_active": False, "manager_chat_id": None}


# Сохраняем состояние в файл
def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# Загружаем состояние при запуске
state = load_state()
manager_active = state.get("manager_active", False)
manager_chat_id = state.get("manager_chat_id", None)

# Проверка токена
if not BOT_TOKEN or len(BOT_TOKEN) < 10:
    print("\n" + "=" * 60)
    print("❌ ОШИБКА: Не указан токен бота!")
    print("=" * 60)
    print("\nИнструкция по получению токена:")
    print("1. Открой Telegram")
    print("2. Найди @BotFather")
    print("3. Отправь команду /newbot")
    print("4. Следуй инструкциям BotFather")
    print("5. Скопируй полученный токен")
    print("6. Вставь его в переменную BOT_TOKEN")
    print("\nПример правильного токена: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    print("=" * 60)
    exit()

# Создаем экземпляры бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


# ============================================
# КЛАВИАТУРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
# ============================================

def get_user_main_keyboard():
    """Основная клавиатура для пользователей"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Задать вопрос"),
                KeyboardButton(text="📞 Связаться с поддержкой")
            ],
            [
                KeyboardButton(text="📊 Статус обращения"),
                KeyboardButton(text="ℹ️ О боте")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard


def get_user_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отменить")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_user_back_keyboard():
    """Клавиатура с кнопкой назад"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад в меню")]
        ],
        resize_keyboard=True
    )
    return keyboard


# ============================================
# INLINE КНОПКИ
# ============================================

def get_support_buttons():
    """Inline кнопки для раздела поддержки"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📧 Отправить сообщение",
        callback_data="send_message"
    ))
    builder.add(InlineKeyboardButton(
        text="📋 Часто задаваемые вопросы",
        callback_data="faq"
    ))
    builder.add(InlineKeyboardButton(
        text="📞 Срочная связь",
        callback_data="urgent"
    ))
    builder.adjust(1)  # По одной кнопке в ряд
    return builder.as_markup()


def get_faq_buttons():
    """Кнопки с частыми вопросами"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="❓ Как работает бот?",
        callback_data="faq_how"
    ))
    builder.add(InlineKeyboardButton(
        text="⏱ Время ответа",
        callback_data="faq_time"
    ))
    builder.add(InlineKeyboardButton(
        text="📱 Контакты",
        callback_data="faq_contacts"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back_to_support"
    ))
    builder.adjust(1)
    return builder.as_markup()


# ============================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    global manager_active, manager_chat_id, state

    # Проверяем, является ли пользователь менеджером
    if message.from_user.username and message.from_user.username.lower() == MANAGER_USERNAME.lower():
        manager_active = True
        manager_chat_id = message.from_user.id

        # Сохраняем состояние
        state["manager_active"] = True
        state["manager_chat_id"] = manager_chat_id
        save_state(state)

        await message.answer(
            "🔐 <b>Панель управления менеджера</b>\n\n"
            "✅ <b>Вы активированы как менеджер!</b>\n\n"
            "📨 <b>Функции:</b>\n"
            "• Все сообщения от пользователей пересылаются вам\n"
            "• Вы видите username и ID каждого пользователя\n"
            "• Чтобы ответить - просто ответьте на сообщение\n"
            "• Используйте /status для проверки состояния\n\n"
            "📊 <b>Статус:</b> Бот работает нормально",
            reply_markup=ReplyKeyboardRemove()
        )
        logger.info(f"✅ Менеджер @{MANAGER_USERNAME} активирован! Chat ID: {manager_chat_id}")
    else:
        # Обычный пользователь - НЕ ПОКАЗЫВАЕМ USERNAME МЕНЕДЖЕРА!
        if manager_active:
            status = "✅ поддержка онлайн и готова принять ваш запрос"
        else:
            status = "⏳ поддержка временно недоступна, но ваше сообщение будет сохранено"

        await message.answer(
            f"👋 <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
            f"📨 Я бот-посредник. Ваши сообщения будут пересылаться в службу поддержки.\n\n"
            f"📊 <b>Статус:</b> {status}\n\n"
            f"💬 Выберите действие на клавиатуре ниже или просто напишите ваш вопрос!",
            reply_markup=get_user_main_keyboard()
        )
        logger.info(f"👤 Пользователь {message.from_user.id} запустил бота")


# Обработчик текстовых сообщений с кнопками (только для пользователей, не менеджера)
@dp.message(F.text)
async def handle_user_buttons(message: Message):
    global manager_active, manager_chat_id

    # Игнорируем сообщения от менеджера (они пойдут в другой обработчик)
    if message.from_user.username and message.from_user.username.lower() == MANAGER_USERNAME.lower():
        return

    text = message.text

    # Обработка кнопок пользователя
    if text == "📝 Задать вопрос":
        await message.answer(
            "📝 <b>Задайте ваш вопрос</b>\n\n"
            "Напишите ваш вопрос в одном сообщении, и я передам его в поддержку.\n\n"
            "Вы можете отправить:\n"
            "• Текстовое сообщение\n"
            "• Фото с описанием\n"
            "• Видео\n"
            "• Документ\n"
            "• Голосовое сообщение",
            reply_markup=get_user_cancel_keyboard()
        )

    elif text == "📞 Связаться с поддержкой":
        await message.answer(
            "📞 <b>Связь с поддержкой</b>\n\n"
            "Выберите способ связи:",
            reply_markup=get_support_buttons()
        )

    elif text == "📊 Статус обращения":
        await message.answer(
            "📊 <b>Статус обращений</b>\n\n"
            f"👤 Ваш ID: <code>{message.from_user.id}</code>\n"
            f"📨 Статус поддержки: {'✅ онлайн' if manager_active else '⏳ офлайн'}\n\n"
            "Все ваши сообщения передаются в поддержку. Ответ придет в этот чат.",
            reply_markup=get_user_back_keyboard()
        )

    elif text == "ℹ️ О боте":
        await message.answer(
            "ℹ️ <b>О боте-посреднике</b>\n\n"
            "🤖 Версия: 2.0\n"
            "📅 Дата создания: 2026\n\n"
            "<b>Возможности:</b>\n"
            "• Анонимная связь с поддержкой\n"
            "• Пересылка текста, фото, видео\n"
            "• Сохранение сообщений при офлайн\n"
            "• Быстрые кнопки для удобства\n\n"
            "📞 По техническим вопросам обращайтесь в поддержку.",
            reply_markup=get_user_back_keyboard()
        )

    elif text == "❌ Отменить":
        await message.answer(
            "❌ Действие отменено. Возвращаю в главное меню.",
            reply_markup=get_user_main_keyboard()
        )

    elif text == "🔙 Назад в меню":
        if manager_active:
            status = "поддержка онлайн"
        else:
            status = "поддержка офлайн"

        await message.answer(
            f"🔙 <b>Главное меню</b>\n\n"
            f"📊 Статус: {status}\n\n"
            f"Выберите действие:",
            reply_markup=get_user_main_keyboard()
        )

    else:
        # Если это не кнопка, значит пользователь пишет сообщение - пересылаем менеджеру
        await forward_to_manager_logic(message)


# ============================================
# ОБРАБОТЧИКИ INLINE КНОПОК
# ============================================

@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    await callback.answer()

    if callback.data == "send_message":
        await callback.message.edit_text(
            "📧 <b>Отправка сообщения</b>\n\n"
            "Напишите ваше сообщение, и я передам его в поддержку.\n\n"
            "Вы можете отправить текст, фото, видео или документ.",
            reply_markup=None
        )
        await callback.message.answer(
            "✏️ Введите ваше сообщение:",
            reply_markup=get_user_cancel_keyboard()
        )

    elif callback.data == "faq":
        await callback.message.edit_text(
            "📋 <b>Часто задаваемые вопросы</b>\n\n"
            "Выберите интересующий вас вопрос:",
            reply_markup=get_faq_buttons()
        )

    elif callback.data == "urgent":
        if manager_active:
            # Отправляем срочное уведомление менеджеру (с username пользователя!)
            user_username = f"@{callback.from_user.username}" if callback.from_user.username else "нет username"
            urgent_text = (
                f"🚨 <b>СРОЧНОЕ ОБРАЩЕНИЕ!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 ID: <code>{callback.from_user.id}</code>\n"
                f"👤 Имя: {callback.from_user.full_name}\n"
                f"🔗 Username: {user_username}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Пользователь запросил срочную связь!"
            )

            target_chat = manager_chat_id if manager_chat_id else MANAGER_USERNAME
            await bot.send_message(
                chat_id=target_chat,
                text=urgent_text,
                parse_mode=ParseMode.HTML
            )

            await callback.message.edit_text(
                "📞 <b>Запрос на срочную связь отправлен!</b>\n\n"
                "Поддержка получила уведомление и свяжется с вами в ближайшее время.",
                reply_markup=get_user_back_keyboard()
            )
        else:
            await callback.message.edit_text(
                "⚠️ <b>Поддержка временно недоступна</b>\n\n"
                "Ваш запрос сохранен и будет обработан, когда поддержка вернется онлайн.",
                reply_markup=get_user_back_keyboard()
            )

    elif callback.data == "faq_how":
        await callback.message.edit_text(
            "❓ <b>Как работает бот?</b>\n\n"
            "1. Вы отправляете сообщение\n"
            "2. Бот анонимно пересылает его в поддержку\n"
            "3. Поддержка отвечает вам в этот же чат\n\n"
            "Все сообщения сохраняются и будут доставлены даже если поддержка офлайн.",
            reply_markup=get_faq_buttons()
        )

    elif callback.data == "faq_time":
        await callback.message.edit_text(
            "⏱ <b>Время ответа</b>\n\n"
            "🟢 Онлайн: ответ в течение 5-15 минут\n"
            "🟡 Офлайн: ответ при возобновлении работы\n\n"
            "Статус поддержки отображается в главном меню.",
            reply_markup=get_faq_buttons()
        )

    elif callback.data == "faq_contacts":
        await callback.message.edit_text(
            "📱 <b>Контакты</b>\n\n"
            "Для связи с поддержкой используйте:\n"
            "• Кнопку '📝 Задать вопрос'\n"
            "• Кнопку '📞 Связаться с поддержкой'\n"
            "• Напишите сообщение в этот чат\n\n"
            "Мы всегда рады помочь!",
            reply_markup=get_faq_buttons()
        )

    elif callback.data == "back_to_support":
        await callback.message.edit_text(
            "📞 <b>Связь с поддержкой</b>\n\n"
            "Выберите способ связи:",
            reply_markup=get_support_buttons()
        )


# ============================================
# ЛОГИКА ПЕРЕСЫЛКИ СООБЩЕНИЙ МЕНЕДЖЕРУ
# ============================================

async def forward_to_manager_logic(message: Message):
    global manager_active, manager_chat_id

    logger.info(f"📨 Получено сообщение от пользователя {message.from_user.id} - тип: {message.content_type}")

    try:
        # Формируем информацию о пользователе ДЛЯ МЕНЕДЖЕРА (с username!)
        user_display_name = message.from_user.full_name if message.from_user.full_name else "Неизвестно"
        user_username = f"@{message.from_user.username}" if message.from_user.username else "нет username"

        user_info = (
            f"📬 <b>Новое сообщение от пользователя</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
            f"👤 <b>Имя:</b> {user_display_name}\n"
            f"🔗 <b>Username:</b> {user_username}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        # Если менеджер не активен, сохраняем сообщение в "очередь"
        if not manager_active:
            await message.answer(
                "📝 <b>Ваше сообщение сохранено</b>\n\n"
                "Поддержка временно недоступна, но ваше сообщение будет доставлено, "
                "как только поддержка вернется онлайн.\n\n"
                "Спасибо за ожидание!",
                reply_markup=get_user_main_keyboard()
            )
            logger.info(f"Сообщение от пользователя {message.from_user.id} сохранено (менеджер не активен)")
            return

        # Отправляем менеджеру
        target_chat = manager_chat_id if manager_chat_id else MANAGER_USERNAME

        # Текстовое сообщение
        if message.text:
            await bot.send_message(
                chat_id=target_chat,
                text=f"{user_info}<b>📄 Текст сообщения:</b>\n{message.text}",
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                "✅ <b>Сообщение отправлено!</b>\n\n"
                "Поддержка получила ваше сообщение и ответит в ближайшее время.",
                reply_markup=get_user_main_keyboard()
            )

        # Фото
        elif message.photo:
            caption = f"{user_info}<b>📸 Фото</b>"
            if message.caption:
                caption += f"\n\n<b>Подпись:</b> {message.caption}"

            await bot.send_photo(
                chat_id=target_chat,
                photo=message.photo[-1].file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                "✅ <b>Фото отправлено!</b>\n\n"
                "Поддержка получила ваше фото и ответит в ближайшее время.",
                reply_markup=get_user_main_keyboard()
            )

        # Видео
        elif message.video:
            caption = f"{user_info}<b>🎥 Видео</b>"
            if message.caption:
                caption += f"\n\n<b>Подпись:</b> {message.caption}"

            await bot.send_video(
                chat_id=target_chat,
                video=message.video.file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                "✅ <b>Видео отправлено!</b>\n\n"
                "Поддержка получила ваше видео и ответит в ближайшее время.",
                reply_markup=get_user_main_keyboard()
            )

        # Документ
        elif message.document:
            caption = f"{user_info}<b>📎 Документ</b>"
            if message.caption:
                caption += f"\n\n<b>Подпись:</b> {message.caption}"

            await bot.send_document(
                chat_id=target_chat,
                document=message.document.file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                "✅ <b>Документ отправлен!</b>\n\n"
                "Поддержка получила ваш документ и ответит в ближайшее время.",
                reply_markup=get_user_main_keyboard()
            )

        # Голосовое сообщение
        elif message.voice:
            await bot.send_voice(
                chat_id=target_chat,
                voice=message.voice.file_id,
                caption=f"{user_info}<b>🎤 Голосовое сообщение</b>",
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                "✅ <b>Голосовое сообщение отправлено!</b>\n\n"
                "Поддержка получила ваше сообщение и ответит в ближайшее время.",
                reply_markup=get_user_main_keyboard()
            )

        # Стикер
        elif message.sticker:
            await bot.send_sticker(
                chat_id=target_chat,
                sticker=message.sticker.file_id
            )
            await bot.send_message(
                chat_id=target_chat,
                text=f"{user_info}<b>🎯 Стикер</b>",
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                "✅ <b>Стикер отправлен!</b>\n\n"
                "Поддержка получила ваш стикер.",
                reply_markup=get_user_main_keyboard()
            )

        # Неподдерживаемый тип
        else:
            await message.answer(
                "❌ <b>Извините, этот тип сообщений пока не поддерживается.</b>\n\n"
                "Пожалуйста, используйте текст, фото, видео или документ.",
                reply_markup=get_user_main_keyboard()
            )
            return

        logger.info(f"✅ Сообщение успешно переслано менеджеру")

    except Exception as e:
        if "chat not found" in str(e).lower():
            manager_active = False
            manager_chat_id = None
            state["manager_active"] = False
            state["manager_chat_id"] = None
            save_state(state)

            await message.answer(
                "⚠️ <b>Поддержка временно недоступна</b>\n\n"
                "Ваше сообщение сохранено и будет доставлено, когда поддержка вернется в сеть.\n"
                "Спасибо за понимание!",
                reply_markup=get_user_main_keyboard()
            )
            logger.warning(f"Менеджер не найден, состояние сброшено")
        else:
            logger.error(f"❌ Ошибка при отправке: {e}", exc_info=True)
            await message.answer(
                "❌ <b>Произошла ошибка при отправке</b>\n\n"
                "Пожалуйста, попробуйте позже или используйте другой способ связи.",
                reply_markup=get_user_main_keyboard()
            )


# ============================================
# ОБРАБОТЧИК ДЛЯ ОТВЕТОВ МЕНЕДЖЕРА
# ============================================
# Этот обработчик должен быть расположен ДО общего обработчика всех сообщений,
# чтобы сообщения менеджера обрабатывались здесь, а не попадали в forward_any_message.

@dp.message()
async def manager_reply_to_user(message: Message):
    global manager_chat_id

    # Проверяем, что сообщение от менеджера
    if not (message.from_user.username and message.from_user.username.lower() == MANAGER_USERNAME.lower()):
        return  # не менеджер - выходим, далее сработает другой обработчик

    # Обновляем chat_id менеджера
    if message.from_user.id != manager_chat_id:
        manager_chat_id = message.from_user.id
        state["manager_chat_id"] = manager_chat_id
        save_state(state)
        logger.info(f"Chat ID менеджера обновлен: {manager_chat_id}")

    # Если это ответ на сообщение
    if message.reply_to_message:
        logger.info(f"📝 Менеджер отвечает на сообщение")

        try:
            # Получаем текст оригинального сообщения
            original_text = ""
            if message.reply_to_message.text:
                original_text = message.reply_to_message.text
            elif message.reply_to_message.caption:
                original_text = message.reply_to_message.caption

            # Ищем ID пользователя
            user_id_match = re.search(r"ID: (\d+)", original_text) if original_text else None
            user_id_match_alt = re.search(r"ID:</b> <code>(\d+)", original_text) if original_text else None

            user_id = None
            if user_id_match:
                user_id = int(user_id_match.group(1))
            elif user_id_match_alt:
                user_id = int(user_id_match_alt.group(1))

            if user_id:
                # Отправляем ответ пользователю (БЕЗ УПОМИНАНИЯ МЕНЕДЖЕРА!)
                await bot.send_message(
                    chat_id=user_id,
                    text=f"📬 <b>Ответ от поддержки:</b>\n\n{message.text}",
                    parse_mode=ParseMode.HTML
                )

                # Подтверждение менеджеру
                await message.reply("✅ Ответ успешно отправлен пользователю!")
                logger.info(f"✅ Ответ отправлен пользователю {user_id}")
            else:
                await message.reply(
                    "❌ Не удалось найти ID пользователя.\n"
                    "Убедитесь, что вы отвечаете на пересланное сообщение от пользователя."
                )

        except Exception as e:
            logger.error(f"❌ Ошибка при ответе пользователю: {e}", exc_info=True)
            await message.reply("❌ Не удалось отправить ответ пользователю.")

    # Если менеджер пишет не в ответ на сообщение
    else:
        await message.reply(
            "ℹ️ Чтобы ответить пользователю, используйте 'ответ' (reply) на его сообщение."
        )


# Обработчик для пересылки любых сообщений от пользователей (не менеджеров)
@dp.message()
async def forward_any_message(message: Message):
    # Проверяем, что сообщение НЕ от менеджера
    if message.from_user.username and message.from_user.username.lower() == MANAGER_USERNAME.lower():
        return  # это менеджер, уже обработан выше

    await forward_to_manager_logic(message)


# Обработчик команды /status (только для менеджера)
@dp.message(Command("status"))
async def cmd_status(message: Message):
    if message.from_user.username and message.from_user.username.lower() == MANAGER_USERNAME.lower():
        status_text = "✅ активен" if manager_active else "❌ не активен"
        await message.answer(
            f"📊 <b>Статус бота</b>\n\n"
            f"👤 Менеджер: @{MANAGER_USERNAME} ({status_text})\n"
            f"🆔 Chat ID: <code>{manager_chat_id if manager_chat_id else 'не определен'}</code>\n"
            f"🤖 Бот работает нормально\n\n"
            f"📨 Ожидаю сообщения от пользователей..."
        )
    else:
        await message.answer("⛔ Эта команда только для менеджера.")


# ============================================
# ЗАПУСК БОТА
# ============================================

async def main():
    global manager_active, manager_chat_id

    try:
        # Проверяем подключение к Telegram
        me = await bot.get_me()

        print("\n" + "=" * 60)
        print(f"✅ БОТ УСПЕШНО ЗАПУЩЕН!")
        print("=" * 60)
        print(f"🤖 Имя бота: @{me.username}")
        print(f"🆔 ID бота: {me.id}")
        print(f"👤 Менеджер: @{MANAGER_USERNAME} (username скрыт от пользователей)")
        print(f"📊 Статус менеджера: {'✅ активен' if manager_active else '⏳ не активен'}")
        if manager_chat_id:
            print(f"🆔 Chat ID менеджера: {manager_chat_id}")
        print("=" * 60)
        print("\n⚠️  ВАЖНО:")
        if not manager_active:
            print("👉 Менеджер @SSQLGF должен написать боту команду /start")
        print("📝 Бот ожидает сообщения от пользователей...")
        print("🔍 Для остановки нажми Ctrl+C")
        print("=" * 60)

        # Запускаем поллинг
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        print("\n" + "=" * 60)
        print("❌ НЕ УДАЛОСЬ ЗАПУСТИТЬ БОТА!")
        print("=" * 60)
        print("Возможные причины:")
        print("1. Неправильный токен - получи новый у @BotFather")
        print("2. Проблемы с интернетом")
        print("3. Блокировка Telegram")
        print("=" * 60)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":  # исправлено: __name__ и "__main__"

    asyncio.run(main())
