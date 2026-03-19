"""
Security Best Practices for TON AI Trading Bot

## 1. Private Key Management

❌ NEVER:
- Commit .env file to git
- Share your mnemonic phrase
- Use your main wallet
- Store keys in code
- Log private keys

✅ ALWAYS:
- Use .env for secrets
- Create separate test wallet
- Keep .env in .gitignore
- Use environment variables
- Rotate keys regularly

## 2. API Key Security

- Store Anthropic API key in .env
- Don't share API keys
- Monitor API usage
- Set spending limits
- Revoke compromised keys immediately

## 3. Transaction Safety

- Start with small amounts (1-2 TON)
- Test on testnet first (if available)
- Verify transaction details before signing
- Use slippage protection
- Set maximum trade limits

## 4. Code Security

- Review all code before running
- Don't run untrusted scripts
- Keep dependencies updated
- Use virtual environment
- Scan for vulnerabilities

## 5. Network Security

- Use secure RPC endpoints
- Verify SSL certificates
- Don't use public WiFi for trading
- Use VPN if needed
- Monitor for suspicious activity

## 6. Operational Security

- Keep logs private
- Don't share trade history publicly
- Monitor wallet activity
- Set up alerts for large transactions
- Have emergency stop mechanism

## 7. Smart Contract Interaction

- Verify contract addresses
- Check contract source code
- Understand what you're signing
- Use established DEXes only
- Be aware of approval scams

## 8. Backup & Recovery

- Backup mnemonic phrase securely (offline)
- Store in multiple secure locations
- Never store digitally unencrypted
- Test recovery process
- Have contingency plan

## 9. Monitoring

- Check bot logs regularly
- Monitor wallet balance
- Track unusual activity
- Set up alerts
- Review trade history

## 10. Emergency Procedures

If compromised:
1. Stop the bot immediately
2. Transfer funds to secure wallet
3. Revoke all API keys
4. Change all passwords
5. Investigate the breach
6. Report if necessary

## Red Flags

⚠️ Stop immediately if:
- Unexpected transactions
- Unusual API calls
- Balance discrepancies
- Unknown contract interactions
- Suspicious log entries

## Resources

- TON Security: https://ton.org/security
- Anthropic Security: https://docs.anthropic.com/security
- Crypto Security Guide: https://www.coinbase.com/learn/crypto-basics/how-to-secure-crypto

---

Remember: Security is not a one-time setup, it's an ongoing process.
