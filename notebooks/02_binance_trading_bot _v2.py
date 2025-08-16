import ccxt
import pandas as pd
import json
import os
import re
import time
import warnings
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
import asyncio

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ----------------------------------------------------------------------------
# Cell 1: Setup & Environment
# ----------------------------------------------------------------------------

def cell1_setup_environment():
    """
    Cell 1: Setup & Environment
    Initialize all required libraries and run data collection
    """

    # Load environment variables
    load_dotenv()

    print("🚀 Bitcoin Trading Bot - Binance + Llama 4 Maverick")
    print("================================================")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Paper Trading Mode: {os.getenv('PAPER_MODE', 'True')}")
    print(f"Trading Budget: ${os.getenv('TRADING_BUDGET', '1000')}")

    # Check required environment variables
    required_vars = ['GROQ_API_KEY', 'BINANCE_API_KEY', 'BINANCE_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️  WARNING: Missing environment variables: {missing_vars}")
        print("Please check your .env file")
    else:
        print("✅ All required environment variables loaded")

    print("\n🔄 Running data collection to get fresh market data...")
    try:
        # Run the data collection script
        exec(open('01_data_collection.py').read())
        print("✅ Data collection completed successfully")
    except Exception as e:
        print(f"❌ Data collection failed: {e}")
        print("Please ensure 01_data_collection.py is in the same directory")


# ----------------------------------------------------------------------------
# Cell 2: Data Collection & Parsing
# ----------------------------------------------------------------------------

def cell2_data_collection_parsing():
    """
    Cell 2: Data Collection & Parsing (Workflow Steps 1-2)
    Parse market data from the generated markdown report
    """
    import ccxt.async_support as ccxt  # Use async version of ccxt
    import pandas as pd
    import json
    import os
    import re
    import time
    import warnings
    from datetime import datetime
    from groq import Groq
    from dotenv import load_dotenv
    import asyncio

    # Suppress warnings for cleaner output
    warnings.filterwarnings('ignore')

    # Load environment variables
    load_dotenv()

    print("🚀 Bitcoin Trading Bot - Binance + Llama 4 Maverick")
    print("================================================")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Paper Trading Mode: {os.getenv('PAPER_MODE', 'True')}")
    print(f"Trading Budget: ${os.getenv('TRADING_BUDGET', '1000')}")

    # Check required environment variables
    required_vars = ['GROQ_API_KEY', 'BINANCE_API_KEY', 'BINANCE_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️  WARNING: Missing environment variables: {missing_vars}")
        print("Please check your .env file and ensure all required variables are set")
        exit(1)  # Exit if critical variables are missing
    else:
        print("✅ All required environment variables loaded")

    print("\n🔄 Running data collection to get fresh market data...")

    async def run_data_collection():
        try:
            # Dynamically import and run the data collection script
            with open('01_data_collection.py', 'r') as file:
                code = file.read()
            # Execute the script in the current namespace
            namespace = {}
            exec(code, namespace)
            # Assume the script defines an async function `collect_data`
            if 'collect_data' in namespace and asyncio.iscoroutinefunction(namespace['collect_data']):
                await namespace['collect_data']()
            print("✅ Data collection completed successfully")
        except Exception as e:
            print(f"❌ Data collection failed: {e}")
            print("Please ensure 01_data_collection.py is in the same directory and contains a valid 'collect_data' async function")

    # Run the async function in the existing event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If an event loop is already running (e.g., in Jupyter), use create_task
            loop.create_task(run_data_collection())
        else:
            # Otherwise, use asyncio.run
            asyncio.run(run_data_collection())
    except Exception as e:
        print(f"❌ Failed to run data collection: {e}")

# ----------------------------------------------------------------------------
# Cell 3: LLM Market Analysis
# ----------------------------------------------------------------------------

def cell3_llm_market_analysis():
    """
    Cell 3: LLM Market Analysis (Workflow Step 3)
    Setup and functions for Llama 4 Maverick market analysis
    """

    def setup_groq_client():
        """
        Initialize Groq client with Llama 4 Maverick for market analysis.
        
        Returns:
        --------
        groq.Client : Configured Groq client object for LLM interactions
        
        Raises:
        -------
        Exception: If GROQ_API_KEY is not set or client initialization fails
        """
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise Exception("GROQ_API_KEY not found in environment variables")
        
        try:
            client = Groq(api_key=api_key)
            print("🤖 Groq client initialized with Llama 4 Maverick")
            return client
        except Exception as e:
            raise Exception(f"Failed to initialize Groq client: {e}")

    def get_llm_market_analysis(client, market_data, portfolio_state):
        """
        Get comprehensive market analysis from Llama 4 Maverick.
        
        Uses the latest Llama 4 Maverick model to analyze current Bitcoin market
        conditions, portfolio state, and provide intelligent trading recommendations
        with detailed reasoning and confidence scoring.
        
        Parameters:
        -----------
        client : groq.Client
            Configured Groq client for API calls
        market_data : dict
            Current market indicators including price, ATR, RSI, etc.
        portfolio_state : dict
            Current portfolio positions, trades, and budget allocation
        
        Returns:
        --------
        dict : LLM analysis containing:
            - 'sentiment' (str): 'bullish', 'bearish', or 'neutral'
            - 'recommendation' (str): 'buy', 'hold', or 'sell'
            - 'confidence' (float): Confidence score from 0.0 to 1.0
            - 'reasoning' (str): Detailed explanation of the analysis
            - 'position_size_modifier' (float): Multiplier for position sizing (0.5-2.0)
            - 'risk_level' (str): 'low', 'medium', or 'high'
        
        Example:
        --------
        >>> analysis = get_llm_market_analysis(client, market_data, portfolio)
        >>> print(f"Recommendation: {analysis['recommendation']}")
        >>> print(f"Confidence: {analysis['confidence']:.2f}")
        """
        
        # Calculate additional context for LLM
        budget_utilization = (portfolio_state['used_budget'] / portfolio_state['total_budget']) * 100
        price_vs_last_buy = 0
        if portfolio_state.get('last_buy_price', 0) > 0:
            price_vs_last_buy = ((market_data['price'] - portfolio_state['last_buy_price']) / portfolio_state['last_buy_price']) * 100
        
        # Construct comprehensive prompt for Llama 4 Maverick
        prompt = f"""
You are an expert Bitcoin trading analyst using Dollar-Cost Averaging (DCA) strategy. Analyze the current market conditions and provide trading recommendations.

CURRENT MARKET DATA:
- Bitcoin Price: ${market_data['price']:,.2f}
- ATR (14-period): ${market_data['atr']:,.2f} (volatility measure)
- RSI (14-period): {market_data['rsi']:.1f} (momentum indicator, <30=oversold, >70=overbought)
- SMA 20: ${market_data.get('sma_20', 0):,.2f}
- SMA 50: ${market_data.get('sma_50', 0):,.2f}
- Data Timestamp: {market_data['timestamp']}

PORTFOLIO STATUS:
- Total Budget: ${portfolio_state['total_budget']:,.2f}
- Used Budget: ${portfolio_state['used_budget']:,.2f} ({budget_utilization:.1f}% utilized)
- Available Budget: ${portfolio_state['total_budget'] - portfolio_state['used_budget']:,.2f}
- BTC Holdings: {portfolio_state['btc_holdings']:.6f} BTC
- Last Buy Price: ${portfolio_state.get('last_buy_price', 0):,.2f}
- Price Change Since Last Buy: {price_vs_last_buy:+.2f}%
- Total Trades: {len(portfolio_state.get('trades', []))}

DCA STRATEGY CONTEXT:
- Triggers: Buy when price drops ≥3% from last purchase OR RSI ≤30 (oversold)
- Position Size: Typically 2% of total budget per trade
- Stop-Loss: ATR-based dynamic stops (Entry Price - 1.5 × ATR)
- Risk Management: Maximum 25% portfolio drawdown protection

ANALYSIS REQUIRED:
Provide a comprehensive analysis in JSON format with the following fields:

1. "sentiment": Overall market sentiment ("bullish", "bearish", "neutral")
2. "recommendation": Trading action ("buy", "hold", "sell")
3. "confidence": Confidence in recommendation (0.0 to 1.0)
4. "reasoning": Detailed explanation of your analysis (2-3 sentences)
5. "position_size_modifier": Adjustment factor for trade size (0.5 to 2.0, where 1.0 = normal 2% position)
6. "risk_level": Current market risk assessment ("low", "medium", "high")
7. "key_factors": List of 2-3 most important factors influencing your decision

Consider technical indicators, portfolio allocation, market volatility, and DCA strategy principles. Be conservative with high confidence scores (>0.8) and provide clear reasoning.

Respond with valid JSON only:
"""

        try:
            print("🧠 Analyzing market conditions with Llama 4 Maverick...")
            
            response = client.chat.completions.create(
                model="llama-4-maverick-17b-128e-instruct",
                messages=[
                    {"role": "system", "content": "You are an expert Bitcoin trading analyst. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1000,
                top_p=0.9
            )
            
            # Extract and parse the JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response if it contains markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON response
            llm_analysis = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['sentiment', 'recommendation', 'confidence', 'reasoning', 'position_size_modifier', 'risk_level']
            for field in required_fields:
                if field not in llm_analysis:
                    raise ValueValue(f"Missing required field: {field}")
            
            # Validate confidence score
            confidence = float(llm_analysis['confidence'])
            if not 0.0 <= confidence <= 1.0:
                print(f"⚠️  Warning: Confidence score {confidence} out of range, clamping to [0,1]")
                llm_analysis['confidence'] = max(0.0, min(1.0, confidence))
            
            # Validate position size modifier
            modifier = float(llm_analysis['position_size_modifier'])
            if not 0.5 <= modifier <= 2.0:
                print(f"⚠️  Warning: Position size modifier {modifier} out of range, clamping to [0.5,2.0]")
                llm_analysis['position_size_modifier'] = max(0.5, min(2.0, modifier))
            
            print(f"🎯 LLM Analysis Complete:")
            print(f"   Sentiment: {llm_analysis['sentiment']}")
            print(f"   Recommendation: {llm_analysis['recommendation']}")
            print(f"   Confidence: {llm_analysis['confidence']:.2f}")
            print(f"   Risk Level: {llm_analysis['risk_level']}")
            
            return llm_analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing LLM response as JSON: {e}")
            print(f"Raw response: {response_text[:200]}...")
            # Return default neutral analysis
            return {
                'sentiment': 'neutral',
                'recommendation': 'hold',
                'confidence': 0.3,
                'reasoning': 'LLM response parsing failed, defaulting to conservative hold position',
                'position_size_modifier': 1.0,
                'risk_level': 'medium',
                'key_factors': ['LLM parsing error']
            }
        except Exception as e:
            print(f"❌ Error getting LLM analysis: {e}")
            # Return default analysis on any error
            return {
                'sentiment': 'neutral',
                'recommendation': 'hold',
                'confidence': 0.2,
                'reasoning': f'LLM analysis failed due to error: {str(e)[:100]}',
                'position_size_modifier': 1.0,
                'risk_level': 'high',
                'key_factors': ['LLM error', 'defaulting to safe mode']
            }

    # Test Groq client setup
    try:
        global groq_client
        groq_client = setup_groq_client()
        print("✅ Groq LLM integration ready")
    except Exception as e:
        print(f"❌ Groq setup failed: {e}")
        groq_client = None

# ----------------------------------------------------------------------------
# Cell 4: Enhanced DCA Strategy
# ----------------------------------------------------------------------------

def cell4_enhanced_dca_strategy():
    """
    Cell 4: Enhanced DCA Strategy (Workflow Step 4)
    Implement core DCA logic with LLM integration and ATR-based stop-loss
    """

    def should_trigger_dca(market_data, portfolio_state, llm_analysis):
        """
        Determine if DCA buy should be triggered based on multiple conditions.
        
        Enhanced DCA strategy that combines traditional price-based triggers
        with RSI oversold conditions and LLM market analysis for intelligent
        decision making.
        
        Parameters:
        -----------
        market_data : dict
            Current market indicators (price, ATR, RSI, etc.)
        portfolio_state : dict
            Current portfolio positions and budget allocation
        llm_analysis : dict
            LLM market analysis with sentiment and recommendations
        
        Returns:
        --------
        dict : Decision result containing:
            - 'should_buy' (bool): Whether to trigger DCA buy
            - 'trigger_reason' (str): Primary reason for the decision
            - 'confidence' (float): Combined confidence score
            - 'position_size_modifier' (float): LLM-adjusted position sizing
        """
        
        print("🧮 Evaluating DCA trigger conditions...")
        
        current_price = market_data['price']
        last_buy_price = portfolio_state.get('last_buy_price', 0)
        rsi = market_data['rsi']
        available_budget = portfolio_state['total_budget'] - portfolio_state['used_budget']
        
        # Calculate budget utilization percentage
        budget_utilization = (portfolio_state['used_budget'] / portfolio_state['total_budget']) * 100
        
        # Initialize decision variables
        triggers = []
        should_buy = False
        confidence = 0.0
        position_modifier = llm_analysis.get('position_size_modifier', 1.0)
        
        # Trigger 1: Price drop ≥3% from last purchase
        if last_buy_price > 0:
            price_change_pct = ((current_price - last_buy_price) / last_buy_price) * 100
            if price_change_pct <= -3.0:
                triggers.append(f"Price drop: {price_change_pct:.1f}% from last buy")
                confidence += 0.3
                should_buy = True
        else:
            # First purchase - always consider if other conditions met
            triggers.append("First purchase opportunity")
            confidence += 0.2
        
        # Trigger 2: RSI oversold condition (≤30)
        if rsi <= 30:
            triggers.append(f"RSI oversold: {rsi:.1f} ≤ 30")
            confidence += 0.3
            should_buy = True
        
        # Trigger 3: LLM recommends buy with sufficient confidence
        llm_recommendation = llm_analysis.get('recommendation', '').lower()
        llm_confidence = llm_analysis.get('confidence', 0.0)
        if llm_recommendation == 'buy' and llm_confidence >= 0.6:
            triggers.append(f"LLM buy signal: {llm_confidence:.2f} confidence")
            confidence += llm_confidence * 0.4  # Weight LLM confidence
            should_buy = True
        
        # Risk Management Checks
        risk_factors = []
        
        # Check budget availability (minimum $50 trade size)
        min_trade_size = 50.0
        if available_budget < min_trade_size:
            risk_factors.append(f"Insufficient budget: ${available_budget:.2f} < ${min_trade_size}")
            should_buy = False
        
        # Check maximum budget utilization (90% limit for safety)
        if budget_utilization > 90:
            risk_factors.append(f"Budget utilization too high: {budget_utilization:.1f}% > 90%")
            should_buy = False
        
        # Check LLM risk level
        llm_risk = llm_analysis.get('risk_level', 'medium').lower()
        if llm_risk == 'high' and llm_confidence < 0.8:
            risk_factors.append(f"High risk market with low LLM confidence: {llm_confidence:.2f}")
            should_buy = False
            confidence *= 0.5  # Reduce confidence in high-risk conditions
        
        # Final confidence calculation
        confidence = min(confidence, 1.0)  # Cap at 1.0
        
        # Create decision result
        decision = {
            'should_buy': should_buy,
            'trigger_reason': '; '.join(triggers) if triggers else 'No triggers activated',
            'risk_factors': risk_factors,
            'confidence': confidence,
            'position_size_modifier': position_modifier,
            'budget_utilization': budget_utilization,
            'available_budget': available_budget
        }
        
        # Log decision details
        print(f"📊 DCA Decision Analysis:")
        print(f"   Should Buy: {'✅ YES' if should_buy else '❌ NO'}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Triggers: {decision['trigger_reason']}")
        if risk_factors:
            print(f"   Risk Factors: {'; '.join(risk_factors)}")
        print(f"   Position Modifier: {position_modifier:.2f}x")
        print(f"   Budget Utilization: {budget_utilization:.1f}%")
        
        return decision

    def calculate_position_size(portfolio_state, llm_analysis, base_percentage=2.0):
        """
        Calculate optimal position size with LLM modifier.
        
        Determines trade size based on available budget, base DCA percentage,
        and LLM position sizing recommendations for dynamic allocation.
        
        Parameters:
        -----------
        portfolio_state : dict
            Current portfolio budget and allocation
        llm_analysis : dict
            LLM analysis with position size modifier
        base_percentage : float, default=2.0
            Base percentage of total budget per trade
        
        Returns:
        --------
        dict : Position sizing details:
            - 'trade_amount' (float): Dollar amount to trade
            - 'percentage_used' (float): Percentage of total budget
            - 'modifier_applied' (float): LLM modifier used
        """
        
        total_budget = portfolio_state['total_budget']
        available_budget = portfolio_state['total_budget'] - portfolio_state['used_budget']
        position_modifier = llm_analysis.get('position_size_modifier', 1.0)
        
        # Calculate base trade amount
        base_amount = total_budget * (base_percentage / 100)
        
        # Apply LLM modifier
        modified_amount = base_amount * position_modifier
        
        # Ensure we don't exceed available budget
        final_amount = min(modified_amount, available_budget * 0.95)  # Leave 5% buffer
        
        # Calculate actual percentage used
        actual_percentage = (final_amount / total_budget) * 100
        
        position_info = {
            'trade_amount': final_amount,
            'percentage_used': actual_percentage,
            'modifier_applied': position_modifier,
            'base_amount': base_amount,
            'available_budget': available_budget
        }
        
        print(f"💰 Position Sizing:")
        print(f"   Base Amount (2%): ${base_amount:.2f}")
        print(f"   LLM Modifier: {position_modifier:.2f}x")
        print(f"   Final Amount: ${final_amount:.2f} ({actual_percentage:.2f}% of total budget)")
        
        return position_info

    def calculate_atr_stop_loss(entry_price, atr_value, multiplier=1.5):
        """
        Calculate ATR-based dynamic stop-loss level.
        
        Uses Average True Range to set volatility-adjusted stop-loss levels
        that adapt to current market conditions and prevent premature exits
        during normal market volatility.
        
        Parameters:
        -----------
        entry_price : float
            Price at which position was entered
        atr_value : float
            Current 14-period Average True Range
        multiplier : float, default=1.5
            ATR multiplier for stop-loss distance
        
        Returns:
        --------
        dict : Stop-loss details:
            - 'stop_loss_price' (float): Calculated stop-loss price
            - 'stop_distance' (float): Distance from entry price
            - 'stop_percentage' (float): Percentage risk from entry
        """
        
        stop_distance = atr_value * multiplier
        stop_loss_price = entry_price - stop_distance
        stop_percentage = (stop_distance / entry_price) * 100
        
        stop_info = {
            'stop_loss_price': stop_loss_price,
            'stop_distance': stop_distance,
            'stop_percentage': stop_percentage,
            'atr_value': atr_value,
            'multiplier': multiplier
        }
        
        print(f"🛡️  ATR Stop-Loss Calculation:")
        print(f"   Entry Price: ${entry_price:,.2f}")
        print(f"   ATR (14): ${atr_value:,.2f}")
        print(f"   Stop Distance: ${stop_distance:,.2f} ({multiplier}x ATR)")
        print(f"   Stop-Loss Price: ${stop_loss_price:,.2f}")
        print(f"   Risk Percentage: {stop_percentage:.2f}%")
        
        return stop_info

    def should_trigger_stop_loss(current_price, entry_price, stop_loss_price, market_data):
        """
        Determine if stop-loss should be triggered.
        
        Evaluates current price against stop-loss level with additional
        market context to prevent false signals during temporary spikes.
        
        Parameters:
        -----------
        current_price : float
            Current Bitcoin market price
        entry_price : float
            Original position entry price
        stop_loss_price : float
            Calculated stop-loss trigger price
        market_data : dict
            Current market indicators for context
        
        Returns:
        --------
        dict : Stop-loss decision:
            - 'should_stop' (bool): Whether to trigger stop-loss
            - 'reason' (str): Reason for decision
            - 'unrealized_pnl_pct' (float): Current unrealized P&L percentage
        """
        
        unrealized_pnl_pct = ((current_price - entry_price) / entry_price) * 100
        price_vs_stop = current_price - stop_loss_price
        
        should_stop = current_price <= stop_loss_price
        
        if should_stop:
            reason = f"Price ${current_price:,.2f} ≤ Stop ${stop_loss_price:,.2f}"
        else:
            reason = f"Price ${current_price:,.2f} above stop ${stop_loss_price:,.2f}"
        
        result = {
            'should_stop': should_stop,
            'reason': reason,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'price_vs_stop': price_vs_stop
        }
        
        if should_stop:
            print(f"🚨 STOP-LOSS TRIGGERED: {reason}")
            print(f"   Unrealized P&L: {unrealized_pnl_pct:+.2f}%")
        
        return result

    # Test DCA strategy functions with current data
    print("🧪 Testing DCA Strategy Functions...")
    try:
        # Create test portfolio state
        test_portfolio = {
            'total_budget': 1000.0,
            'used_budget': 100.0,
            'btc_holdings': 0.001,
            'last_buy_price': 115000.0,
            'trades': []
        }
        
        # Create test LLM analysis
        test_llm_analysis = {
            'sentiment': 'neutral',
            'recommendation': 'buy',
            'confidence': 0.7,
            'position_size_modifier': 1.2,
            'risk_level': 'medium'
        }
        
        # Test DCA decision
        if 'test_market_data' in locals():
            dca_decision = should_trigger_dca(test_market_data, test_portfolio, test_llm_analysis)
            
            if dca_decision['should_buy']:
                position_info = calculate_position_size(test_portfolio, test_llm_analysis)
                stop_info = calculate_atr_stop_loss(test_market_data['price'], test_market_data['atr'])
            
            print("✅ DCA strategy functions tested successfully")
        else:
            print("⚠️  Market data not available for testing")
        
    except Exception as e:
        print(f"❌ DCA strategy test failed: {e}")

# ----------------------------------------------------------------------------
# Cell 5: Trade Execution
# ----------------------------------------------------------------------------

def cell5_trade_execution():
    """
    Cell 5: Trade Execution (Workflow Step 5)
    Binance API integration with paper/live trading modes
    """

    def initialize_binance_client():
        """
        Initialize Binance exchange client using ccxt library.
        
        Sets up connection to Binance with API credentials and configures
        for either paper trading (testnet) or live trading based on environment.
        
        Returns:
        --------
        ccxt.Exchange : Configured Binance exchange client
        bool : True if paper trading mode, False if live trading
        
        Raises:
        -------
        Exception: If API credentials missing or client initialization fails
        """
        
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_SECRET')
        paper_mode = os.getenv('PAPER_MODE', 'True').lower() == 'true'
        
        if not api_key or not api_secret:
            if paper_mode:
                print("⚠️  No Binance credentials found - using paper trading mode")
                return None, True
            else:
                raise Exception("Binance API credentials required for live trading")
        
        try:
            # Initialize Binance client
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': paper_mode,  # Use testnet for paper trading
                'options': {
                    'defaultType': 'spot',  # Spot trading
                },
                'enableRateLimit': True,
            })
            
            # Test connection
            if not paper_mode:
                account_info = exchange.fetch_balance()
                print(f"🔗 Connected to Binance (Live Trading)")
                print(f"   Account Status: Active")
            else:
                print(f"🔗 Connected to Binance (Paper Trading)")
            
            return exchange, paper_mode
            
        except Exception as e:
            raise Exception(f"Failed to initialize Binance client: {e}")

    def execute_buy_order(exchange, symbol, trade_amount, current_price, paper_mode=True):
        """
        Execute a buy order on Binance or simulate in paper trading mode.
        
        Places a market buy order for Bitcoin using the specified trade amount.
        In paper mode, simulates the order execution without actual trading.
        
        Parameters:
        -----------
        exchange : ccxt.Exchange or None
            Binance exchange client (None for paper mode)
        symbol : str
            Trading symbol (e.g., 'BTC/USDT')
        trade_amount : float
            Dollar amount to purchase
        current_price : float
            Current Bitcoin price for calculations
        paper_mode : bool, default=True
            Whether to simulate trade (True) or execute live (False)
        
        Returns:
        --------
        dict : Order result containing:
            - 'success' (bool): Whether order was successful
            - 'order_id' (str): Order ID or simulation ID
            - 'btc_amount' (float): Amount of BTC purchased
            - 'actual_price' (float): Actual execution price
            - 'fees' (float): Trading fees paid
            - 'timestamp' (str): Execution timestamp
        """
        
        print(f"💳 Executing BUY order...")
        print(f"   Symbol: {symbol}")
        print(f"   Amount: ${trade_amount:.2f}")
        print(f"   Mode: {'📝 Paper Trading' if paper_mode else '🚀 Live Trading'}")
        
        if paper_mode:
            # Simulate paper trading
            simulated_slippage = 0.001  # 0.1% slippage simulation
            execution_price = current_price * (1 + simulated_slippage)
            btc_amount = trade_amount / execution_price
            simulated_fees = trade_amount * 0.001  # 0.1% trading fee simulation
            
            order_result = {
                'success': True,
                'order_id': f"PAPER_{int(time.time())}",
                'btc_amount': btc_amount,
                'actual_price': execution_price,
                'fees': simulated_fees,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'mode': 'paper'
            }
            
            print(f"📝 Paper Trade Executed:")
            print(f"   BTC Purchased: {btc_amount:.6f} BTC")
            print(f"   Execution Price: ${execution_price:,.2f}")
            print(f"   Simulated Fees: ${simulated_fees:.2f}")
            
            return order_result
        
        else:
            # Execute live trade
            try:
                # Calculate BTC amount to buy
                btc_amount = trade_amount / current_price
                
                # Place market buy order
                order = exchange.create_market_buy_order(symbol, btc_amount)
                
                order_result = {
                    'success': True,
                    'order_id': order['id'],
                    'btc_amount': order['amount'],
                    'actual_price': order['price'] if order['price'] else current_price,
                    'fees': order['fee']['cost'] if order['fee'] else 0,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'mode': 'live'
                }
                
                print(f"🚀 Live Trade Executed:")
                print(f"   Order ID: {order['id']}")
                print(f"   BTC Purchased: {order['amount']:.6f} BTC")
                print(f"   Execution Price: ${order['price']:,.2f}" if order['price'] else f"Market Price: ${current_price:,.2f}")
                
                return order_result
                
            except Exception as e:
                print(f"❌ Buy order failed: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'mode': 'live'
                }

    def execute_sell_order(exchange, symbol, btc_amount, current_price, paper_mode=True):
        """
        Execute a sell order on Binance or simulate in paper trading mode.
        
        Places a market sell order for the specified BTC amount.
        Used for stop-loss execution or profit-taking.
        
        Parameters:
        -----------
        exchange : ccxt.Exchange or None
            Binance exchange client (None for paper mode)
        symbol : str
            Trading symbol (e.g., 'BTC/USDT')
        btc_amount : float
            Amount of BTC to sell
        current_price : float
            Current Bitcoin price for calculations
        paper_mode : bool, default=True
            Whether to simulate trade (True) or execute live (False)
        
        Returns:
        --------
        dict : Order result with execution details
        """
        
        print(f"💸 Executing SELL order...")
        print(f"   Symbol: {symbol}")
        print(f"   BTC Amount: {btc_amount:.6f} BTC")
        print(f"   Mode: {'📝 Paper Trading' if paper_mode else '🚀 Live Trading'}")
        
        if paper_mode:
            # Simulate paper trading
            simulated_slippage = 0.001  # 0.1% slippage simulation
            execution_price = current_price * (1 - simulated_slippage)
            usd_received = btc_amount * execution_price
            simulated_fees = usd_received * 0.001  # 0.1% trading fee
            net_received = usd_received - simulated_fees
            
            order_result = {
                'success': True,
                'order_id': f"PAPER_SELL_{int(time.time())}",
                'btc_amount': btc_amount,
                'actual_price': execution_price,
                'usd_received': net_received,
                'fees': simulated_fees,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'mode': 'paper'
            }
            
            print(f"📝 Paper Sell Executed:")
            print(f"   BTC Sold: {btc_amount:.6f} BTC")
            print(f"   Execution Price: ${execution_price:,.2f}")
            print(f"   USD Received: ${net_received:.2f} (after fees)")
            
            return order_result
        
        else:
            # Execute live trade
            try:
                # Place market sell order
                order = exchange.create_market_sell_order(symbol, btc_amount)
                
                order_result = {
                    'success': True,
                    'order_id': order['id'],
                    'btc_amount': order['amount'],
                    'actual_price': order['price'] if order['price'] else current_price,
                    'usd_received': order['cost'] if order['cost'] else btc_amount * current_price,
                    'fees': order['fee']['cost'] if order['fee'] else 0,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'mode': 'live'
                }
                
                print(f"🚀 Live Sell Executed:")
                print(f"   Order ID: {order['id']}")
                print(f"   BTC Sold: {order['amount']:.6f} BTC")
                print(f"   USD Received: ${order['cost']:.2f}" if order['cost'] else f"Estimated: ${btc_amount * current_price:.2f}")
                
                return order_result
                
            except Exception as e:
                print(f"❌ Sell order failed: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'mode': 'live'
                }

    def get_account_balance(exchange, paper_mode=True):
        """
        Get current account balance from Binance or simulate for paper trading.
        
        Returns current USDT and BTC balances for portfolio management.
        
        Parameters:
        -----------
        exchange : ccxt.Exchange or None
            Binance exchange client
        paper_mode : bool, default=True
            Whether to simulate balance (True) or fetch live (False)
        
        Returns:
        --------
        dict : Account balance information
        """
        
        if paper_mode:
            # Return simulated balances
            return {
                'USDT': {'free': 10000.0, 'used': 0.0, 'total': 10000.0},
                'BTC': {'free': 0.0, 'used': 0.0, 'total': 0.0},
                'mode': 'paper'
            }
        
        else:
            try:
                balance = exchange.fetch_balance()
                return {
                    'USDT': balance.get('USDT', {'free': 0, 'used': 0, 'total': 0}),
                    'BTC': balance.get('BTC', {'free': 0, 'used': 0, 'total': 0}),
                    'mode': 'live'
                }
            except Exception as e:
                print(f"❌ Failed to fetch balance: {e}")
                return None

    # Initialize Binance client
    print("🔄 Initializing Binance trading client...")
    try:
        global binance_exchange, is_paper_mode
        binance_exchange, is_paper_mode = initialize_binance_client()
        
        if binance_exchange or is_paper_mode:
            print("✅ Binance client initialized successfully")
            
            # Test balance fetch
            balance_info = get_account_balance(binance_exchange, is_paper_mode)
            if balance_info:
                print(f"💰 Account Balance ({balance_info['mode']} mode):")
                print(f"   USDT: ${balance_info['USDT']['free']:,.2f}")
                print(f"   BTC: {balance_info['BTC']['free']:.6f}")
        else:
            print("❌ Failed to initialize Binance client")
            binance_exchange = None
            is_paper_mode = True
            
    except Exception as e:
        print(f"❌ Binance initialization failed: {e}")
        binance_exchange = None
        is_paper_mode = True

# ----------------------------------------------------------------------------
# Cell 6: Portfolio Management
# ----------------------------------------------------------------------------

def cell6_portfolio_management():
    """
    Cell 6: Portfolio Management (Workflow Step 6)
    State persistence and portfolio tracking with JSON storage
    """

    def create_default_portfolio(total_budget=1000.0):
        """
        Create a default portfolio state structure.
        
        Initializes a new portfolio with default values for fresh trading sessions.
        
        Parameters:
        -----------
        total_budget : float, default=1000.0
            Total trading budget allocation
        
        Returns:
        --------
        dict : Default portfolio state structure
        """
        
        return {
            'total_budget': total_budget,
            'used_budget': 0.0,
            'btc_holdings': 0.0,
            'last_buy_price': 0.0,
            'trades': [],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_fees_paid': 0.0,
            'max_drawdown_pct': 0.0,
            'unrealized_pnl': 0.0,
            'realized_pnl': 0.0
        }

    def load_portfolio(file_path='portfolio_state.json'):
        """
        Load portfolio state from JSON file.
        
        Loads existing portfolio state or creates a new one if file doesn't exist.
        
        Parameters:
        -----------
        file_path : str, default='portfolio_state.json'
            Path to portfolio state JSON file
        
        Returns:
        --------
        dict : Portfolio state dictionary
        """
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    portfolio = json.load(f)
                
                print(f"📂 Portfolio loaded from {file_path}")
                print(f"   Total Budget: ${portfolio['total_budget']:,.2f}")
                print(f"   Used Budget: ${portfolio['used_budget']:,.2f} ({(portfolio['used_budget']/portfolio['total_budget']*100):.1f}%)")
                print(f"   BTC Holdings: {portfolio['btc_holdings']:.6f} BTC")
                print(f"   Total Trades: {portfolio.get('total_trades', len(portfolio['trades']))}")
                print(f"   Last Updated: {portfolio.get('last_updated', 'Unknown')}")
                
                return portfolio
            else:
                # Create new portfolio
                budget = float(os.getenv('TRADING_BUDGET', '1000'))
                portfolio = create_default_portfolio(budget)
                
                print(f"🆕 Creating new portfolio with ${budget:,.2f} budget")
                
                # Save the new portfolio
                save_portfolio(portfolio, file_path)
                
                return portfolio
                
        except Exception as e:
            print(f"❌ Error loading portfolio: {e}")
            print("Creating fresh portfolio state...")
            
            budget = float(os.getenv('TRADING_BUDGET', '1000'))
            return create_default_portfolio(budget)

    def save_portfolio(portfolio, file_path='portfolio_state.json'):
        """
        Save portfolio state to JSON file.
        
        Persists current portfolio state with timestamp and backup.
        
        Parameters:
        -----------
        portfolio : dict
            Portfolio state to save
        file_path : str, default='portfolio_state.json'
            Path to save portfolio state
        """
        
        try:
            # Update timestamp
            portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Create backup if file exists
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                os.rename(file_path, backup_path)
            
            # Save new state
            with open(file_path, 'w') as f:
                json.dump(portfolio, f, indent=2, default=str)
            
            print(f"💾 Portfolio saved to {file_path}")
            
        except Exception as e:
            print(f"❌ Error saving portfolio: {e}")

    def update_portfolio_after_buy(portfolio, order_result, market_data, stop_loss_info):
        """
        Update portfolio state after a successful buy order.
        
        Updates budget allocation, holdings, and trade records.
        
        Parameters:
        -----------
        portfolio : dict
            Current portfolio state
        order_result : dict
            Buy order execution result
        market_data : dict
            Current market data
        stop_loss_info : dict
            Stop-loss calculation details
        
        Returns:
        --------
        dict : Updated portfolio state
        """
        
        if not order_result['success']:
            print("❌ Cannot update portfolio - buy order failed")
            return portfolio
        
        # Calculate trade cost including fees
        trade_cost = order_result['btc_amount'] * order_result['actual_price'] + order_result['fees']
        
        # Update portfolio balances
        portfolio['used_budget'] += trade_cost
        portfolio['btc_holdings'] += order_result['btc_amount']
        portfolio['last_buy_price'] = order_result['actual_price']
        portfolio['total_fees_paid'] += order_result['fees']
        portfolio['total_trades'] = portfolio.get('total_trades', 0) + 1
        
        # Create trade record
        trade_record = {
            'trade_id': len(portfolio['trades']) + 1,
            'type': 'buy',
            'timestamp': order_result['timestamp'],
            'order_id': order_result['order_id'],
            'btc_amount': order_result['btc_amount'],
            'price': order_result['actual_price'],
            'cost': trade_cost,
            'fees': order_result['fees'],
            'stop_loss_price': stop_loss_info['stop_loss_price'],
            'atr_value': stop_loss_info['atr_value'],
            'rsi_at_entry': market_data['rsi'],
            'market_sentiment': market_data.get('sentiment', 'unknown'),
            'status': 'open'
        }
        
        portfolio['trades'].append(trade_record)
        
        # Calculate current portfolio value
        current_btc_value = portfolio['btc_holdings'] * market_data['price']
        available_budget = portfolio['total_budget'] - portfolio['used_budget']
        portfolio_value = current_btc_value + available_budget
        
        # Calculate unrealized P&L
        total_cost = sum(trade['cost'] for trade in portfolio['trades'] if trade['type'] == 'buy' and trade['status'] == 'open')
        portfolio['unrealized_pnl'] = current_btc_value - total_cost
        
        print(f"📈 Portfolio Updated After Buy:")
        print(f"   BTC Holdings: {portfolio['btc_holdings']:.6f} BTC")
        print(f"   Used Budget: ${portfolio['used_budget']:,.2f}")
        print(f"   Portfolio Value: ${portfolio_value:,.2f}")
        print(f"   Unrealized P&L: ${portfolio['unrealized_pnl']:+,.2f}")
        
        return portfolio

    def update_portfolio_after_sell(portfolio, order_result, trade_to_close, market_data):
        """
        Update portfolio state after a successful sell order.
        
        Updates holdings, calculates realized P&L, and closes trade record.
        
        Parameters:
        -----------
        portfolio : dict
            Current portfolio state
        order_result : dict
            Sell order execution result
        trade_to_close : dict
            Original buy trade being closed
        market_data : dict
            Current market data
        
        Returns:
        --------
        dict : Updated portfolio state
        """
        
        if not order_result['success']:
            print("❌ Cannot update portfolio - sell order failed")
            return portfolio
        
        # Update portfolio balances
        portfolio['btc_holdings'] -= order_result['btc_amount']
        portfolio['btc_holdings'] = max(0, portfolio['btc_holdings'])  # Prevent negative holdings
        portfolio['total_fees_paid'] += order_result['fees']
        
        # Calculate realized P&L
        buy_cost = trade_to_close['cost']
        sell_proceeds = order_result['usd_received']
        realized_pnl = sell_proceeds - buy_cost
        portfolio['realized_pnl'] += realized_pnl
        
        # Update trade record
        for trade in portfolio['trades']:
            if trade['trade_id'] == trade_to_close['trade_id']:
                trade['status'] = 'closed'
                trade['exit_timestamp'] = order_result['timestamp']
                trade['exit_price'] = order_result['actual_price']
                trade['exit_order_id'] = order_result['order_id']
                trade['realized_pnl'] = realized_pnl
                break
        
        # Update win/loss statistics
        if realized_pnl > 0:
            portfolio['winning_trades'] = portfolio.get('winning_trades', 0) + 1
        else:
            portfolio['losing_trades'] = portfolio.get('losing_trades', 0) + 1
        
        # Recalculate unrealized P&L for remaining holdings
        if portfolio['btc_holdings'] > 0:
            remaining_cost = sum(trade['cost'] for trade in portfolio['trades'] if trade['type'] == 'buy' and trade['status'] == 'open')
            current_value = portfolio['btc_holdings'] * market_data['price']
            portfolio['unrealized_pnl'] = current_value - remaining_cost
        else:
            portfolio['unrealized_pnl'] = 0.0
        
        print(f"📉 Portfolio Updated After Sell:")
        print(f"   BTC Holdings: {portfolio['btc_holdings']:.6f} BTC")
        print(f"   Realized P&L: ${realized_pnl:+,.2f}")
        print(f"   Total Realized P&L: ${portfolio['realized_pnl']:+,.2f}")
        print(f"   Unrealized P&L: ${portfolio['unrealized_pnl']:+,.2f}")
        
        return portfolio

    def calculate_portfolio_metrics(portfolio, current_btc_price):
        """
        Calculate comprehensive portfolio performance metrics.
        
        Computes various performance indicators for portfolio analysis.
        
        Parameters:
        -----------
        portfolio : dict
            Current portfolio state
        current_btc_price : float
            Current Bitcoin price
        
        Returns:
        --------
        dict : Portfolio metrics and performance indicators
        """
        
        # Calculate current portfolio value
        btc_value = portfolio['btc_holdings'] * current_btc_price
        available_cash = portfolio['total_budget'] - portfolio['used_budget']
        total_portfolio_value = btc_value + available_cash
        
        # Calculate total returns
        total_invested = portfolio['used_budget']
        total_pnl = portfolio['realized_pnl'] + portfolio['unrealized_pnl']
        
        # Calculate percentages
        budget_utilization = (portfolio['used_budget'] / portfolio['total_budget']) * 100
        portfolio_return_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        # Win rate calculation
        total_closed_trades = portfolio.get('winning_trades', 0) + portfolio.get('losing_trades', 0)
        win_rate = (portfolio.get('winning_trades', 0) / total_closed_trades * 100) if total_closed_trades > 0 else 0
        
        # Average trade analysis
        closed_trades = [trade for trade in portfolio['trades'] if trade.get('status') == 'closed']
        avg_trade_pnl = sum(trade.get('realized_pnl', 0) for trade in closed_trades) / len(closed_trades) if closed_trades else 0
        
        metrics = {
            'total_portfolio_value': total_portfolio_value,
            'btc_value': btc_value,
            'available_cash': available_cash,
            'total_pnl': total_pnl,
            'portfolio_return_pct': portfolio_return_pct,
            'budget_utilization_pct': budget_utilization,
            'win_rate_pct': win_rate,
            'total_trades': portfolio.get('total_trades', 0),
            'winning_trades': portfolio.get('winning_trades', 0),
            'losing_trades': portfolio.get('losing_trades', 0),
            'avg_trade_pnl': avg_trade_pnl,
            'total_fees_paid': portfolio.get('total_fees_paid', 0)
        }
        
        return metrics

    def check_risk_limits(portfolio, current_btc_price, max_drawdown_pct=25.0):
        """
        Check if portfolio exceeds risk management limits.
        
        Evaluates portfolio against maximum drawdown and other risk parameters.
        
        Parameters:
        -----------
        portfolio : dict
            Current portfolio state
        current_btc_price : float
            Current Bitcoin price
        max_drawdown_pct : float, default=25.0
            Maximum allowed portfolio drawdown percentage
        
        Returns:
        --------
        dict : Risk assessment results
        """
        
        metrics = calculate_portfolio_metrics(portfolio, current_btc_price)
        
        # Calculate current drawdown
        peak_value = portfolio['total_budget']  # Starting budget as peak
        current_value = metrics['total_portfolio_value']
        current_drawdown = ((peak_value - current_value) / peak_value * 100) if peak_value > 0 else 0
        
        # Risk checks
        risk_violations = []
        
        if current_drawdown > max_drawdown_pct:
            risk_violations.append(f"Drawdown {current_drawdown:.1f}% exceeds limit {max_drawdown_pct}%")
        
        if metrics['budget_utilization_pct'] > 95:
            risk_violations.append(f"Budget utilization {metrics['budget_utilization_pct']:.1f}% too high")
        
        risk_status = {
            'current_drawdown_pct': current_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'risk_violations': risk_violations,
            'risk_level': 'HIGH' if risk_violations else 'NORMAL',
            'trading_allowed': len(risk_violations) == 0
        }
        
        if risk_violations:
            print(f"🚨 RISK ALERT:")
            for violation in risk_violations:
                print(f"   {violation}")
        
        return risk_status

    # Test portfolio management functions
    print("🧪 Testing Portfolio Management...")
    try:
        # Load or create portfolio
        test_portfolio = load_portfolio('test_portfolio.json')
        
        # Calculate metrics if we have market data
        if 'test_market_data' in locals():
            metrics = calculate_portfolio_metrics(test_portfolio, test_market_data['price'])
            
            print(f"📊 Portfolio Metrics:")
            print(f"   Total Value: ${metrics['total_portfolio_value']:,.2f}")
            print(f"   Total P&L: ${metrics['total_pnl']:+,.2f} ({metrics['portfolio_return_pct']:+.2f}%)")
            print(f"   Budget Utilization: {metrics['budget_utilization_pct']:.1f}%")
            print(f"   Win Rate: {metrics['win_rate_pct']:.1f}%")
            
            # Check risk limits
            risk_status = check_risk_limits(test_portfolio, test_market_data['price'])
            print(f"   Risk Level: {risk_status['risk_level']}")
            
        print("✅ Portfolio management functions tested successfully")
        
    except Exception as e:
        print(f"❌ Portfolio management test failed: {e}")

# ----------------------------------------------------------------------------
# Cell 7: Main Trading Loop
# ----------------------------------------------------------------------------

def cell7_main_trading_loop():
    """
    Cell 7: Main Trading Loop (Workflow Step 7)
    Orchestrate the complete trading system with error handling and logging
    """

    def main_trading_cycle(portfolio_file='portfolio_state.json', symbol='BTC/USDT'):
        """
        Execute one complete trading cycle.
        
        Orchestrates data collection, LLM analysis, DCA evaluation, and trade execution
        for a single trading iteration with comprehensive error handling.
        
        Parameters:
        -----------
        portfolio_file : str, default='portfolio_state.json'
            Path to portfolio state file
        symbol : str, default='BTC/USDT'
            Trading symbol for Binance
        
        Returns:
        --------
        dict : Cycle results with execution summary
        """
        
        cycle_start_time = datetime.now()
        print(f"🔄 Starting Trading Cycle at {cycle_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        cycle_results = {
            'timestamp': cycle_start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'success': False,
            'actions_taken': [],
            'errors': [],
            'market_data': None,
            'llm_analysis': None,
            'dca_decision': None,
            'trades_executed': [],
            'portfolio_metrics': None
        }
        
        try:
            # Step 1: Load Portfolio State
            print("📂 Step 1: Loading portfolio state...")
            portfolio = load_portfolio(portfolio_file)
            cycle_results['actions_taken'].append("Portfolio loaded")
            
            # Step 2: Parse Market Data
            print("\n📊 Step 2: Parsing market data...")
            try:
                market_data = parse_market_data()  # Assuming this function is defined elsewhere or needs implementation
                cycle_results['market_data'] = market_data
                cycle_results['actions_taken'].append("Market data parsed")
                print(f"   Current BTC Price: ${market_data['price']:,.2f}")
            except Exception as e:
                error_msg = f"Market data parsing failed: {e}"
                print(f"❌ {error_msg}")
                cycle_results['errors'].append(error_msg)
                return cycle_results
            
            # Step 3: Get LLM Analysis
            print("\n🧠 Step 3: Getting LLM market analysis...")
            try:
                if groq_client:
                    llm_analysis = get_llm_market_analysis(groq_client, market_data, portfolio)
                    cycle_results['llm_analysis'] = llm_analysis
                    cycle_results['actions_taken'].append("LLM analysis completed")
                else:
                    print("⚠️  Groq client not available, using default analysis")
                    llm_analysis = {
                        'sentiment': 'neutral',
                        'recommendation': 'hold',
                        'confidence': 0.5,
                        'reasoning': 'LLM unavailable, using conservative default',
                        'position_size_modifier': 1.0,
                        'risk_level': 'medium'
                    }
                    cycle_results['llm_analysis'] = llm_analysis
            except Exception as e:
                error_msg = f"LLM analysis failed: {e}"
                print(f"❌ {error_msg}")
                cycle_results['errors'].append(error_msg)
                # Use default analysis
                llm_analysis = {
                    'sentiment': 'neutral',
                    'recommendation': 'hold',
                    'confidence': 0.3,
                    'reasoning': f'LLM error: {str(e)[:50]}',
                    'position_size_modifier': 1.0,
                    'risk_level': 'high'
                }
            
            # Step 4: Check Risk Limits
            print("\n🛡️  Step 4: Checking risk limits...")
            risk_status = check_risk_limits(portfolio, market_data['price'])
            
            if not risk_status['trading_allowed']:
                print("🚨 Trading halted due to risk limits")
                cycle_results['actions_taken'].append("Trading halted - risk limits exceeded")
                cycle_results['success'] = True  # Successful risk management
                return cycle_results
            
            # Step 5: Evaluate DCA Triggers
            print("\n🧮 Step 5: Evaluating DCA triggers...")
            try:
                dca_decision = should_trigger_dca(market_data, portfolio, llm_analysis)
                cycle_results['dca_decision'] = dca_decision
                cycle_results['actions_taken'].append("DCA evaluation completed")
            except Exception as e:
                error_msg = f"DCA evaluation failed: {e}"
                print(f"❌ {error_msg}")
                cycle_results['errors'].append(error_msg)
                return cycle_results
            
            # Step 6: Execute Trades if Triggered
            if dca_decision['should_buy']:
                print("\n💳 Step 6: Executing BUY order...")
                try:
                    # Calculate position size
                    position_info = calculate_position_size(portfolio, llm_analysis)
                    
                    # Calculate stop-loss
                    stop_loss_info = calculate_atr_stop_loss(market_data['price'], market_data['atr'])
                    
                    # Execute buy order
                    buy_result = execute_buy_order(
                        binance_exchange, 
                        symbol, 
                        position_info['trade_amount'], 
                        market_data['price'], 
                        is_paper_mode
                    )
                    
                    if buy_result['success']:
                        # Update portfolio
                        portfolio = update_portfolio_after_buy(
                            portfolio, buy_result, market_data, stop_loss_info
                        )
                        
                        # Save updated portfolio
                        save_portfolio(portfolio, portfolio_file)
                        
                        cycle_results['trades_executed'].append({
                            'type': 'buy',
                            'result': buy_result,
                            'position_info': position_info,
                            'stop_loss_info': stop_loss_info
                        })
                        
                        cycle_results['actions_taken'].append("Buy order executed and portfolio updated")
                    else:
                        error_msg = f"Buy order failed: {buy_result.get('error', 'Unknown error')}"
                        print(f"❌ {error_msg}")
                        cycle_results['errors'].append(error_msg)
                        
                except Exception as e:
                    error_msg = f"Trade execution failed: {e}"
                    print(f"❌ {error_msg}")
                    cycle_results['errors'].append(error_msg)
            
            # Step 7: Check Stop-Loss for Existing Positions
            print("\n🛡️  Step 7: Checking stop-loss conditions...")
            try:
                open_trades = [trade for trade in portfolio['trades'] if trade.get('status') == 'open']
                
                for trade in open_trades:
                    stop_decision = should_trigger_stop_loss(
                        market_data['price'],
                        trade['price'],
                        trade['stop_loss_price'],
                        market_data
                    )
                    
                    if stop_decision['should_stop']:
                        print(f"🚨 Stop-loss triggered for trade {trade['trade_id']}")
                        
                        # Execute sell order
                        sell_result = execute_sell_order(
                            binance_exchange,
                            symbol,
                            trade['btc_amount'],
                            market_data['price'],
                            is_paper_mode
                        )
                        
                        if sell_result['success']:
                            # Update portfolio
                            portfolio = update_portfolio_after_sell(
                                portfolio, sell_result, trade, market_data
                            )
                            
                            # Save updated portfolio
                            save_portfolio(portfolio, portfolio_file)
                            
                            cycle_results['trades_executed'].append({
                                'type': 'stop_loss_sell',
                                'result': sell_result,
                                'original_trade': trade
                            })
                            
                            cycle_results['actions_taken'].append(f"Stop-loss executed for trade {trade['trade_id']}")
                        else:
                            error_msg = f"Stop-loss sell failed: {sell_result.get('error', 'Unknown error')}"
                            print(f"❌ {error_msg}")
                            cycle_results['errors'].append(error_msg)
                            
            except Exception as e:
                error_msg = f"Stop-loss check failed: {e}"
                print(f"❌ {error_msg}")
                cycle_results['errors'].append(error_msg)
            
            # Step 8: Calculate Final Portfolio Metrics
            print("\n📊 Step 8: Calculating portfolio metrics...")
            try:
                portfolio_metrics = calculate_portfolio_metrics(portfolio, market_data['price'])
                cycle_results['portfolio_metrics'] = portfolio_metrics
                cycle_results['actions_taken'].append("Portfolio metrics calculated")
                
                print(f"💼 Portfolio Summary:")
                print(f"   Total Value: ${portfolio_metrics['total_portfolio_value']:,.2f}")
                print(f"   Total P&L: ${portfolio_metrics['total_pnl']:+,.2f} ({portfolio_metrics['portfolio_return_pct']:+.2f}%)")
                print(f"   BTC Holdings: {portfolio['btc_holdings']:.6f} BTC")
                print(f"   Budget Utilization: {portfolio_metrics['budget_utilization_pct']:.1f}%")
                
            except Exception as e:
                error_msg = f"Portfolio metrics calculation failed: {e}"
                print(f"❌ {error_msg}")
                cycle_results['errors'].append(error_msg)
            
            # Mark cycle as successful
            cycle_results['success'] = True
            
        except Exception as e:
            error_msg = f"Critical trading cycle error: {e}"
            print(f"❌ {error_msg}")
            cycle_results['errors'].append(error_msg)
        
        # Calculate cycle duration
        cycle_end_time = datetime.now()
        cycle_duration = (cycle_end_time - cycle_start_time).total_seconds()
        cycle_results['duration_seconds'] = cycle_duration
        
        print("\n" + "=" * 60)
        print(f"🏁 Trading Cycle Complete")
        print(f"   Duration: {cycle_duration:.1f} seconds")
        print(f"   Success: {'✅ YES' if cycle_results['success'] else '❌ NO'}")
        print(f"   Actions: {len(cycle_results['actions_taken'])}")
        print(f"   Errors: {len(cycle_results['errors'])}")
        print(f"   Trades: {len(cycle_results['trades_executed'])}")
        
        return cycle_results

    def run_trading_bot(cycles=None, cycle_interval_minutes=30, portfolio_file='portfolio_state.json'):
        """
        Run the trading bot for multiple cycles or continuously.
        
        Executes the main trading loop with specified intervals and cycle limits.
        
        Parameters:
        -----------
        cycles : int or None, default=None
            Number of cycles to run (None for continuous operation)
        cycle_interval_minutes : int, default=30
            Minutes between trading cycles
        portfolio_file : str, default='portfolio_state.json'
            Path to portfolio state file
        """
        
        print("🚀 BITCOIN TRADING BOT STARTING")
        print("=" * 60)
        print(f"Mode: {'Paper Trading' if is_paper_mode else 'Live Trading'}")
        print(f"Cycle Interval: {cycle_interval_minutes} minutes")
        print(f"Max Cycles: {cycles if cycles else 'Continuous'}")
        print(f"Portfolio File: {portfolio_file}")
        print("=" * 60)
        
        cycle_count = 0
        total_errors = 0
        total_trades = 0
        
        try:
            while True:
                cycle_count += 1
                
                print(f"\n🔄 CYCLE {cycle_count}")
                if cycles:
                    print(f"   Progress: {cycle_count}/{cycles}")
                
                # Execute trading cycle
                cycle_result = main_trading_cycle(portfolio_file)
                
                # Update statistics
                total_errors += len(cycle_result['errors'])
                total_trades += len(cycle_result['trades_executed'])
                
                # Log cycle summary
                print(f"\n📋 Cycle {cycle_count} Summary:")
                print(f"   Timestamp: {cycle_result['timestamp']}")
                print(f"   Success: {cycle_result['success']}")
                print(f"   Duration: {cycle_result.get('duration_seconds', 0):.1f}s")
                print(f"   Actions: {', '.join(cycle_result['actions_taken'][:3])}{'...' if len(cycle_result['actions_taken']) > 3 else ''}")
                
                if cycle_result['trades_executed']:
                    for trade in cycle_result['trades_executed']:
                        print(f"   Trade: {trade['type']} - {trade['result']['order_id']}")
                
                if cycle_result['errors']:
                    print(f"   Errors: {'; '.join(cycle_result['errors'][:2])}")
                
                # Check if we've reached the cycle limit
                if cycles and cycle_count >= cycles:
                    break
                
                # Wait for next cycle
                print(f"\n⏳ Waiting {cycle_interval_minutes} minutes until next cycle...")
                print(f"   Next cycle at: {(datetime.now() + pd.Timedelta(minutes=cycle_interval_minutes)).strftime('%H:%M:%S')}")
                
                # In notebook environment, we break after one cycle for testing
                # In production, you would use: time.sleep(cycle_interval_minutes * 60)
                print("\n⚠️  Breaking after one cycle for notebook testing")
                print("   Remove this break for continuous operation")
                break
                
        except KeyboardInterrupt:
            print("\n🛑 Trading bot stopped by user")
        except Exception as e:
            print(f"\n❌ Trading bot crashed: {e}")
        
        finally:
            print("\n" + "=" * 60)
            print("🏁 TRADING BOT SESSION COMPLETE")
            print(f"Total Cycles: {cycle_count}")
            print(f"Total Trades: {total_trades}")
            print(f"Total Errors: {total_errors}")
            print(f"Success Rate: {((cycle_count - total_errors) / cycle_count * 100):.1f}%" if cycle_count > 0 else "N/A")
            print("=" * 60)

    # Test the complete trading system
    print("🧪 Testing Complete Trading System...")
    print("\nExecuting one trading cycle for demonstration...")

    try:
        # Run one cycle for testing
        test_result = main_trading_cycle('test_portfolio.json')
        
        if test_result['success']:
            print("\n✅ Trading system test completed successfully!")
            print("\n🚀 Ready to run trading bot!")
            print("\nTo start continuous trading, run:")
            print("   run_trading_bot(cycles=None, cycle_interval_minutes=30)")
            print("\nTo run for limited cycles, run:")
            print("   run_trading_bot(cycles=10, cycle_interval_minutes=30)")
        else:
            print("\n⚠️  Trading system test completed with issues")
            print(f"Errors encountered: {test_result['errors']}")
            
    except Exception as e:
        print(f"\n❌ Trading system test failed: {e}")
        print("Please check your configuration and try again")

    print("\n" + "=" * 60)
    print("🎯 BITCOIN TRADING BOT READY")
    print("=" * 60)
    print("Key Features Implemented:")
    print("✅ Multi-source data collection with technical indicators")
    print("✅ Llama 4 Maverick LLM market analysis")
    print("✅ Enhanced DCA strategy with RSI and LLM triggers")
    print("✅ ATR-based dynamic stop-loss system")
    print("✅ Binance API integration (Paper/Live trading)")
    print("✅ JSON-based portfolio state persistence")
    print("✅ Comprehensive risk management")
    print("✅ Error handling and recovery")
    print("✅ Performance tracking and metrics")
    print("\nTo start trading: run_trading_bot()")

# ----------------------------------------------------------------------------
# Main Function to Run the Whole Thing
# ----------------------------------------------------------------------------

def main():
    cell1_setup_environment()
    # cell2_data_collection_parsing()
    # cell3_llm_market_analysis()
    # cell4_enhanced_dca_strategy()
    # cell5_trade_execution()
    # cell6_portfolio_management()
    # cell7_main_trading_loop()

if __name__ == "__main__":
    # Uncomment the function calls below to test individual parts
    # cell1_setup_environment()
    # cell2_data_collection_parsing()
    # cell3_llm_market_analysis()
    # cell4_enhanced_dca_strategy()
    # cell5_trade_execution()
    # cell6_portfolio_management()
    # cell7_main_trading_loop()

    # Run the entire bot
    main()
