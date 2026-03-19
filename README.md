# TON AI Trading Bot

🤖 Автономный AI-бот для торговли токенами в TON экосистеме

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ⚠️ ВНИМАНИЕ

Это **экспериментальный проект** для образовательных целей. Используйте только средства, которые готовы потерять полностью. Автор не несет ответственности за финансовые потери.

## 🎯 Возможности

- 🤖 **AI-управление**: Claude Sonnet 4.5 принимает торговые решения
- 💱 **DEX интеграция**: Реальные swap на STON.fi, поддержка DeDust
- 📊 **Мониторинг рынка**: Реальные данные с DEX
- 📝 **История сделок**: Полное логирование всех операций
- 🔧 **Настраиваемость**: Гибкие параметры торговли
- 🛡️ **Безопасность**: Режим симуляции по умолчанию, приватные ключи в .env
- ⚡ **Kiro.cheap API**: Быстрый доступ к Claude через оптимизированный endpoint

## 🚀 Быстрый старт

### 1. Установка

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
bash install.sh
```

### 2. Настройка

Создайте `.env` файл:
```bash
cp .env.example .env
```

Заполните:
- `WALLET_MNEMONIC` - 24 слова seed-фразы
- `ANTHROPIC_API_KEY` - API ключ от Kiro.cheap (sk-aw-...)
- `ENABLE_REAL_TRADING` - false (симуляция) или true (реальные сделки)

### 3. Проверка

```bash
python test_setup.py
```

### 4. Запуск

```bash
python main.py
```

## 📁 Структура проекта

```
AI_TON/
├── main.py              # Основной цикл бота
├── wallet.py            # TON кошелек
├── ai_trader.py         # AI логика
├── market_data.py       # Данные с DEX
├── dex_handler.py       # Выполнение сделок
├── config.py            # Конфигурация
├── trade_logger.py      # Логирование
├── cli.py               # CLI интерфейс
├── test_setup.py        # Проверка настройки
├── test_trading.py      # Тест торговли
├── check_balance.py     # Проверка баланса
├── view_markets.py      # Просмотр рынков
├── requirements.txt     # Зависимости
└── .env.example         # Пример конфигурации
```

## 🛠️ Команды CLI

```bash
python cli.py balance    # Показать баланс
python cli.py markets    # Показать рынки
python cli.py trades     # История сделок
python cli.py run        # Запустить бота
```

## ⚙️ Настройки

В `.env` файле:

```env
# AI Configuration
ANTHROPIC_API_KEY=sk-aw-your_key_here
ANTHROPIC_BASE_URL=https://api.kiro.cheap
ANTHROPIC_MODEL=claude-sonnet-4-5-20250514

# Trading Configuration
MIN_TRADE_AMOUNT=0.1          # Минимальная сумма сделки (TON)
MAX_TRADE_AMOUNT=1.0          # Максимальная сумма сделки (TON)
CHECK_INTERVAL=60             # Интервал проверки (секунды)
ENABLE_REAL_TRADING=false     # Реальная торговля (true/false)
```

⚠️ **ВАЖНО**: По умолчанию бот работает в режиме **симуляции**. Для реальных сделок установите `ENABLE_REAL_TRADING=true`

## 📊 Как это работает

1. **Подключение**: Бот подключается к TON сети и DEX API
2. **Анализ**: Получает данные о пулах ликвидности и ценах
3. **Решение**: AI анализирует рынок и принимает решение
4. **Исполнение**: Выполняет сделку на выбранном DEX
5. **Логирование**: Записывает результат в историю
6. **Повтор**: Ждет интервал и повторяет цикл

## 🔒 Безопасность

- ✅ Используйте **отдельный кошелек** для экспериментов
- ✅ Храните приватные ключи в `.env`
- ✅ Начинайте с **малых сумм** (1-2 TON)
- ✅ Мониторьте активность бота
- ✅ Добавьте `.env` в `.gitignore`

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE)

## ⚠️ Disclaimer

Этот проект предоставляется "как есть" без каких-либо гарантий. Криптовалютная торговля несет существенный риск потери средств. Автор не несет ответственности за любые финансовые потери, возникшие в результате использования этого ПО.

## 🔗 Ресурсы

- [TON Documentation](https://ton.org/docs)
- [DeDust Docs](https://docs.dedust.io)
- [STON.fi Docs](https://docs.ston.fi)
- [Anthropic API](https://docs.anthropic.com)
- [pytoniq](https://github.com/yungwine/pytoniq)

## 📈 Roadmap

- [x] Реализация реальных swap транзакций (STON.fi)
- [x] Интеграция с Kiro.cheap API
- [x] Режим симуляции для безопасного тестирования
- [ ] Больше торговых пар
- [ ] Jetton -> TON swaps
- [ ] Арбитраж между DEX
- [ ] Stop-loss / Take-profit
- [ ] Веб-интерфейс
- [ ] Telegram уведомления
- [ ] Backtesting
- [ ] Multi-wallet поддержка

---

**Сделано с ❤️ для TON экосистемы**

*Удачи в экспериментах! 🚀*
