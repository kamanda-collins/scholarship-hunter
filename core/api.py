import os
import json
import hashlib
from datetime import datetime
import streamlit as st
from .config import USAGE_FILE, MAX_FREE_USERS


class APIManager:
    """Manages API key usage and limits with secure user key storage"""
    def __init__(self, server_api_key=None):
        import streamlit as st
        # Prefer Streamlit secrets, fallback to env var, handle missing secrets gracefully
        try:
            # Check if we're in Streamlit context and secrets exist
            if hasattr(st, 'secrets') and 'gemini' in st.secrets:
                self.server_api_key = server_api_key or st.secrets["gemini"]["api_key"] or os.getenv("GEMINI_API_KEY")
            else:
                self.server_api_key = server_api_key or os.getenv("GEMINI_API_KEY")
        except Exception:
            # Silently handle case where secrets don't exist or are inaccessible
            self.server_api_key = server_api_key or os.getenv("GEMINI_API_KEY")
        self.usage_file = USAGE_FILE
        self.user_keys_file = "cache/user_api_keys.json"

    def load_usage_data(self):
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {"users": [], "count": 0, "created_at": datetime.now().isoformat()}
        return {"users": [], "count": 0, "created_at": datetime.now().isoformat()}

    def save_usage_data(self, data):
        with open(self.usage_file, 'w') as f:
            json.dump(data, f, indent=2)

    def can_use_server_api(self, user_id):
        data = self.load_usage_data()
        if user_id in data["users"]:
            return True
        if data["count"] >= MAX_FREE_USERS:
            return False
        data["users"].append(user_id)
        data["count"] += 1
        data["updated_at"] = datetime.now().isoformat()
        self.save_usage_data(data)
        return True

    def get_api_key(self, user_id, user_api_key=None):
        if user_api_key:
            # Save the user's API key securely for future use
            self.save_user_api_key(user_id, user_api_key)
            return user_api_key, 'user'
        if self.can_use_server_api(user_id):
            return self.server_api_key, 'server'
        return None, 'basic'

    def get_usage_stats(self):
        data = self.load_usage_data()
        return {
            "total_users": data["count"],
            "remaining_slots": max(0, MAX_FREE_USERS - data["count"]),
            "created_at": data.get("created_at", "Unknown")
        }

    def _hash_key(self, api_key):
        """Create a secure hash of the API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def save_user_api_key(self, user_id, api_key):
        """Securely save user's API key"""
        if not api_key:
            return
        
        # Load existing data
        user_keys = {}
        if os.path.exists(self.user_keys_file):
            try:
                with open(self.user_keys_file, 'r') as f:
                    user_keys = json.load(f)
            except Exception:
                user_keys = {}
        
        # Store hashed key with user ID
        user_keys[user_id] = {
            "key_hash": self._hash_key(api_key),
            "saved_at": datetime.now().isoformat()
        }
        
        # Save to file
        os.makedirs(os.path.dirname(self.user_keys_file), exist_ok=True)
        with open(self.user_keys_file, 'w') as f:
            json.dump(user_keys, f, indent=2)

    def verify_user_api_key(self, user_id, api_key):
        """Verify if the provided API key matches the stored one"""
        if not api_key or not os.path.exists(self.user_keys_file):
            return False
        
        try:
            with open(self.user_keys_file, 'r') as f:
                user_keys = json.load(f)
            
            if user_id in user_keys:
                return user_keys[user_id]["key_hash"] == self._hash_key(api_key)
        except Exception:
            pass
        
        return False
