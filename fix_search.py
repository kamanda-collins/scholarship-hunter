#!/usr/bin/env python3
"""
Fix the search functionality in the UI to enable immediate scraping
"""

# Let's replace the problematic section of the UI app with clean code
search_section = '''
    if search_clicked:
        # Quick search using cache (existing functionality)
        with st.spinner("⚡ Searching scholarship database..."):
            st.info(f"🎯 Prioritizing {st.session_state.selected_country} + International opportunities")
            st.info("📚 Using intelligent caching for instant results")
            
            opportunities = scraper.search_by_goal(
                goal=st.session_state.user_goal,
                keywords=keywords_list,
                custom_sites=custom_urls,
                user_id=st.session_state.user_id,
                country=st.session_state.selected_country
            )
            st.session_state.scraped_data = opportunities
            
            if opportunities:
                st.success(f"🎉 Found {len(opportunities)} scholarships instantly from database!")
                if len(opportunities) >= 5:
                    st.info("🔄 Database is being updated in background with fresh scholarships")
            else:
                st.warning("⚠️ No scholarships found. Try 'Live Scrape' for fresh results.")
    
    elif aggressive_search:
        # Aggressive real-time scraping
        with st.spinner("🚀 Performing live scholarship scraping..."):
            st.warning("⏱️ This may take 30-60 seconds but will find the freshest scholarships")
            
            # First get cached results for immediate display
            cached_opportunities = scraper.search_by_goal(
                goal=st.session_state.user_goal,
                keywords=keywords_list,
                custom_sites=custom_urls,
                user_id=st.session_state.user_id,
                country=st.session_state.selected_country
            )
            
            # Then perform aggressive scraping
            fresh_opportunities = scraper.perform_aggressive_search(
                goal=st.session_state.user_goal,
                keywords=keywords_list,
                country=st.session_state.selected_country,
                max_sites=5
            )
            
            # Combine results (remove duplicates)
            all_opportunities = cached_opportunities + fresh_opportunities
            
            # Remove duplicates based on title similarity
            unique_opportunities = []
            seen_titles = set()
            for opp in all_opportunities:
                title_key = opp['title'].lower()[:50]  # First 50 chars for similarity check
                if title_key not in seen_titles:
                    unique_opportunities.append(opp)
                    seen_titles.add(title_key)
            
            st.session_state.scraped_data = unique_opportunities
            
            if unique_opportunities:
                cached_count = len(cached_opportunities)
                fresh_count = len(fresh_opportunities)
                st.success(f"🎉 Found {len(unique_opportunities)} total scholarships!")
                st.info(f"📚 {cached_count} from cache + 🆕 {fresh_count} fresh from web")
            else:
                st.error("❌ No scholarships found. Try different keywords or check custom sites.")
'''

print("Search section code prepared. Manual replacement needed due to encoding issues.")
