import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot with prefix and intents
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot successfully connects to Discord."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Currently active in {len(bot.guilds)} servers.')

@bot.command(name='ping')
async def ping(ctx):
    """Simple command to check if the bot is responsive."""
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

@bot.command(name='hello')
async def hello(ctx):
    """Greets the user who triggered the command."""
    await ctx.send(f'Hello {ctx.author.name}! 👋')

@bot.command(name='info')
async def info(ctx):
    """Provides information about the server."""
    server = ctx.guild
    await ctx.send(f'''
Server Information:
```
Name: {server.name}
Member Count: {server.member_count}
Created On: {server.created_at.strftime("%B %d, %Y")}
Owner: {server.owner.name}
```''')

@bot.event
async def on_member_join(member):
    """Welcomes new members when they join the server."""
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f'Welcome {member.mention} to the server! 🎉')

@bot.event
async def on_command_error(ctx, error):
    """Error handling for bot commands."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

def main():
    """Main function to run the bot."""
    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No token found. Make sure to set DISCORD_TOKEN in your .env file.")
    
    # Run the bot
    bot.run(token)

if __name__ == "__main__":
    main()