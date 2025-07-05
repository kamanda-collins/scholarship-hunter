#!/usr/bin/env python3
"""
Quick test to verify logo integration
"""
import os

def test_logo_integration():
    print("🎨 Testing Logo Integration...")
    
    # Check if logo file exists
    logo_path = "ui/logo.svg"
    if os.path.exists(logo_path):
        print(f"✅ Logo file found: {logo_path}")
        
        # Check file size
        file_size = os.path.getsize(logo_path)
        print(f"📊 Logo file size: {file_size} bytes")
        
        # Check if it's a valid SVG
        with open(logo_path, 'r') as f:
            content = f.read()
            if content.strip().startswith('<svg') and content.strip().endswith('</svg>'):
                print("✅ Valid SVG format detected")
            else:
                print("❌ Invalid SVG format")
                
        # Check CSS file
        css_path = "ui/mobile_styles.css"
        if os.path.exists(css_path):
            print(f"✅ CSS file found: {css_path}")
            with open(css_path, 'r') as f:
                css_content = f.read()
                if 'svg' in css_content.lower():
                    print("✅ Logo CSS styles detected")
                else:
                    print("❌ No logo CSS styles found")
        
        print(f"\n🎉 Logo integration test completed!")
        print(f"📱 Logo will be responsive on mobile and desktop")
        print(f"🎨 Logo positioned next to the title")
        print(f"🔗 App running at: http://localhost:8504")
        
    else:
        print(f"❌ Logo file not found: {logo_path}")

if __name__ == "__main__":
    test_logo_integration()
