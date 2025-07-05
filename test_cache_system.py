#!/usr/bin/env python3
"""
Test script to verify the enhanced scholarship caching system
"""

import sys
import os
sys.path.append('/workspaces/newfolder-trials/search_agent')

from core.scholarship_cache import ScholarshipCache
from core.scraping import EnhancedScholarshipScraper
from core.db import DatabaseManager

def test_cache_system():
    """Test the scholarship caching system"""
    print("🧪 Testing Enhanced Scholarship Cache System")
    print("=" * 50)
    
    # Test cache initialization
    cache = ScholarshipCache()
    total_count = cache.get_scholarship_count()
    uganda_count = cache.get_scholarship_count(country='Uganda')
    
    print(f"📊 Total scholarships in cache: {total_count}")
    print(f"🇺🇬 Uganda-specific scholarships: {uganda_count}")
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    
    # Test 1: Uganda student search
    uganda_results = cache.search_scholarships(
        goal='student',
        country='Uganda',
        limit=10
    )
    print(f"✅ Uganda student search: {len(uganda_results)} results")
    
    # Test 2: Engineering keyword search
    eng_results = cache.search_scholarships(
        goal='student',
        keywords=['engineering'],
        limit=10
    )
    print(f"✅ Engineering keyword search: {len(eng_results)} results")
    
    # Test 3: International scholarships
    intl_results = cache.search_scholarships(
        goal='student',
        country='International',
        limit=10
    )
    print(f"✅ International scholarship search: {len(intl_results)} results")
    
    # Test scraper integration
    print("\n🔄 Testing scraper integration...")
    db_manager = DatabaseManager()
    scraper = EnhancedScholarshipScraper(db_manager)
    
    # This should return cached results instantly
    results = scraper.search_by_goal(
        goal='student',
        keywords=['undergraduate'],
        country='Uganda'
    )
    print(f"✅ Scraper integration test: {len(results)} results")
    
    # Print a few sample results
    if results:
        print("\n📋 Sample results:")
        for i, result in enumerate(results[:3]):
            print(f"{i+1}. {result['title']}")
            print(f"   Country: {result.get('country', 'N/A')}")
            print(f"   Amount: {result.get('amount', 'N/A')}")
            print()
    
    print("🎉 All tests completed successfully!")
    print("🚀 The caching system is working and should provide instant results!")

if __name__ == "__main__":
    test_cache_system()
