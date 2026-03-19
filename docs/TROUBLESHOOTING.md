"""
Troubleshooting Guide

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
- Check DEX status pages

### 4. Wallet Issues

#### Problem: "Insufficient balance"

Solution:
- Check wallet balance: `python check_balance.py`
- Transfer more TON to wallet
- Ensure minimum 0.5 TON for gas fees

#### Problem: "Transaction failed"

Solution:
- Check you have enough TON for gas
- Verify network isn't congested
- Try with smaller amount
- Check transaction on explorer

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

#### Problem: "Trade simulation only"

Note: Current version simulates trades. To implement real trades:
- See docs/dedust_integration.txt
- See docs/stonfi_integration.txt
- Requires additional implementation

#### Problem: "DEX not responding"

Solution:
- Check DEX is operational
- Try alternative DEX
- Wait and retry
- Check DEX status page

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
- Check DEX APIs are accessible
- Verify API endpoints in config.py
- Try again later
- Check API documentation for changes

#### Problem: "Trade history not saving"

Solution:
- Check file permissions
- Verify disk space
- Check trades.json isn't corrupted
- Restart bot

### 9. Logging Issues

#### Problem: No logs appearing

Solution:
- Check console output
- Verify Python isn't buffering output
- Run with: `python -u main.py`
- Check log file permissions

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

Test setup:
```bash
python test_setup.py
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
python test_setup.py
```

---

Still having issues? Create an issue on GitHub with details.
