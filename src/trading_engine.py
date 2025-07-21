"""
Bitcoin Trading Agent - Trading Engine Module

This module contains the core trading logic:
- DCA Strategy implementation
- ATR-based stop-loss system
- Position management
- Risk controls
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DCAStrategy:
    """Dollar-Cost Averaging strategy implementation"""
    
    def __init__(self, config):
        self.config = config
        self.budget = config.get('budget', 1000)
        self.dca_percentage = config.get('dca_percentage', 3.0)
        self.position_size_pct = config.get('position_size_pct', 2.0)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        
        # Portfolio tracking
        self.trades = []
        self.total_invested = 0
        self.total_btc = 0
        
    def should_trigger_dca(self, current_data, previous_price=None):
        """Check if DCA trigger conditions are met"""
        if not self.config.get('enable_dca', True):
            return False, "DCA disabled in config"
        
        # Check budget
        if self.total_invested >= self.budget:
            return False, "Budget exhausted"
        
        current_price = current_data['price']
        
        # Price drop trigger
        if previous_price:
            price_change = ((current_price - previous_price) / previous_price) * 100
            if price_change <= -self.dca_percentage:
                return True, f"Price drop trigger: {price_change:.2f}%"
        
        # RSI oversold trigger
        if current_data.get('rsi_14', 50) <= self.rsi_oversold:
            return True, f"RSI oversold: {current_data['rsi_14']:.1f}"
        
        return False, "No trigger conditions met"
    
    def calculate_position_size(self, current_price):
        """Calculate position size based on remaining budget"""
        remaining_budget = self.budget - self.total_invested
        position_value = min(
            self.budget * (self.position_size_pct / 100),
            remaining_budget
        )
        btc_amount = position_value / current_price
        return position_value, btc_amount
    
    def execute_dca_trade(self, current_data, trigger_reason):
        """Execute DCA trade"""
        current_price = current_data['price']
        position_value, btc_amount = self.calculate_position_size(current_price)
        
        trade = {
            'timestamp': current_data['timestamp'],
            'type': 'DCA_BUY',
            'price': current_price,
            'usd_amount': position_value,
            'btc_amount': btc_amount,
            'trigger_reason': trigger_reason,
            'atr': current_data.get('atr_14', 0),
            'rsi': current_data.get('rsi_14', 50)
        }
        
        self.trades.append(trade)
        self.total_invested += position_value
        self.total_btc += btc_amount
        
        logger.info(f"DCA buy executed: ${position_value:.2f} at ${current_price:.2f}")
        return trade
    
    def get_portfolio_status(self, current_price):
        """Get current portfolio status"""
        if self.total_btc == 0:
            return {
                'total_invested': 0,
                'total_btc': 0,
                'current_value': 0,
                'pnl': 0,
                'pnl_pct': 0,
                'avg_buy_price': 0,
                'trades_count': 0
            }
        
        current_value = self.total_btc * current_price
        pnl = current_value - self.total_invested
        pnl_pct = (pnl / self.total_invested * 100) if self.total_invested > 0 else 0
        avg_buy_price = self.total_invested / self.total_btc
        
        return {
            'total_invested': self.total_invested,
            'total_btc': self.total_btc,
            'current_value': current_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'avg_buy_price': avg_buy_price,
            'trades_count': len(self.trades)
        }


class ATRStopLossStrategy:
    """ATR-based stop-loss strategy"""
    
    def __init__(self, config):
        self.config = config
        self.atr_multiplier = config.get('atr_multiplier', 1.5)
        self.active_positions = []
        self.closed_positions = []
    
    def calculate_stop_loss(self, entry_price, atr_value):
        """Calculate ATR-based stop-loss level"""
        stop_loss = entry_price - (atr_value * self.atr_multiplier)
        stop_distance_pct = ((entry_price - stop_loss) / entry_price) * 100
        return stop_loss, stop_distance_pct
    
    def open_position(self, trade_data, atr_value):
        """Open new position with ATR stop-loss"""
        entry_price = trade_data['price']
        stop_loss, stop_distance = self.calculate_stop_loss(entry_price, atr_value)
        
        position = {
            'id': f"pos_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'entry_time': trade_data['timestamp'],
            'entry_price': entry_price,
            'btc_amount': trade_data['btc_amount'],
            'usd_amount': trade_data['usd_amount'],
            'stop_loss': stop_loss,
            'stop_distance_pct': stop_distance,
            'atr_at_entry': atr_value,
            'trade_type': trade_data['type'],
            'status': 'ACTIVE'
        }
        
        self.active_positions.append(position)
        logger.info(f"Position opened: {position['id']} at ${entry_price:.2f}")\n        return position
    
    def check_stop_losses(self, current_data):
        """Check if any positions hit stop-loss"""
        current_price = current_data['price']
        stopped_positions = []
        
        for position in self.active_positions.copy():
            if current_price <= position['stop_loss']:
                stopped_position = self.close_position(position, current_data, 'STOP_LOSS')
                stopped_positions.append(stopped_position)
        
        return stopped_positions
    
    def close_position(self, position, current_data, reason):
        """Close position and calculate P&L"""
        exit_price = current_data['price']
        exit_time = current_data['timestamp']
        
        # Calculate P&L
        pnl_usd = (exit_price - position['entry_price']) * position['btc_amount']
        pnl_pct = ((exit_price - position['entry_price']) / position['entry_price']) * 100
        
        # Update position
        position.update({
            'exit_time': exit_time,
            'exit_price': exit_price,
            'pnl_usd': pnl_usd,
            'pnl_pct': pnl_pct,
            'close_reason': reason,
            'status': 'CLOSED',
            'hold_time': exit_time - position['entry_time']
        })
        
        # Move to closed positions
        self.active_positions.remove(position)
        self.closed_positions.append(position)
        
        logger.info(f"Position closed: {position['id']} P&L: ${pnl_usd:+.2f}")
        return position
    
    def update_trailing_stops(self, current_data):
        """Update trailing stops based on current ATR"""
        current_atr = current_data.get('atr_14', 0)
        current_price = current_data['price']
        
        for position in self.active_positions:
            if current_price > position['entry_price']:
                new_stop = current_price - (current_atr * self.atr_multiplier)
                
                if new_stop > position['stop_loss']:
                    old_stop = position['stop_loss']
                    position['stop_loss'] = new_stop
                    position['stop_distance_pct'] = ((current_price - new_stop) / current_price) * 100
                    logger.info(f"Trailing stop updated: ${old_stop:.2f} → ${new_stop:.2f}")
    
    def get_positions_summary(self):
        """Get summary of all positions"""
        total_trades = len(self.active_positions) + len(self.closed_positions)
        
        if not self.closed_positions:
            return {
                'active_positions': len(self.active_positions),
                'closed_positions': 0,
                'total_trades': total_trades,
                'win_rate': 0,
                'avg_return': 0
            }
        
        wins = sum(1 for pos in self.closed_positions if pos['pnl_usd'] > 0)
        win_rate = (wins / len(self.closed_positions)) * 100
        avg_return = sum(pos['pnl_pct'] for pos in self.closed_positions) / len(self.closed_positions)
        
        return {
            'active_positions': len(self.active_positions),
            'closed_positions': len(self.closed_positions),
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_return': avg_return
        }


class RiskManager:
    """Portfolio risk management"""
    
    def __init__(self, config):
        self.config = config
        self.max_drawdown = config.get('max_drawdown', 25.0)
        self.portfolio_start_value = None
    
    def check_portfolio_health(self, portfolio_value):
        """Check portfolio health and risk metrics"""
        if self.portfolio_start_value is None:
            self.portfolio_start_value = portfolio_value
        
        # Calculate drawdown
        drawdown = ((portfolio_value - self.portfolio_start_value) / self.portfolio_start_value) * 100
        
        # Check if max drawdown hit
        max_drawdown_hit = drawdown <= -self.max_drawdown
        
        return {
            'current_value': portfolio_value,
            'start_value': self.portfolio_start_value,
            'drawdown': drawdown,
            'max_drawdown_limit': self.max_drawdown,
            'max_drawdown_hit': max_drawdown_hit,
            'risk_level': self._get_risk_level(drawdown)
        }
    
    def _get_risk_level(self, drawdown):
        """Determine risk level based on drawdown"""
        if drawdown >= -5:
            return 'LOW'
        elif drawdown >= -15:
            return 'MEDIUM'
        elif drawdown >= -25:
            return 'HIGH'
        else:
            return 'CRITICAL'


class TradingEngine:
    """Main trading engine that coordinates all strategies"""
    
    def __init__(self, config, exchange_client=None):
        self.config = config
        self.exchange = exchange_client
        
        # Initialize strategies
        self.dca_strategy = DCAStrategy(config)
        self.atr_strategy = ATRStopLossStrategy(config)
        self.risk_manager = RiskManager(config)
        
        # Trading state
        self.trading_log = []
        self.last_price = None
        self.is_running = False
    
    def execute_trading_cycle(self, current_market_data):
        """Execute one complete trading cycle"""
        cycle_start = datetime.now()
        actions_taken = []
        
        try:
            logger.info(f"Starting trading cycle at {cycle_start}")
            
            # 1. Check stop-losses first
            if self.config.get('enable_atr_stops', True):
                stopped_positions = self.atr_strategy.check_stop_losses(current_market_data)
                
                for stopped_pos in stopped_positions:
                    if self.exchange:
                        # Execute sell order
                        sell_order = self.exchange.place_market_order(
                            side='sell',
                            size=stopped_pos['btc_amount'],
                            paper_trade=True
                        )
                        
                        if sell_order:
                            actions_taken.append(f"Stop-loss triggered: {stopped_pos['id']}")
            
            # 2. Check DCA triggers
            should_dca, dca_reason = self.dca_strategy.should_trigger_dca(
                current_market_data, self.last_price
            )
            
            if should_dca:
                # Execute DCA trade
                dca_trade = self.dca_strategy.execute_dca_trade(current_market_data, dca_reason)
                
                if self.exchange:
                    # Execute buy order
                    buy_order = self.exchange.place_market_order(
                        side='buy',
                        size=dca_trade['btc_amount'],
                        paper_trade=True
                    )
                    
                    if buy_order:
                        actions_taken.append(f"DCA buy executed: ${dca_trade['usd_amount']:.2f}")
                        
                        # Open position with stop-loss if enabled
                        if self.config.get('enable_atr_stops', True):
                            current_atr = current_market_data.get('atr_14', 1000)
                            position = self.atr_strategy.open_position(dca_trade, current_atr)
            
            # 3. Update trailing stops
            if self.config.get('enable_atr_stops', True) and self.atr_strategy.active_positions:
                self.atr_strategy.update_trailing_stops(current_market_data)
            
            # 4. Risk management check
            if self.exchange:
                portfolio_value = self.exchange.get_portfolio_value(current_market_data['price'])['total_value']
                risk_status = self.risk_manager.check_portfolio_health(portfolio_value)
                
                if risk_status['max_drawdown_hit']:
                    logger.warning(f"Max drawdown reached: {risk_status['drawdown']:.2f}%")
                    actions_taken.append("Max drawdown warning issued")
            
            # 5. Update state
            self.last_price = current_market_data['price']
            
            # 6. Log cycle
            cycle_summary = {
                'timestamp': cycle_start,
                'current_price': current_market_data['price'],
                'actions_taken': actions_taken,
                'active_positions': len(self.atr_strategy.active_positions),
                'dca_invested': self.dca_strategy.total_invested,
                'dca_btc': self.dca_strategy.total_btc
            }
            
            self.trading_log.append(cycle_summary)
            logger.info(f"Cycle complete: {len(actions_taken)} actions taken")
            
            return cycle_summary
            
        except Exception as e:
            logger.error(f"Trading cycle error: {e}")
            return None
    
    def get_performance_summary(self, current_price):
        """Get comprehensive performance summary"""
        dca_status = self.dca_strategy.get_portfolio_status(current_price)
        atr_summary = self.atr_strategy.get_positions_summary()
        
        portfolio_value = 0
        if self.exchange:
            portfolio = self.exchange.get_portfolio_value(current_price)
            portfolio_value = portfolio['total_value']
        
        return {
            'timestamp': datetime.now(),
            'current_price': current_price,
            'dca_performance': dca_status,
            'atr_performance': atr_summary,
            'portfolio_value': portfolio_value,
            'total_trades': len(self.trading_log),
            'risk_status': self.risk_manager.check_portfolio_health(portfolio_value) if portfolio_value > 0 else None
        }
    
    def save_state(self, filepath):
        """Save trading engine state to file"""
        state = {
            'config': self.config,
            'dca_trades': self.dca_strategy.trades,
            'active_positions': self.atr_strategy.active_positions,
            'closed_positions': self.atr_strategy.closed_positions,
            'trading_log': self.trading_log,
            'last_price': self.last_price,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_state(self, filepath):
        """Load trading engine state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Restore state
            self.dca_strategy.trades = state.get('dca_trades', [])
            self.atr_strategy.active_positions = state.get('active_positions', [])
            self.atr_strategy.closed_positions = state.get('closed_positions', [])
            self.trading_log = state.get('trading_log', [])
            self.last_price = state.get('last_price')
            
            # Recalculate DCA totals
            self.dca_strategy.total_invested = sum(t['usd_amount'] for t in self.dca_strategy.trades)
            self.dca_strategy.total_btc = sum(t['btc_amount'] for t in self.dca_strategy.trades)
            
            logger.info(f"State loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False