import discord
from discord import app_commands
from discord import SyncWebhook
from discord.ext import commands
from discord.ui import Modal, Select, View
import aiohttp
from data import *
import datetime
import json
import asyncio
import traceback

# for my dotenv file
#from decouple import config


intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!!", case_insensitive=True, intents=intents,
                   strip_after_prefix=True)

slash = bot.tree


class Body(Modal, title='Anonymous Message Editor'):
    content = discord.ui.TextInput(
        label="'Message'",
        style=discord.TextStyle.long,
        placeholder='The text that will become your anonymous message',
        required=True,
        max_length=4000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

    async def on_error(self, error: Exception, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong.\nError: {error}', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)


class Dropdown(Select):
    def __init__(self):

        with open("storage.json", "r") as f:
            data = json.load(f)

        options = [discord.SelectOption(label=k) for k in data["blocked_anon_numbers"]]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose the anon_id_number...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.val = True
        self.view.stop()


class DropdownView(View):
    def __init__(self):
        self.val = False
        super().__init__(timeout=60)

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())

    async def on_timeout(self):
        return


@bot.event
async def on_ready():
    print("Bot running with:")
    print("Username: ", bot.user.name)
    print("User ID: ", bot.user.id)
    await bot.change_presence(activity=discord.Game(name='Sharif sabha'))
    await slash.sync(guild=discord.Object(id=GUILD_ID))

intents = discord.Intents.all()
intents.reactions = True
bot = commands.Bot(command_prefix="!!", case_insensitive=True, intents=intents,
                   strip_after_prefix=True)
slash = bot.tree

@bot.event
async def on_member_join(member):
    welcome_message = f"{member.mention}<a:Heart:1118949630059757638>𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐒𝐇𝐀𝐑𝐈𝐅 𝐒𝐀𝐁𝐇𝐀<a:Heart:1118949630059757638> \n \n Get to Work <@&1109726651723567196>"
    channel= bot.get_channel(1104365327241973914)
    await channel.send(welcome_message)
    chan = bot.get_channel(1104365326768025771)
    embed=discord.Embed(title="<a:yellow_hearts:1118829376138641429> Welcome to Sharif Shabha's Discord" , description=f"<a:arrowright:1118946754683994232> Make sure to read <#1104365326768025774> to avoid getting punishment \n<a:arrowright:1118946754683994232> Assign yourself roles in <#1104365326768025775> \n<a:arrowright:1118946754683994232>Join to generate your VC <#1104733443734118491> \n<a:arrowright:1118946754683994232>Head trowards <#1104365327241973914> for texting and metting new friends \n <a:Green_Verification:1118954028961898546>Invite Link \nhttps://dsc.gg/sharif ") # F-Strings!
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1109072506129743892/1109078544665018459/SHARIF_8.gif") # Set the embed's thumbnail to the member's avatar image!
    embed.set_image(url="https://media.discordapp.net/attachments/1080892410835509268/1108855254243606598/standard.gif")
    await chan.send(f"A new member has joined our family {member.mention}\n",embed=embed)

starboard_channel_id = 1118994629052870786


starboard_messages = {}  # Dictionary to store starboard messages

@bot.event
async def on_reaction_add(reaction, member):
    schannel = bot.get_channel(starboard_channel_id)
    
    if (reaction.emoji == '⭐') and (reaction.count >= 1):
        message = reaction.message
        jump_url = message.jump_url

        if message.id not in starboard_messages:  # Check if the message has already been posted
            embed = discord.Embed(title="Sharif Sabha Starboard" , description= f'{message.content} \n[Click here to jump to message]({jump_url})')
            embed.set_author(name=message.author.name, icon_url=message.author.avatar)
            
            if len(message.attachments) > 0:
                embed.set_image(url=message.attachments[0].url)
            
            embed.set_footer(text=f" ⭐ {reaction.count} | # {message.channel.name}")
            embed.timestamp = datetime.datetime.utcnow()
            
            starboard_messages[message.id] = {
                'message': await schannel.send(embed=embed),
                'reaction': reaction,
            }
        else:
            starboard_entry = starboard_messages[message.id]
            starboard_entry['reaction'] = reaction
            await update_starboard_message(starboard_entry['message'], reaction.count)

async def update_starboard_message(message, count):
    embed = message.embeds[0]
    embed.set_footer(text=f" ⭐ {count} | # {message.channel.name}")
    await message.edit(embed=embed)

@slash.command(guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    content='The text of your anonymous message, leave blank for a paragraph editor',
)
async def confess(interaction, content: str = None):
    """Send an anonymous message to this channel"""
    # Remove the next two lines to let slash command be used in any channel
    #if not interaction.channel_id == CHANNEL_ID:
     #   return

    with open("storage.json", "r") as f:
        data = json.load(f)

    # Blocked Check
    if interaction.user.id in data["blocked"]:
        return await interaction.response.send_message("You have been blocked from confessing.", ephemeral=True)

    emb = discord.Embed(color=discord.Color.random(), title="Sharif Sabha")
    data["count"] += 1
    emb.set_footer(text=f"Conferssion no. #{data['count']}, If this confession is ToS-breaking or overtly hateful, you can report it ")
    emb.set_thumbnail(url="https://cdn.discordapp.com/icons/1104365324582793318/a_7457fcf4ca011dd5db45a0ebb069dcea.gif")

    with open("storage.json", "w") as f:
        json.dump(data, f, indent=4)

    option = False
        # Take long input
    modal = Body()
    await interaction.response.send_modal(modal)
    option = await modal.wait()
    if option:
        return
    content = str(modal.content)
    option = True

    if content:
        emb.description = f'"{content}"'

    if option:
        await interaction.followup.send("Done, your Confession has been submited.", ephemeral=True)
    else:
        await interaction.response.send_message("Done, your confession has been submited.", ephemeral=True)

    ch = interaction.guild.get_channel(1116399774204178542)
    await ch.send(embed=emb)

    #ch = interaction.guild.get_channel(channel_id)
    #username = interaction.user
    #await ch.send(f'Confession Log:\nUsername: {username}\n\n{str(emb)}')

    username = interaction.user
    description = emb.description
    confession_number = data["count"]

    confession_embed = discord.Embed(
    title="Confession Log",
    description=f"Confession Number: {confession_number}\nUsername: {username}\nDescription: {description}",
    color=discord.Color.random()
    )
    webhook = SyncWebhook.from_url('YOUR WEBHOOK URL')
    webhook.send(embed=confession_embed)

bot.run("BOT_TOKEN")  # Replace with your Discord bot token