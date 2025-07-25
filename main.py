"""
Hand Hockey Discord Bot - Main Entry Point
Loads all command modules and starts the bot
"""
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import logging
import os
import sys
from pathlib import Path
from config import Config

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("DISCORD_TOKEN is not set in the environment variables")
    raise ValueError("Discord token not found")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class HandHockeyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None,  # Help command is loaded as a cog
            application_id=Config.APPLICATION_ID
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler for the bot"""
        # Ignore CommandNotFound errors to reduce log spam
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Let other errors bubble up to be handled by cog error handlers
        # If no cog handles it, log the error
        logger.error(f"Unhandled command error: {error}", exc_info=True)

    async def setup_hook(self):
        # Initialize database
        try:
            from database import init_database
            await init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
        # Load all cogs from the cogs directory
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f"Loaded cog: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load cog {filename}: {e}")
        logger.info("All cogs loaded successfully")

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info('------')
        # Sync commands
        try:
            logger.info("Starting command sync...")
            if Config.GUILD_ID:
                # Sync to specific guild for faster development (instant)
                guild = discord.Object(id=Config.GUILD_ID)
                await self.tree.sync(guild=guild)
                logger.info(f"Command tree synced successfully to guild {Config.GUILD_ID}!")
            else:
                # Global sync (takes up to 1 hour)
                await self.tree.sync()
                logger.info("Command tree synced globally!")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

bot = HandHockeyBot()

async def main():
    async with bot:
        try:
            await bot.start(TOKEN)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
