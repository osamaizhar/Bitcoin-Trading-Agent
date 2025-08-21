# """
# [Module Number: 5] LLM Decision Module for Bitcoin Trading Agent

# Purpose: Uses Moonshot via Groq API to generate dynamic trading suggestions.

# Inputs:
# - Market data from 01_data_collection (technical indicators, price data)
# - Configuration from 02_config_manager

# Outputs:
# - Trading suggestions (e.g., buy/sell with rationale)
# - Confidence scores for decisions

# Dependencies: groq, pandas, 01_data_collection
# """

# import os
# from groq import Groq
# from dotenv import load_dotenv
# import pandas as pd
# import asyncio
# from data_collection import collect_yahoo_async

# def initialize_groq_client():
#     """Initialize Groq client with API key."""
#     # Load environment variables for secure API access
#     load_dotenv()
#     api_key = os.getenv('GROQ_API_KEY')
#     if not api_key:
#         raise Exception("Groq API key missing in .env")
#     # Return initialized Groq client
#     return Groq(api_key=api_key)

# def generate_llm_prompt(yahoo_df, current_price, indicators):
#     """Generate prompt for Moonshot based on market data."""
#     # Construct detailed prompt with market data for LLM analysis
#     prompt = f"""
#     You are a Bitcoin trading assistant. Analyze the following market data and suggest a trading action (BUY, SELL, or HOLD) with a confidence score (0-100). Provide a brief rationale.

#     Current Price: ${current_price:,.2f}
#     ATR (14): ${indicators['atr_14']:,.2f}
#     RSI (14): {indicators['rsi_14']:.1f}
#     SMA 20: ${indicators['sma_20']:,.2f}
#     SMA 50: ${indicators['sma_50']:,.2f}
#     MACD: {indicators['macd']:.2f}
#     MACD Signal: {indicators['macd_signal']:.2f}
#     Recent Volume: {yahoo_df['volume'].iloc[-1]:,}
#     Price Change (24h): {(yahoo_df['close'].iloc[-1] - yahoo_df['close'].iloc[-2]) / yahoo_df['close'].iloc[-2] * 100:.2f}%

#     Suggest an action and confidence score. Format response as JSON:
#     ```json
#     {
#         "action": "BUY|SELL|HOLD",
#         "confidence": <0-100>,
#         "rationale": "<brief explanation>"
#     }
#     ```
#     """
#     return prompt

# def get_llm_decision(yahoo_df, current_price, indicators):
#     """Get trading decision from Moonshot via Groq API."""
#     try:
#         # Initialize Groq client
#         client = initialize_groq_client()
#         # Generate prompt with market data
#         prompt = generate_llm_prompt(yahoo_df, current_price, indicators)
#         # Query Moonshot model for trading decision
#         response = client.chat.completions.create(
#             model="llama3-8b-8192",  # Moonshot-compatible model
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=200
#         )
#         # Parse JSON response from LLM
#         decision = eval(response.choices[0].message.content.strip('```json\n```'))
#         print(f"[LLM] Decision: {decision['action']} ({decision['confidence']}%) - {decision['rationale']}")
#         return decision
#     except Exception as e:
#         # Handle LLM query errors
#         print(f"[ERROR] LLM decision failed: {e}")
#         return None

# if __name__ == "__main__":
#     """Test 05_llm_decision module with real market data."""
#     print("Testing 05_llm_decision module with real data...")
#     try:
#         # Fetch real market data
#         yahoo_df, current_price, indicators = asyncio.run(collect_yahoo_async())
#         if yahoo_df is None or current_price is None:
#             raise Exception("Failed to fetch market data")
        
#         # Get real LLM decision
#         decision = get_llm_decision(yahoo_df, current_price, indicators)
#         print(f"[TEST] LLM Decision: {decision}")
#     except Exception as e:
#         print(f"[TEST ERROR] {e}")




# # ------------------------- version 2 (GPT oss 120) -----------------------------------------------------
# """
# [Module Number:5] LLM Decision Module for Bitcoin Trading Agent

# Purpose: Uses Moonshot via Groq API to generate dynamic trading suggestions.

# Inputs:
# - Market data from data_collection01 (technical indicators, price data)
# - Configuration from 02_config_manager

# Outputs:
# - Trading suggestions (e.g., buy/sell with rationale)
# - Confidence scores for decisions

# Dependencies: groq, pandas, data_collection01
# """

# import os
# from groq import Groq
# from dotenv import load_dotenv
# import pandas as pd
# import asyncio
# from data_collection01 import generate_bitcoin_data_md

# def initialize_groq_client():
#  """Initialize Groq client with API key."""
#  # Load environment variables for secure API access
#  load_dotenv()
#  api_key = os.getenv('GROQ_API_KEY')
#  if not api_key:
#  raise Exception("Groq API key missing in .env")
#  # Return initialized Groq client
#  return Groq(api_key=api_key)

# def generate_llm_prompt(yahoo_df, current_price, indicators):
#  """Generate prompt for Moonshot based on market data."""
#  # Construct detailed prompt with market data for LLM analysis
#  prompt = f"""
#  You are a Bitcoin trading assistant. Analyze the following market data and suggest a trading action (BUY, SELL, or HOLD) with a confidence score (0-100). Provide a brief rationale.

#  Current Price: ${current_price:,.2f}
#  ATR (14): ${indicators['atr_14']:,.2f}
#  RSI (14): {indicators['rsi_14']:.1f}
#  SMA20: ${indicators['sma_20']:,.2f}
#  SMA50: ${indicators['sma_50']:,.2f}
#  MACD: {indicators['macd']:.2f}
#  MACD Signal: {indicators['macd_signal']:.2f}
#  Recent Volume: {yahoo_df['volume'].iloc[-1]:,}
#  Price Change (24h): {(yahoo_df['close'].iloc[-1] - yahoo_df['close'].iloc[-2]) / yahoo_df['close'].iloc[-2] *100:.2f}%

#  Suggest an action and confidence score. Format response as JSON:
#  ```json
#  {
#  "action": "BUY|SELL|HOLD",
#  "confidence": <0-100>,
#  "rationale": "<brief explanation>"
#  }


# ----------------------------- Version 3 ------------------------------
"""
[Module Number: 5] LLM Decision Module for Bitcoin Trading Agent

Purpose: Uses Moonshot via Groq API to generate dynamic trading suggestions.

Inputs:
- Market data from 01_data_collection (technical indicators, price data)
- Configuration from 02_config_manager

Outputs:
- Trading suggestions (e.g., buy/sell with rationale)
- Confidence scores for decisions

Dependencies: groq, pandas, 01_data_collection
"""

import os
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
import asyncio
# === NEW IMPORT ===
from data_collection_01 import generate_complete_bitcoin_data_md

# ... rest of file until __main__ ...

if __name__ == "__main__":
    """Test 05_llm_decision module with real market data."""
    print("Testing 05_llm_decision module with real data...")
    try:
        # === NEW CALL ===
        md_df = generate_complete_bitcoin_data_md()
        yahoo_df = md_df  # rename for downstream compatibility
        current_price = yahoo_df['close'].iloc[-1]
        indicators = {
            'atr_14': yahoo_df['atr_14'].iloc[-1],
            'rsi_14': yahoo_df['rsi_14'].iloc[-1],
            'sma_20': yahoo_df['sma_20'].iloc[-1],
            'sma_50': yahoo_df['sma_50'].iloc[-1],
            'macd': yahoo_df['macd'].iloc[-1],
            'macd_signal': yahoo_df['macd_signal'].iloc[-1],
        }
        # Get real LLM decision
        decision = get_llm_decision(yahoo_df, current_price, indicators)
        print(f"[TEST] LLM Decision: {decision}")
    except Exception as e:
        print(f"[TEST ERROR] {e}")