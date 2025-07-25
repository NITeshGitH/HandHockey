"""
Utility functions and error handling for Hand Hockey Discord Bot
"""
import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import Config
import random
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hand_hockey_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BotError(Exception):
    """Base exception for bot errors"""
    pass

class MatchError(BotError):
    """Exception for match-related errors"""
    pass

class PlayerError(BotError):
    """Exception for player-related errors"""
    pass

class ValidationError(BotError):
    """Exception for validation errors"""
    pass

def create_error_embed(title: str, description: str) -> discord.Embed:
    """Create a standardized error embed"""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=Config.Colors.ERROR
    )
    return embed

def create_success_embed(title: str, description: str) -> discord.Embed:
    """Create a standardized success embed"""
    embed = discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=Config.Colors.SUCCESS
    )
    return embed

def create_warning_embed(title: str, description: str) -> discord.Embed:
    """Create a standardized warning embed"""
    embed = discord.Embed(
        title=f"⚠️ {title}",
        description=description,
        color=Config.Colors.WARNING
    )
    return embed

def create_info_embed(title: str, description: str) -> discord.Embed:
    """Create a standardized info embed"""
    embed = discord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=Config.Colors.INFO
    )
    return embed

def validate_team(team: str) -> str:
    """Validate and normalize team input"""
    team = team.upper().strip()
    if team not in Config.VALID_TEAMS:
        raise ValidationError(f"Team must be one of: {', '.join(Config.VALID_TEAMS)}")
    return team

def validate_role(role: str) -> str:
    """Validate and normalize role input"""
    role = role.upper().strip()
    if role not in Config.VALID_ROLES:
        raise ValidationError(f"Role must be one of: {', '.join(Config.VALID_ROLES)}")
    return role

def get_role_emoji(role: str) -> str:
    """Get emoji for a role"""
    role_emojis = {
        "ST": "⚽",  # Striker
        "MF": "🏃",  # Midfielder
        "DEF": "🛡️",  # Defender
        "GK": "🧤"   # Goalkeeper
    }
    return role_emojis.get(role.upper(), "❓")

def get_role_name(role: str) -> str:
    """Get full name for a role"""
    role_names = {
        "ST": "Striker",
        "MF": "Midfielder", 
        "DEF": "Defender",
        "GK": "Goalkeeper"
    }
    return role_names.get(role.upper(), "Unknown")

def generate_match_id(user_id: int = None) -> str:
    """Generate a short, user-friendly match ID"""
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"match_{code}"

def is_match_expired(created_at: datetime) -> bool:
    """Check if a match has expired"""
    expiry_time = created_at + timedelta(minutes=Config.MATCH_TIMEOUT_MINUTES)
    return datetime.now() > expiry_time

async def send_dm_safely(user: discord.User, embed: discord.Embed) -> bool:
    """Safely send a DM to a user with error handling"""
    try:
        await user.send(embed=embed)
        logger.info(f"DM sent successfully to {user.name}")
        return True
    except discord.Forbidden:
        logger.warning(f"Cannot send DM to {user.name} - DMs are disabled")
        return False
    except discord.HTTPException as e:
        logger.error(f"Failed to send DM to {user.name}: {e}")
        return False

async def timeout_handler(coro, timeout: int):
    """Handle coroutine with timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout} seconds")
        raise BotError(f"Operation timed out after {timeout} seconds")

def log_command_usage(ctx, command_name: str, additional_info: str = ""):
    """Log command usage for monitoring"""
    user_info = f"{ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})"
    guild_info = f"Guild: {ctx.guild.name} (ID: {ctx.guild.id})" if ctx.guild else "DM"
    
    log_message = f"Command '{command_name}' used by {user_info} in {guild_info}"
    if additional_info:
        log_message += f" - {additional_info}"
    
    logger.info(log_message)

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    async def handle_command_error(ctx, error):
        """Handle command errors"""
        if isinstance(error, ValidationError):
            embed = create_error_embed("Invalid Input", str(error))
            await ctx.send(embed=embed)
        
        elif isinstance(error, MatchError):
            embed = create_error_embed("Match Error", str(error))
            await ctx.send(embed=embed)
        
        elif isinstance(error, PlayerError):
            embed = create_error_embed("Player Error", str(error))
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = create_error_embed(
                "Missing Argument", 
                f"Missing required argument: {error.param.name}"
            )
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.BadArgument):
            embed = create_error_embed("Invalid Argument", str(error))
            await ctx.send(embed=embed)
        
        elif isinstance(error, commands.CommandNotFound):
            # Silently ignore CommandNotFound errors to reduce spam
            return
        
        elif isinstance(error, commands.CommandInvokeError):
            # Unwrap the original error and handle it recursively
            await ErrorHandler.handle_command_error(ctx, error.original)
            return
        
        else:
            embed = create_error_embed(
                "Unexpected Error", 
                "An unexpected error occurred. Please try again later."
            )
            await ctx.send(embed=embed)
            logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=True)
