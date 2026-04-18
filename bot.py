"""
MEXC TradingView Webhook Bot
Author: Sultan Alkhamash
License: MIT
"""

import os
import time
import hmac
import hashlib
import logging
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MEXC_API_KEY")
SECRET_KEY = os.getenv("MEXC_SECRET_KEY")
BASE_URL = os.getenv("MEXC_BASE_URL", "https://futures.mexc.com")
DEFAULT_SYMBOL = os.getenv("DEFAULT_SYMBOL", "BNB_USDT")
DEFAULT_LEVERAGE = int(os.getenv("DEFAULT_LEVERAGE", "5"))
DEFAULT_VOLUME = os.getenv("DEFAULT_VOLUME", "1")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "5000"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

if not API_KEY or not SECRET_KEY:
    raise EnvironmentError(
        "Missing MEXC_API_KEY or MEXC_SECRET_KEY. "
        "Please copy .env.example to .env and fill in your credentials."
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def sign_request(params: dict, secret: str) -> str:
    """Generate HMAC SHA256 signature for MEXC API requests."""
    query = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(
        secret.encode(),
        query.encode(),
        hashlib.sha256
    ).hexdigest()


def place_order(symbol: str, side: int, leverage: int = None, volume: str = None) -> dict:
    """Place a futures order on MEXC."""
    leverage = leverage or DEFAULT_LEVERAGE
    volume = volume or DEFAULT_VOLUME

    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "5",
        "leverage": leverage,
        "openType": "1",
        "vol": volume,
        "timestamp": timestamp,
        "api_key": API_KEY
    }
    params["sign"] = sign_request(params, SECRET_KEY)

    headers = {
        "Content-Type": "application/json",
        "ApiKey": API_KEY
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/private/order/submit",
            json=params,
            headers=headers,
            timeout=10
        )
        result = response.json()
        logger.info(f"Order placed: symbol={symbol} side={side} result={result}")
        return result
    except requests.RequestException as e:
        logger.error(f"Order request failed: {e}")
        return {"error": str(e)}


@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive trading signals from TradingView alerts."""
    data = request.get_json(silent=True)

    if not data:
        logger.warning("Received empty or invalid payload")
        return jsonify({"error": "No data received"}), 400

    logger.info(f"Webhook received: {data}")

    if WEBHOOK_SECRET:
        if data.get("secret") != WEBHOOK_SECRET:
            logger.warning("Unauthorized webhook attempt")
            return jsonify({"error": "Unauthorized"}), 401

    action = data.get("action", "").lower()
    symbol = data.get("symbol", DEFAULT_SYMBOL)

    action_map = {
        "buy": 1,
        "sell": 3,
        "close_long": 4,
        "close_short": 2,
    }

    if action not in action_map:
        logger.warning(f"Unknown action received: {action}")
        return jsonify({"error": f"Unknown action: {action}"}), 400

    result = place_order(symbol, side=action_map[action])
    return jsonify({"status": "ok", "result": result})


@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "running", "service": "mexc-webhook-bot"})


@app.route("/", methods=["GET"])
def index():
    """Root endpoint."""
    return jsonify({
        "service": "MEXC TradingView Webhook Bot",
        "endpoints": {
            "/webhook": "POST - Receive TradingView alerts",
            "/health": "GET - Health check"
        }
    })


if __name__ == "__main__":
    logger.info(f"Starting MEXC Webhook Bot on port {WEBHOOK_PORT}")
    app.run(host="0.0.0.0", port=WEBHOOK_PORT, debug=False)
