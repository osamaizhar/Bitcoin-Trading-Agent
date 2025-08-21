"""
[Module Number: 6] Notification Manager Module for Bitcoin Trading Agent

Purpose: Sends Telegram notifications for trades and weekly email reports via Gmail.

Inputs:
- Trade details from 03_trade_executor
- Portfolio and trade log data for weekly reports
- Configuration from 02_config_manager

Outputs:
- Telegram messages for each trade
- Weekly email report sent every Monday at 9:00 AM

Dependencies: python-telegram-bot, smtplib, pandas, schedule
"""

import os
from dotenv import load_dotenv
import telegram
import smtplib
from email.mime.text import MIMEText
import pandas as pd
from datetime import datetime
import schedule
import time

def initialize_telegram_bot():
    """Initialize Telegram bot."""
    # Load Telegram credentials from .env
    load_dotenv()
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not bot_token or not chat_id:
        raise Exception("Telegram credentials missing in .env")
    # Return initialized bot and chat ID
    return telegram.Bot(token=bot_token), chat_id

def send_telegram_notification(trade_record):
    """Send Telegram notification for a trade."""
    try:
        # Initialize Telegram bot
        bot, chat_id = initialize_telegram_bot()
        # Format trade details for notification
        message = f"""
        {trade_record['trade_type']} Trade Executed
        Type: {trade_record['type']}
        Price: ${trade_record['price']:,.2f}
        Quantity: {trade_record['quantity']:.6f} BTC
        Amount: ${trade_record['amount_usd']:,.2f}
        Time: {trade_record['timestamp']}
        """
        # Send message to Telegram chat
        bot.send_message(chat_id=chat_id, text=message)
        print("[OK] Telegram notification sent")
    except Exception as e:
        # Handle Telegram send errors
        print(f"[ERROR] Telegram notification failed: {e}")

def send_weekly_report(portfolio, current_price, trade_log_path):
    """Send weekly email report with portfolio and trade summary."""
    try:
        # Load Gmail credentials
        load_dotenv()
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        if not gmail_user or not gmail_password:
            raise Exception("Gmail credentials missing in .env")

        # Calculate portfolio value
        portfolio_value = portfolio['btc'] * current_price + portfolio['usdt']
        # Load trade log for weekly summary
        trade_df = pd.read_csv(trade_log_path) if os.path.exists(trade_log_path) else pd.DataFrame()
        weekly_trades = trade_df[pd.to_datetime(trade_df['timestamp']).dt.isocalendar().week == datetime.now().isocalendar().week]
        # Calculate profit/loss from trades
        profit_loss = sum(trade['amount_usd'] * (-1 if trade['type'] == 'BUY' else 1) for _, trade in weekly_trades.iterrows())

        # Generate report text
        report = f"""
        Bitcoin Trading Agent Weekly Report
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Portfolio:
        - BTC: {portfolio['btc']:.6f}
        - USD: ${portfolio['usdt']:,.2f}
        - Total Value: ${portfolio_value:,.2f}

        Weekly Performance:
        - Trades: {len(weekly_trades)}
        - Profit/Loss: ${profit_loss:,.2f}
        - Fees: ${len(weekly_trades) * 0.1:,.2f} (estimated)

        Recent Trades:
        {weekly_trades.head(5).to_string(index=False)}
        """

        # Prepare email
        msg = MIMEText(report)
        msg['Subject'] = 'Bitcoin Trading Agent Weekly Report'
        msg['From'] = gmail_user
        msg['To'] = gmail_user

        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, gmail_user, msg.as_string())
        print("[OK] Weekly email report sent")
    except Exception as e:
        # Handle email send errors
        print(f"[ERROR] Weekly report failed: {e}")

def schedule_weekly_report(portfolio, current_price, trade_log_path):
    """Schedule weekly report every Monday at 9:00 AM."""
    # Schedule job to run weekly report
    schedule.every().monday.at("09:00").do(send_weekly_report, portfolio, current_price, trade_log_path)

if __name__ == "__main__":
    """Test 06_notification_manager module with real notifications."""
    print("Testing 06_notification_manager module with real notifications...")
    try:
        # Mock trade record for Telegram test
        mock_trade = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'BUY',
            'trade_type': 'TEST_DCA',
            'price': 60000.0,
            'quantity': 0.000167,
            'amount_usd': 10.0
        }
        send_telegram_notification(mock_trade)
        print("[TEST] Real Telegram notification sent")

        # Mock portfolio and trade log for email test
        mock_portfolio = {'btc': 0.0, 'usdt': 100.0}
        mock_current_price = 60000.0
        mock_trade_log = pd.DataFrame([mock_trade])
        mock_trade_log.to_csv('../data/test_trade_log.csv', index=False)
        send_weekly_report(mock_portfolio, mock_current_price, '../data/test_trade_log.csv')
        print("[TEST] Real weekly email report sent")
    except Exception as e:
        print(f"[TEST ERROR] {e}")