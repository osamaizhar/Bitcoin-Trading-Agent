"""
Bitcoin Data Collection - Usage Examples

This file demonstrates how to use the modular data collection functions.
"""

from data_collection_modular import *

# =============================================================================
# BASIC USAGE EXAMPLES
# =============================================================================

def example_1_setup_environment():
    """Example 1: Setup environment and check configuration"""
    print("Example 1: Setup Environment")
    print("-" * 40)
    
    # Setup environment
    env_config = setup_environment()
    print(f"Environment loaded: {env_config.get('env_loaded')}")
    
    # Create directories
    dirs = create_data_directories()
    print(f"Data directory created: {'data' in dirs}")
    
    # Load configuration
    config = load_configuration()
    print(f"Available sources: {len(config.get('available_sources', []))}")
    
    return env_config, dirs, config

def example_2_collect_single_source():
    """Example 2: Collect data from a single source"""
    print("\nExample 2: Collect from Single Source")
    print("-" * 40)
    
    # Collect Yahoo Finance data
    yahoo_result = run_individual_source('yahoo', period='1mo')
    
    if yahoo_result['success']:
        data = yahoo_result['data']
        print(f"✅ Yahoo data collected: {len(data)} records")
        print(f"Date range: {data['date'].min()} to {data['date'].max()}")
        print(f"Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    else:
        print(f"❌ Yahoo collection failed: {yahoo_result.get('error')}")
    
    return yahoo_result

def example_3_collect_coinmarketcap():
    """Example 3: Collect current data from CoinMarketCap"""
    print("\nExample 3: Collect CoinMarketCap Current Data")
    print("-" * 40)
    
    cmc_result = run_individual_source('coinmarketcap')
    
    if cmc_result['success']:
        data = cmc_result['data']
        print(f"✅ CoinMarketCap data collected")
        print(f"Current price: ${data['price']:,.2f}")
        print(f"24h change: {data['percent_change_24h']:.2f}%")
        print(f"Market cap: ${data['market_cap']:,.0f}")
    else:
        print(f"❌ CoinMarketCap failed: {cmc_result.get('error')}")
    
    return cmc_result

def example_4_full_collection():
    """Example 4: Run full collection pipeline"""
    print("\nExample 4: Full Collection Pipeline")
    print("-" * 40)
    
    # Run full collection with specific sources
    sources_to_try = ['yahoo', 'coinmarketcap', 'investing_fallback']
    
    full_result = run_full_collection(
        period='1mo',
        data_dir='../data',
        sources=sources_to_try
    )
    
    # Print summary
    summary = full_result['summary']
    print(f"\n📊 Collection Summary:")
    print(f"Successful sources: {len(summary['sources_successful'])}/{len(summary['sources_attempted'])}")
    print(f"Total records: {summary['total_records']}")
    
    if summary['sources_successful']:
        print("✅ Successful sources:", ", ".join(summary['sources_successful']))
    
    if summary['sources_failed']:
        print("❌ Failed sources:", ", ".join(summary['sources_failed']))
    
    return full_result

def example_5_data_quality_check():
    """Example 5: Perform data quality checks"""
    print("\nExample 5: Data Quality Assessment")  
    print("-" * 40)
    
    # First collect some data
    yahoo_result = run_individual_source('yahoo', period='3mo')
    
    if yahoo_result['success']:
        # Perform quality check
        quality_result = perform_data_quality_checks(yahoo_result['data'])
        
        if quality_result['success']:
            print(f"🏆 Data Quality Score: {quality_result['quality_score']}/100")
            print(f"Total issues found: {len(quality_result['issues'])}")
            
            if quality_result['issues']:
                print("Issues detected:")
                for issue in quality_result['issues']:
                    print(f"  - {issue}")
            else:
                print("✅ No data quality issues found!")
        else:
            print(f"❌ Quality check failed: {quality_result.get('error')}")
    else:
        print("❌ No data available for quality check")
    
    return quality_result if yahoo_result['success'] else None

def example_6_save_and_standardize():
    """Example 6: Collect, standardize and save multiple sources"""
    print("\nExample 6: Multi-source Collection and Standardization")
    print("-" * 40)
    
    # Collect from multiple sources
    yahoo_result = run_individual_source('yahoo', period='1mo')
    cmc_result = run_individual_source('coinmarketcap')
    
    # Prepare data for standardization
    dataframes_to_combine = []
    source_names = []
    
    if yahoo_result['success']:
        dataframes_to_combine.append(yahoo_result['data'])
        source_names.append('yahoo')
    
    # Note: CoinMarketCap returns current price, not historical data
    # So we'll just work with Yahoo data for this example
    
    if dataframes_to_combine:
        # Standardize data
        standardized_result = standardize_data_sources(
            *dataframes_to_combine,
            source_names=source_names,
            data_dir='../data'
        )
        
        if standardized_result['success']:
            combined_data = standardized_result['data']
            print(f"✅ Standardized data: {len(combined_data)} records")
            print(f"Sources processed: {standardized_result['sources_processed']}")
            
            # Save to files
            data_to_save = {'combined_standardized': combined_data}
            save_result = save_data_files(data_to_save, '../data')
            
            if save_result['success']:
                print(f"💾 Files saved: {len(save_result['files_saved'])}")
            
        else:
            print(f"❌ Standardization failed: {standardized_result.get('error')}")
    else:
        print("❌ No data sources available for standardization")

# =============================================================================
# ADVANCED USAGE EXAMPLES
# =============================================================================

def advanced_example_custom_pipeline():
    """Advanced: Create a custom data collection pipeline"""
    print("\nAdvanced Example: Custom Pipeline")
    print("-" * 40)
    
    # Step 1: Setup
    print("1. Environment setup...")
    env_config = setup_environment()
    
    # Step 2: Try multiple sources in priority order
    print("2. Collecting from priority sources...")
    
    priority_sources = ['yahoo', 'coinmarketcap', 'investing_fallback']
    successful_collections = {}
    
    for source in priority_sources:
        print(f"   Trying {source}...")
        result = run_individual_source(source, period='2mo')
        
        if result['success']:
            successful_collections[source] = result
            print(f"   ✅ {source} successful")
        else:
            print(f"   ❌ {source} failed: {result.get('error', 'Unknown error')[:50]}")
    
    # Step 3: Process successful collections
    print("3. Processing collected data...")
    
    if successful_collections:
        # Get historical data sources only
        historical_sources = []
        historical_names = []
        
        for source, result in successful_collections.items():
            if 'data' in result and result['data'] is not None:
                if len(result['data']) > 1:  # Historical data (more than 1 record)
                    historical_sources.append(result['data'])
                    historical_names.append(source)
        
        if historical_sources:
            # Standardize
            combined_result = standardize_data_sources(
                *historical_sources, 
                source_names=historical_names
            )
            
            # Quality check
            if combined_result['success']:
                quality_result = perform_data_quality_checks(combined_result['data'])
                
                print(f"4. Quality Assessment:")
                print(f"   Quality Score: {quality_result['quality_score']}/100")
                
                # Generate final summary
                print("5. Final Summary:")
                print(f"   Total records: {len(combined_result['data'])}")
                print(f"   Sources used: {', '.join(historical_names)}")
                print(f"   Date range: {combined_result['data']['date'].min()} to {combined_result['data']['date'].max()}")
                
                return {
                    'combined_data': combined_result,
                    'quality_assessment': quality_result,
                    'sources_used': historical_names
                }
        else:
            print("   No historical data sources available")
    else:
        print("   No successful data collections")
    
    return None

# =============================================================================
# RUN ALL EXAMPLES
# =============================================================================

def run_all_examples():
    """Run all usage examples"""
    print("🚀 Bitcoin Data Collection - Usage Examples")
    print("=" * 60)
    
    try:
        # Basic examples
        example_1_setup_environment()
        example_2_collect_single_source()
        example_3_collect_coinmarketcap()
        example_4_full_collection()
        example_5_data_quality_check()
        example_6_save_and_standardize()
        
        # Advanced example
        advanced_result = advanced_example_custom_pipeline()
        
        print("\n🎉 All examples completed!")
        print("\n💡 Next Steps:")
        print("- Use the collected data for trading strategy development")
        print("- Set up automated collection schedules")
        print("- Integrate with notification systems")
        print("- Add more data sources as needed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        return False

if __name__ == "__main__":
    """
    Run examples when script is executed directly
    """
    print("Select example to run:")
    print("1. Setup Environment")
    print("2. Single Source Collection")
    print("3. CoinMarketCap Collection") 
    print("4. Full Pipeline")
    print("5. Quality Check")
    print("6. Multi-source Standardization")
    print("7. Advanced Custom Pipeline")
    print("8. Run All Examples")
    
    choice = input("\nEnter choice (1-8): ").strip()
    
    examples = {
        '1': example_1_setup_environment,
        '2': example_2_collect_single_source,
        '3': example_3_collect_coinmarketcap,
        '4': example_4_full_collection,
        '5': example_5_data_quality_check,
        '6': example_6_save_and_standardize,
        '7': advanced_example_custom_pipeline,
        '8': run_all_examples
    }
    
    if choice in examples:
        examples[choice]()
    else:
        print("Invalid choice. Running all examples...")
        run_all_examples()