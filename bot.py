#!/usr/bin/env python3
"""
⚡ Telegram Auto Reaction Bot v3.0
Advanced Auto-Reaction Engine
Author: AutoReact Pro
"""
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from telethon.tl.functions.messages import SendReactionRequest
import random
import json
import os
# ═══════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════
API_ID = int(os.getenv("API_ID", "YOUR_API_ID"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
REACTIONS = ["👍", "❤️", "🔥", "🎉", "😂", "🏆", "⚡", "🚀"]
DELAY_RANGE = (500, 2000)  # ms
MAX_RETRIES = 3
LOG_LEVEL = logging.INFO
# ═══════════════════════════════════════
# SETUP LOGGING
# ═══════════════════════════════════════
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=LOG_LEVEL,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
# ═══════════════════════════════════════
# BOT CLASS
# ═══════════════════════════════════════
class AutoReactionBot:
    def __init__(self):
        self.client = TelegramClient(
            'auto_react_session',
            API_ID,
            API_HASH
        )
        self.stats = {
            "total_reactions": 0,
            "active_chats": set(),
            "errors": 0,
            "start_time": None
        }
        self.config = self._load_config()
        
    def _load_config(self):
        """Load bot configuration from file"""
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {
            "enabled_chats": [],
            "reactions": REACTIONS,
            "mode": "random",
            "delay": DELAY_RANGE,
            "exclude_chats": [],
            "keywords": [],
            "schedule": "24/7"
        }
    
    def _save_config(self):
        """Save current configuration"""
        with open("config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
    
    async def start(self):
        """Initialize and start the bot"""
        import time
        self.stats["start_time"] = time.time()
        
        await self.client.start()
        logger.info("⚡ Auto Reaction Bot Started!")
        logger.info(f"📊 Mode: {self.config['mode']}")
        logger.info(f"🎯 Reactions: {self.config['reactions']}")
        
        # Register event handlers
        self.client.add_event_handler(
            self.on_new_message,
            events.NewMessage(chats=self.config.get("enabled_chats"))
        )
        
        self.client.add_event_handler(
            self.on_message_edit,
            events.MessageEdited()
        )
        
        logger.info("✅ All handlers registered. Listening...")
        await self.client.run_until_disconnected()
    
    async def on_new_message(self, event):
        """Handle new incoming messages"""
        try:
            chat_id = event.chat_id
            
            # Check exclusions
            if chat_id in self.config.get("exclude_chats", []):
                return
            
            # Keyword filter
            keywords = self.config.get("keywords", [])
            if keywords and event.text:
                if not any(kw.lower() in event.text.lower() for kw in keywords):
                    return
            
            # Select reaction based on mode
            reaction = self._select_reaction(event)
            
            # Apply delay
            delay = random.uniform(
                self.config["delay"][0] / 1000,
                self.config["delay"][1] / 1000
            )
            await asyncio.sleep(delay)
            
            # Send reaction with retry
            await self._send_reaction_with_retry(
                event.chat_id, event.id, reaction
            )
            
            # Update stats
            self.stats["total_reactions"] += 1
            self.stats["active_chats"].add(chat_id)
            
            logger.info(
                f"✅ Reacted {reaction} in chat {chat_id} "
                f"(Total: {self.stats['total_reactions']})"
            )
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ Error: {str(e)}")
    
    def _select_reaction(self, event) -> str:
        """Select reaction based on configured mode"""
        reactions = self.config["reactions"]
        mode = self.config["mode"]
        
        if mode == "random":
            return random.choice(reactions)
        elif mode == "sequential":
            idx = self.stats["total_reactions"] % len(reactions)
            return reactions[idx]
        elif mode == "smart":
            return self._smart_select(event, reactions)
        else:
            return random.choice(reactions)
    
    def _smart_select(self, event, reactions) -> str:
        """AI-based reaction selection"""
        text = (event.text or "").lower()
        
        # Sentiment-based selection
        positive_words = ["good", "great", "awesome", "love", "amazing"]
        funny_words = ["lol", "haha", "funny", "joke", "😂"]
        fire_words = ["fire", "hot", "lit", "wow", "incredible"]
        
        if any(w in text for w in funny_words):
            return "😂"
        elif any(w in text for w in fire_words):
            return "🔥"
        elif any(w in text for w in positive_words):
            return "❤️"
        else:
            return random.choice(reactions)
    
    async def _send_reaction_with_retry(
        self, chat_id, msg_id, reaction, retries=MAX_RETRIES
    ):
        """Send reaction with retry logic"""
        for attempt in range(retries):
            try:
                await self.client(
                    SendReactionRequest(
                        peer=chat_id,
                        msg_id=msg_id,
                        reaction=reaction,
                        big=False
                    )
                )
                return True
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise e
        return False
    
    async def on_message_edit(self, event):
        """Handle edited messages"""
        logger.info(f"📝 Message edited in {event.chat_id}")
# ═══════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════
if __name__ == "__main__":
    bot = AutoReactionBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.critical(f"💥 Fatal error: {e}")
🚀 Setup Instructions
