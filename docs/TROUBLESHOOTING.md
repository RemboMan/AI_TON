# Troubleshooting Guide

## Common Issues and Solutions

### 1. Installation Issues

#### Problem: pip install fails
```
ERROR: Could not find a version that satisfies the requirement pytoniq
```

Solution:
- Update pip: `python -m pip install --upgrade pip`
- Try with specific version: `pip install pytoniq==0.1.38`
- Check Python version (need 3.8+): `python --version`

#### Problem: Virtual environment not activating

Windows:
```bash
venv\Scripts\activate.bat
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 2. Configuration Issues

#### Problem: "WALLET_MNEMONIC not configured"

Solution:
- Create .env file: `cp .env.example .env`
- Edit .env and add your 24-word mnemonic
- Make sure there are no extra spaces or quotes

#### Problem: "Invalid mnemonic phrase"

Solution:
- Check you have exactly 24 words
- Verify words are separated by single spaces
- Ensure no trailing spaces
- Words should be lowercase

### 3. Connection Issues

#### Problem: "Failed to connect to TON network"

Solution:
- Check internet connection
- Try again (network might be temporarily down)
- Verify firewall isn't blocking connections
- Check if TON network is operational

#### Problem: "API request failed"

Solution:
- Check API endpoints are accessible
- Verify no rate limiting
- Try again after a few minutes
- Check DeDust status

### 4. Wallet Issues

#### Problem: "Insufficient balance"

Solution:
- Check wallet balance: `python check_balance.py`
- Transfer more TON to wallet
- Ensure minimum 0.5 TON for gas fees

#### Problem: "Transaction failed"

Solution:
- Check you have enough TON for gas (0.3 TON per transaction)
- Verify network isn't congested
- Try with smaller amount
- Check transaction on tonscan.org

### 5. AI Issues

#### Problem: "AI decision error"

Solution:
- Verify ANTHROPIC_API_KEY is correct
- Check API key has credits
- Check internet connection
- Review error message for details

#### Problem: "Invalid JSON response from AI"

Solution:
- This is usually temporary
- Bot will retry on next cycle
- Check AI prompt isn't too complex
- Verify model is available

### 6. Trading Issues

#### Problem: "Pool address not found"

Solution:
- Token doesn't have a DeDust pool
- Check DeDust API for pool availability
- Add pool address to KNOWN_POOLS in dex_handler.py
- Or use a different token

#### Problem: "Reserve query failed"

Solution:
- Pool contract might be busy
- Bot will use min_out = 1 as fallback
- Transaction will still work but with less slippage protection
- Try again on next cycle

#### Problem: "Slippage too high"

Solution:
- Market is volatile
- Try smaller trade amount
- Wait for better market conditions
- Check pool liquidity

### 7. Performance Issues

#### Problem: Bot is slow

Solution:
- Check internet speed
- Reduce CHECK_INTERVAL if too frequent
- Check system resources
- Close other applications

#### Problem: High API costs

Solution:
- Increase CHECK_INTERVAL
- Reduce max_tokens in AI calls
- Monitor API usage dashboard
- Set spending limits

### 8. Data Issues

#### Problem: "No market data available"

Solution:
- Check DeDust API is accessible
- Verify API endpoint in config.py
- Try again later
- Check API documentation for changes

#### Problem: "Trade history not saving"

Solution:
- Check file permissions
- Verify disk space
- Check trades.json isn't corrupted
- Restart bot

### 9. Token Issues

#### Problem: "Token balance not showing"

Solution:
- Token might not be in your wallet yet
- Check transaction completed on tonscan.org
- Wait a few seconds and check again
- Verify token address is correct

#### Problem: "Cannot sell token"

Solution:
- Check you have enough tokens to sell
- Verify token has DeDust pool
- Check pool has enough liquidity
- Try smaller amount

### 10. General Debugging

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check bot status:
```bash
python cli.py balance
python cli.py markets
python cli.py trades
```

## Getting Help

If issue persists:
1. Check error logs carefully
2. Search existing GitHub issues
3. Create new issue with:
   - Error message
   - Steps to reproduce
   - System info (OS, Python version)
   - Relevant logs (remove sensitive data!)

## Emergency Stop

To stop bot immediately:
- Press Ctrl+C
- Or close terminal
- Bot will cleanup gracefully

## Reset Everything

If all else fails:
```bash
# Backup your .env first!
rm -rf venv/
rm trades.json
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python check_balance.py
```

---

Still having issues? Create an issue on GitHub with details.
