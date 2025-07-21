"""
Bitcoin Trading Agent - Notifications Module

This module handles all notification systems:
- WhatsApp alerts via PyWhatKit
- Gmail email reports
- Telegram notifications (optional)
"""

import os
import time
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class WhatsAppNotifier:
    """WhatsApp notification system using PyWhatKit"""
    
    def __init__(self, phone_number="+923353015576"):
        self.phone_number = phone_number
        self.last_message_time = None
        self.rate_limit_seconds = 30  # Minimum time between messages
    
    def send_instant_message(self, message, wait_time=15):
        """Send WhatsApp message instantly"""
        try:
            import pywhatkit as kit
            
            # Rate limiting
            if self.last_message_time:
                time_diff = datetime.now() - self.last_message_time
                if time_diff.total_seconds() < self.rate_limit_seconds:
                    wait_seconds = self.rate_limit_seconds - time_diff.total_seconds()
                    logger.info(f"Rate limiting: waiting {wait_seconds:.0f}s")
                    time.sleep(wait_seconds)
            
            # Format message with timestamp
            timestamp = datetime.now().strftime('%H:%M:%S')
            formatted_message = f"🤖 BTC Bot Alert\\n{timestamp}\\n\\n{message}"
            
            # Send message
            kit.sendwhatmsg_instantly(
                phone_no=self.phone_number,
                message=formatted_message,
                wait_time=wait_time,
                tab_close=True,
                close_time=3
            )
            
            self.last_message_time = datetime.now()
            logger.info(f"WhatsApp message sent to {self.phone_number}")
            return True
            
        except ImportError:
            logger.error("PyWhatKit not installed")
            return False
        except Exception as e:
            logger.error(f"WhatsApp error: {e}")
            return False
    
    def send_trade_alert(self, trade_type, price, amount, reason, pnl=None):
        """Send formatted trade alert"""
        try:
            if trade_type == "DCA_BUY":
                message = (
                    f"🟢 DCA BUY EXECUTED\\n"
                    f"💰 ${amount:.2f} → {amount/price:.6f} BTC\\n"
                    f"📊 Price: ${price:,.2f}\\n"
                    f"📝 Reason: {reason}"
                )
            elif trade_type == "STOP_LOSS":
                pnl_emoji = "📈" if pnl and pnl > 0 else "📉"
                message = (
                    f"🔴 STOP-LOSS TRIGGERED\\n"
                    f"💸 Sold at ${price:,.2f}\\n"
                    f"{pnl_emoji} P&L: ${pnl:+.2f}\\n"
                    f"📝 {reason}"
                )
            elif trade_type == "ERROR":
                message = (
                    f"⚠️ SYSTEM ERROR\\n"
                    f"🚨 {reason}\\n"
                    f"🔧 Check logs for details"
                )
            elif trade_type == "STARTUP":
                message = (
                    f"🚀 BITCOIN BOT STARTED\\n"
                    f"💰 Budget: ${amount:,.2f}\\n"
                    f"📊 Current Price: ${price:,.2f}\\n"
                    f"⚙️ {reason}"
                )
            elif trade_type == "SHUTDOWN":
                message = (
                    f"🛑 BITCOIN BOT STOPPED\\n"
                    f"💼 Final Portfolio: ${amount:,.2f}\\n"
                    f"📊 Final Price: ${price:,.2f}\\n"
                    f"📝 {reason}"
                )
            else:
                message = f"📊 {trade_type}\\n💰 ${price:,.2f}\\n📝 {reason}"
            
            return self.send_instant_message(message)
            
        except Exception as e:
            logger.error(f"Trade alert error: {e}")
            return False
    
    def send_daily_summary(self, portfolio_value, day_pnl, trades_count, current_price):
        """Send daily portfolio summary"""
        try:
            pnl_emoji = "📈" if day_pnl >= 0 else "📉"
            message = (
                f"📊 DAILY SUMMARY\\n"
                f"💼 Portfolio: ${portfolio_value:,.2f}\\n"
                f"{pnl_emoji} Day P&L: ${day_pnl:+.2f}\\n"
                f"⚡ Trades: {trades_count}\\n"
                f"💰 BTC Price: ${current_price:,.2f}"
            )
            
            return self.send_instant_message(message)
            
        except Exception as e:
            logger.error(f"Daily summary error: {e}")
            return False
    
    def send_weekly_summary(self, portfolio_value, week_pnl, trades_count, current_price):
        """Send weekly portfolio summary"""
        try:
            pnl_emoji = "📈" if week_pnl >= 0 else "📉"
            date_str = datetime.now().strftime('%B %d, %Y')
            
            message = (
                f"📊 WEEKLY SUMMARY\\n"
                f"📅 {date_str}\\n"
                f"💼 Portfolio: ${portfolio_value:,.2f}\\n"
                f"{pnl_emoji} Week P&L: ${week_pnl:+.2f}\\n"
                f"⚡ Trades: {trades_count}\\n"
                f"💰 BTC Price: ${current_price:,.2f}"
            )
            
            return self.send_instant_message(message)
            
        except Exception as e:
            logger.error(f"Weekly summary error: {e}")
            return False


class GmailReporter:
    """Gmail email reporting system"""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv('GMAIL_EMAIL')
        self.password = os.getenv('GMAIL_APP_PASSWORD')
        self.configured = bool(self.email and self.password)
    
    def send_email(self, subject, body_html, to_email=None):
        """Send HTML email"""
        if not self.configured:
            logger.warning("Gmail not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email
            msg['To'] = to_email or self.email
            
            # Attach HTML content
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Email error: {e}")
            return False
    
    def generate_weekly_report_html(self, performance_data, trades_data, config_data):
        """Generate comprehensive HTML weekly report"""
        
        # Extract data with safe defaults
        portfolio = performance_data.get('portfolio', {})
        dca_perf = performance_data.get('dca_performance', {})
        atr_perf = performance_data.get('atr_performance', {})
        
        total_value = portfolio.get('total_value', 0)
        usd_balance = portfolio.get('usd_balance', 0)
        btc_balance = portfolio.get('btc_balance', 0)
        
        total_invested = dca_perf.get('total_invested', 0)
        total_btc = dca_perf.get('total_btc', 0)
        avg_buy_price = dca_perf.get('avg_buy_price', 0)
        dca_pnl = dca_perf.get('pnl', 0)
        
        active_positions = atr_perf.get('active_positions', 0)
        win_rate = atr_perf.get('win_rate', 0)
        total_trades = performance_data.get('total_trades', 0)
        
        current_price = performance_data.get('current_price', 0)
        report_date = datetime.now().strftime('%B %d, %Y')
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bitcoin Trading Bot - Weekly Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #f39c12, #e67e22);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.2em;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                .section {{
                    padding: 25px 30px;
                    border-bottom: 1px solid #eee;
                }}
                .section:last-child {{
                    border-bottom: none;
                }}
                .section h2 {{
                    color: #2c3e50;
                    margin-top: 0;
                    font-size: 1.4em;
                    border-bottom: 2px solid #f39c12;
                    padding-bottom: 10px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #f39c12;
                }}
                .metric-value {{
                    font-size: 1.5em;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 5px;
                }}
                .metric-label {{
                    font-size: 0.9em;
                    color: #7f8c8d;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
                .neutral {{ color: #95a5a6; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: 600;
                    color: #2c3e50;
                }}
                .trade-row:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                .footer {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 20px 30px;
                    text-align: center;
                    font-size: 0.9em;
                }}
                .status-indicator {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.8em;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .status-active {{ background-color: #2ecc71; color: white; }}
                .status-paper {{ background-color: #3498db; color: white; }}
                .status-paused {{ background-color: #f39c12; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Bitcoin Trading Bot</h1>
                    <p>Weekly Performance Report - {report_date}</p>
                </div>
                
                <div class="section">
                    <h2>💼 Portfolio Overview</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${total_value:,.2f}</div>
                            <div class="metric-label">Total Portfolio Value</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${usd_balance:,.2f}</div>
                            <div class="metric-label">USD Balance</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{btc_balance:.6f}</div>
                            <div class="metric-label">BTC Balance</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${current_price:,.2f}</div>
                            <div class="metric-label">Current BTC Price</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 DCA Strategy Performance</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">${total_invested:,.2f}</div>
                            <div class="metric-label">Total Invested</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{total_btc:.6f}</div>
                            <div class="metric-label">BTC Accumulated</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${avg_buy_price:,.2f}</div>
                            <div class="metric-label">Average Buy Price</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value {'positive' if dca_pnl >= 0 else 'negative'}">${dca_pnl:+,.2f}</div>
                            <div class="metric-label">Unrealized P&L</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>⚡ Trading Activity</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{total_trades}</div>
                            <div class="metric-label">Total Trades</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{active_positions}</div>
                            <div class="metric-label">Active Positions</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{win_rate:.1f}%</div>
                            <div class="metric-label">Win Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">
                                <span class="status-indicator status-{'active' if config_data.get('trading_mode', 'paper') == 'live' else 'paper'}">
                                    {config_data.get('trading_mode', 'paper').upper()}
                                </span>
                            </div>
                            <div class="metric-label">Trading Mode</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>⚙️ Strategy Configuration</h2>
                    <table>
                        <tr>
                            <th>Parameter</th>
                            <th>Current Value</th>
                        </tr>
                        <tr>
                            <td>DCA Trigger</td>
                            <td>{config_data.get('dca_percentage', 3):.1f}% price drop</td>
                        </tr>
                        <tr>
                            <td>ATR Stop-Loss Multiplier</td>
                            <td>{config_data.get('atr_multiplier', 1.5):.1f}x</td>
                        </tr>
                        <tr>
                            <td>Position Size</td>
                            <td>{config_data.get('position_size_pct', 2):.1f}% of budget</td>
                        </tr>
                        <tr>
                            <td>Maximum Drawdown</td>
                            <td>{config_data.get('max_drawdown', 25):.1f}%</td>
                        </tr>
                        <tr>
                            <td>Total Budget</td>
                            <td>${config_data.get('budget', 1000):,.2f}</td>
                        </tr>
                    </table>
                </div>
        """
        
        # Add recent trades section
        if trades_data and len(trades_data) > 0:
            html += """
                <div class="section">
                    <h2>🔄 Recent Trades</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Price</th>
                                <th>Amount (BTC)</th>
                                <th>Value (USD)</th>
                                <th>Reason</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Show last 10 trades
            recent_trades = trades_data[-10:] if len(trades_data) > 10 else trades_data
            
            for trade in recent_trades:
                trade_time = trade.get('timestamp', datetime.now())
                if isinstance(trade_time, str):
                    try:
                        trade_time = datetime.fromisoformat(trade_time.replace('Z', '+00:00'))
                    except:
                        trade_time = datetime.now()
                
                html += f"""
                        <tr class="trade-row">
                            <td>{trade_time.strftime('%m/%d %H:%M')}</td>
                            <td>{trade.get('type', 'UNKNOWN')}</td>
                            <td>${trade.get('price', 0):,.2f}</td>
                            <td>{trade.get('btc_amount', 0):.6f}</td>
                            <td>${trade.get('usd_amount', 0):,.2f}</td>
                            <td>{trade.get('trigger_reason', trade.get('reason', 'N/A'))}</td>
                        </tr>
                """
            
            html += """
                        </tbody>
                    </table>
                </div>
            """
        else:
            html += """
                <div class="section">
                    <h2>🔄 Recent Trades</h2>
                    <p style="text-align: center; color: #7f8c8d; font-style: italic;">
                        No trades executed this week.
                    </p>
                </div>
            """
        
        # Add footer
        html += f"""
                <div class="footer">
                    <p>🤖 Generated with Claude Code | Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>⚠️ This is an automated trading system. Past performance does not guarantee future results.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_weekly_report(self, performance_data, trades_data, config_data):
        """Send weekly performance report"""
        try:
            subject = f"🤖 Bitcoin Bot Weekly Report - {datetime.now().strftime('%B %d, %Y')}"
            html_body = self.generate_weekly_report_html(performance_data, trades_data, config_data)
            
            return self.send_email(subject, html_body)
            
        except Exception as e:
            logger.error(f"Weekly report error: {e}")
            return False
    
    def send_error_report(self, error_message, error_details=None):
        """Send error notification email"""
        try:
            subject = f"🚨 Bitcoin Bot Error Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 20px;">
                <div style="background-color: #e74c3c; color: white; padding: 20px; border-radius: 5px;">
                    <h2>🚨 Bitcoin Trading Bot Error</h2>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; border-left: 4px solid #e74c3c;">
                    <h3>Error Message:</h3>
                    <p><code>{error_message}</code></p>
                </div>
                
                {f'<div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa;"><h3>Error Details:</h3><pre>{error_details}</pre></div>' if error_details else ''}
                
                <div style="margin: 20px 0; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <h3>Recommended Actions:</h3>
                    <ul>
                        <li>Check the bot logs for more details</li>
                        <li>Verify API key configuration</li>
                        <li>Check internet connectivity</li>
                        <li>Restart the bot if necessary</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(subject, html_body)
            
        except Exception as e:
            logger.error(f"Error report email failed: {e}")
            return False


class NotificationManager:
    """Centralized notification management"""
    
    def __init__(self, whatsapp_number="+923353015576"):
        self.whatsapp = WhatsAppNotifier(whatsapp_number)
        self.gmail = GmailReporter()
        
        self.notification_history = []
    
    def send_trade_notification(self, trade_type, price, amount, reason, pnl=None):
        """Send trade notification via all enabled channels"""
        success = False
        
        # WhatsApp notification
        if self.whatsapp.send_trade_alert(trade_type, price, amount, reason, pnl):
            success = True
        
        # Log notification
        notification = {
            'timestamp': datetime.now(),
            'type': 'trade',
            'trade_type': trade_type,
            'price': price,
            'amount': amount,
            'reason': reason,
            'pnl': pnl,
            'success': success
        }
        
        self.notification_history.append(notification)
        return success
    
    def send_daily_summary(self, portfolio_value, day_pnl, trades_count, current_price):
        """Send daily summary via WhatsApp"""
        return self.whatsapp.send_daily_summary(portfolio_value, day_pnl, trades_count, current_price)
    
    def send_weekly_report(self, performance_data, trades_data, config_data):
        """Send comprehensive weekly report"""
        email_success = self.gmail.send_weekly_report(performance_data, trades_data, config_data)
        whatsapp_success = self.whatsapp.send_weekly_summary(
            performance_data.get('portfolio', {}).get('total_value', 0),
            performance_data.get('dca_performance', {}).get('pnl', 0),
            performance_data.get('total_trades', 0),
            performance_data.get('current_price', 0)
        )
        
        return email_success or whatsapp_success
    
    def send_error_alert(self, error_message, error_details=None):
        """Send error alert via all channels"""
        whatsapp_success = self.whatsapp.send_trade_alert("ERROR", 0, 0, error_message)
        email_success = self.gmail.send_error_report(error_message, error_details)
        
        return whatsapp_success or email_success
    
    def get_notification_stats(self):
        """Get notification statistics"""
        if not self.notification_history:
            return {'total': 0, 'success_rate': 0}
        
        total = len(self.notification_history)
        successful = sum(1 for n in self.notification_history if n['success'])
        success_rate = (successful / total) * 100
        
        return {
            'total': total,
            'successful': successful,
            'success_rate': success_rate,
            'last_notification': self.notification_history[-1]['timestamp'] if self.notification_history else None
        }