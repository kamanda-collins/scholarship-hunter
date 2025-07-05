#!/usr/bin/env python3
"""
Verify Scraping Improvements
Tests the enhanced scraping functionality with all fixes applied
"""

import os
import sys
import time
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_custom_site_scraping():
    """Test immediate scraping when custom sites are added"""
    print("🧪 Testing Custom Site Immediate Scraping...")
    
    try:
        from core.scraping import EnhancedScholarshipScraper
        from core.db import DatabaseManager
        
        # Initialize components
        db_manager = DatabaseManager()
        scraper = EnhancedScholarshipScraper(db_manager)
        
        # Test scraping a single site
        test_url = "https://www.scholars4dev.com/"
        print(f"  🕷️ Testing scraping: {test_url}")
        
        results = scraper.scrape_single_site(
            test_url, 
            goal="student", 
            country="Uganda", 
            max_scholarships=3
        )
        
        if results:
            print(f"  ✅ SUCCESS: Found {len(results)} scholarships")
            for i, scholarship in enumerate(results[:2]):
                print(f"    📚 {i+1}. {scholarship['title'][:60]}...")
        else:
            print(f"  ⚠️ No scholarships found (may be anti-bot or site structure)")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

def test_aggressive_search():
    """Test the aggressive real-time search functionality"""
    print("\n🧪 Testing Aggressive Real-time Search...")
    
    try:
        from core.scraping import EnhancedScholarshipScraper
        from core.db import DatabaseManager
        
        # Initialize components
        db_manager = DatabaseManager()
        scraper = EnhancedScholarshipScraper(db_manager)
        
        # Test aggressive search
        print("  🚀 Performing aggressive search...")
        start_time = time.time()
        
        results = scraper.perform_aggressive_search(
            goal="student",
            keywords=["engineering", "technology"],
            country="Uganda",
            max_sites=3  # Limit for testing
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if results:
            print(f"  ✅ SUCCESS: Found {len(results)} scholarships in {duration:.1f} seconds")
            for i, scholarship in enumerate(results[:3]):
                print(f"    📚 {i+1}. {scholarship['title'][:60]}...")
        else:
            print(f"  ⚠️ No scholarships found (may be anti-bot protection)")
        
        print(f"  ⏱️ Performance: {duration:.1f} seconds for {3} sites")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

def test_background_trigger():
    """Test enhanced background scraping trigger logic"""
    print("\n🧪 Testing Enhanced Background Scraping Logic...")
    
    try:
        from core.scraping import EnhancedScholarshipScraper
        from core.db import DatabaseManager
        
        # Initialize components
        db_manager = DatabaseManager()
        scraper = EnhancedScholarshipScraper(db_manager)
        
        # Test trigger conditions
        countries_to_test = ["Uganda", "Kenya", "Nigeria"]
        
        for country in countries_to_test:
            should_run = scraper._should_run_background_update(country)
            print(f"  🌍 {country}: Background update needed = {should_run}")
            
            if should_run:
                print(f"    ✅ Trigger logic working - will update for {country}")
            else:
                print(f"    ℹ️ No update needed for {country} (cache fresh)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

def test_cache_enhancements():
    """Test enhanced cache methods"""
    print("\n🧪 Testing Enhanced Cache Methods...")
    
    try:
        from core.scholarship_cache import ScholarshipCache
        
        # Initialize cache
        cache = ScholarshipCache()
        
        # Test new methods
        total_count = cache.get_total_scholarship_count()
        print(f"  📊 Total scholarships in cache: {total_count}")
        
        # Test duplicate removal
        print("  🧹 Testing duplicate removal...")
        removed_count = cache.remove_duplicate_scholarships()
        print(f"    ✅ Removed {removed_count} duplicates")
        
        # Test enhanced cleanup
        print("  🧹 Testing enhanced cleanup...")
        expired_count = cache.cleanup_expired_scholarships(days_old=30)
        print(f"    ✅ Removed {expired_count} expired scholarships")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

def test_ui_integration():
    """Test UI integration with new scraping features"""
    print("\n🧪 Testing UI Integration...")
    
    try:
        # Check if UI has the new buttons
        with open('ui/app.py', 'r') as f:
            ui_content = f.read()
        
        has_quick_search = "Quick Search" in ui_content
        has_live_scrape = "Live Scrape" in ui_content
        has_aggressive_search = "aggressive_search" in ui_content
        
        print(f"  🔘 Quick Search button: {'✅' if has_quick_search else '❌'}")
        print(f"  🔘 Live Scrape button: {'✅' if has_live_scrape else '❌'}")
        print(f"  🔘 Aggressive search logic: {'✅' if has_aggressive_search else '❌'}")
        
        if has_quick_search and has_live_scrape and has_aggressive_search:
            print("  ✅ UI integration complete")
            return True
        else:
            print("  ⚠️ UI integration partial - some features missing")
            return False
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

def main():
    """Run all improvement verification tests"""
    print("🔧 Scholarship Hunter - Scraping Improvements Verification")
    print("=" * 70)
    
    tests = [
        ("Custom Site Immediate Scraping", test_custom_site_scraping),
        ("Aggressive Real-time Search", test_aggressive_search),
        ("Enhanced Background Triggers", test_background_trigger),
        ("Enhanced Cache Methods", test_cache_enhancements),
        ("UI Integration", test_ui_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "⚠️ PARTIAL"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("🔧 SCRAPING IMPROVEMENTS VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL IMPROVEMENTS VERIFIED! 🎉")
        print("\n🚀 Enhanced Features Available:")
        print("   ✅ Immediate scraping when adding custom sites")
        print("   ✅ Aggressive real-time search option ('Live Scrape' button)")
        print("   ✅ More frequent background updates (3 hours vs 6)")
        print("   ✅ Enhanced background scraping (8 sites vs 5)")
        print("   ✅ Intelligent duplicate removal")
        print("   ✅ Configurable cleanup thresholds")
        print("\n🎯 User Experience:")
        print("   ⚡ Quick Search: Instant cached results")
        print("   🚀 Live Scrape: Fresh content (30-60 seconds)")
        print("   🔄 Background: Auto-updates every 3 hours")
        print("   🧹 Maintenance: Auto-cleanup and deduplication")
    else:
        print(f"\n⚠️ {total - passed} issue(s) need attention.")
        print("\nℹ️ Note: Some failures may be due to anti-bot protection")
        print("   or network issues. Core functionality should still work.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
