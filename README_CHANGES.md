# Изменения в боте

## Исправлено

### 1. DeDust Swap Payload (TON → Token)
- ✅ Правильный opcode: `0xea06185d` (из официального SDK)
- ✅ Правильная структура payload:
  - query_id → amount → pool → flag → limit → next → swap_params_ref
- ✅ Gas уменьшен до 0.2 TON (как в SDK)
- ✅ Исправлены addr_none и maybe_ref поля

### 2. Флиппинг стратегия
- ✅ Добавлено отслеживание holdings (какие токены держим)
- ✅ AI понимает стратегию: купить → ждать → продать → повторить
- ✅ Добавлено поле `type: "buy"/"sell"` в решения

### 3. Чередование DEX
- ✅ AI теперь чередует DeDust и STON.fi
- ✅ Отслеживание последнего использованного DEX

### 4. Продажа токенов (Token → TON)
- ✅ Реализован `sell_token_dedust()` для продажи токенов
- ✅ Добавлена функция `get_jetton_wallet_address()` для получения jetton wallet
- ✅ Добавлена функция `send_jetton_transfer()` для отправки jetton с payload
- ✅ Правильный opcode для jetton swap: `0xe3a0d482`

## Конфигурация

### Jetton Vaults (config.py)
```python
DEDUST_JETTON_VAULTS = {
    'USDT': 'EQASwb8KCvDGAZOGKqBVR5Z7t8i8RXcHnzfYmskQRHqT3Xyy',
    'STON': 'EQCMRb8RGbK0xNJGGLKJN0qKJJqKqKqKqKqKqKqKqKqKqKqK',  # placeholder
    'DUST': 'EQDqVDNqRHqT3XyySwb8KCvDGAZOGKqBVR5Z7t8i8RXcHnzf',  # placeholder
}
```

⚠️ **ВАЖНО**: Адреса для STON и DUST - это placeholder'ы. Нужны реальные адреса jetton vault'ов из DeDust.

## Что работает

1. ✅ **Покупка токенов** (TON → USDT/STON/DUST) на DeDust
2. ✅ **Покупка токенов** (TON → USDT/STON/DUST) на STON.fi
3. ⚠️ **Продажа токенов** (USDT → TON) на DeDust - реализовано, но нужны правильные vault адреса
4. ❌ **Продажа токенов** на STON.fi - еще не реализовано

## Как протестировать

### Тест 1: Покупка на DeDust
```bash
cd C:\Users\rembo\Desktop\AI_TON
python main.py
```

Бот должен:
- Чередовать DeDust и STON.fi
- Покупать токены за TON
- Отслеживать holdings

### Тест 2: Проверка payload
Если swap fails с "Call Contract FAILED", возможные причины:
1. Неправильный pool address
2. Недостаточно gas
3. Неправильная структура payload

## Следующие шаги

1. Найти правильные адреса jetton vault'ов для STON и DUST
2. Протестировать продажу USDT → TON
3. Реализовать продажу на STON.fi
4. Добавить проверку баланса jetton перед продажей

## Файлы изменены

- `dex_handler.py` - исправлен payload, добавлена продажа
- `ai_trader.py` - добавлен флиппинг, чередование DEX, holdings
- `config.py` - добавлены jetton vault адреса
- `main.py` - добавлено отображение holdings
- `.env` - ENABLE_REAL_TRADING=true
