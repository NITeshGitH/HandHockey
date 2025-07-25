"""
Configuration management for Hand Hockey Discord Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration settings"""
    
    # Discord Bot Settings
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    APPLICATION_ID = os.getenv('APPLICATION_ID')
    GUILD_ID = int(os.getenv('YOUR_GUILD_ID')) if os.getenv('YOUR_GUILD_ID') else None
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', 'H')
    
    # Database Settings (PostgreSQL - Neon.com)
    DATABASE_URL = os.getenv('DATABASE_URL')
    DB_POOL_MIN_SIZE = int(os.getenv('DB_POOL_MIN_SIZE', 1))
    DB_POOL_MAX_SIZE = int(os.getenv('DB_POOL_MAX_SIZE', 10))
    
    # Game Settings
    MAX_PLAYERS_PER_MATCH = int(os.getenv('MAX_PLAYERS_PER_MATCH', 10))
    MATCH_TIMEOUT_MINUTES = int(os.getenv('MATCH_TIMEOUT_MINUTES', 10))
    TURN_TIMEOUT_SECONDS = int(os.getenv('TURN_TIMEOUT_SECONDS', 45))
    
    # Bot Colors (for embeds)
    class Colors:
        SUCCESS = 0x00ff00
        ERROR = 0xff0000
        WARNING = 0xffaa00
        INFO = 0x0099ff
        GOLD = 0xffd700
        ORANGE = 0xff6600
    
    # Game Roles
    VALID_ROLES = ["ST", "MF", "DEF", "GK"]  # Striker, Midfielder, Defender, Goalkeeper
    VALID_TEAMS = ["A", "B"]
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required. Please set it in your .env file.")
        
        if not cls.APPLICATION_ID:
            raise ValueError("APPLICATION_ID is required. Please set it in your .env file.")
        
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is required. Please set it in your .env file for Neon.com PostgreSQL connection.")
        
        return True
