# MEXC TradingView Webhook Bot

A lightweight, production-ready Flask webhook server that connects TradingView alerts to MEXC Futures for automated cryptocurrency trading.

Built for traders who want to execute their Pine Script strategies automatically without manual intervention.

## Features

- Automated Order Execution — Receives TradingView alerts and places orders on MEXC Futures in milliseconds
- Secure Credential Management — API keys stored in environment variables, never in code
- Optional Webhook Authentication — Protect your endpoint with a secret token
- Comprehensive Logging — All trades and errors logged to file and console
- Multiple Order Types — Supports opening and closing both Long and Short positions
- Configurable — Symbol, leverage, volume, and port all customizable via .env
- Health Check Endpoint — Monitor bot status with a simple HTTP GET request

## Architecture

TradingView Alert → Flask Webhook → MEXC Futures API

## Requirements

- Python 3.8+
- A MEXC account with Futures API access
- A VPS or server with a public IP
- TradingView Pro plan or higher

## Installation

1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Copy .env.example to .env and fill in your MEXC API credentials
4. Run: python bot.py

## TradingView Alert Setup

Webhook URL: http://your-server-ip:5000/webhook

Message format:
{
  "action": "buy",
  "symbol": "BNB_USDT"
}

## Supported Actions

- buy: Open Long position
- sell: Open Short position
- close_long: Close Long position
- close_short: Close Short position

## API Endpoints

- POST /webhook: Receive trading signals from TradingView
- GET /health: Health check for monitoring
- GET /: Service info

## Security Best Practices

- Never commit your .env file — it contains your API keys
- Use a sub-account on MEXC with limited permissions
- Set a WEBHOOK_SECRET to prevent unauthorized access
- Enable IP whitelisting on MEXC

## Disclaimer

This software is provided for educational purposes. Cryptocurrency trading carries significant financial risk. Always test with small amounts before deploying with real capital.

## License

MIT License

## Author

Sultan Alkhamash
Flight Dispatcher & Self-taught Developer
Riyadh, Saudi Arabia

GitHub: @sulalkhamash1

If you find this project useful, please give it a star.
