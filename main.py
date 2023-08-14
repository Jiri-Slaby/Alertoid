import discord
from discord.ext import commands
import requests
import datetime
import asyncio
import os

intents = discord.Intents.all()  # This will enable the all intents
intents.members = True  # This will enable the members intent

# Create a bot instance with a command prefix
bot = commands.Bot(command_prefix="!", intents=intents)
# Global Variables
previous_alert_data = None
current_alert_data = None

# Access your service variables
bot_token = os.environ['Bot_token']
ps2_api_token = os.environ['PS2_API_token']
channel_id = None
server_id = None


async def alert():
    global previous_alert_data
    global current_alert_data
    # Send a GET request to the api endpoint
    response = requests.get("https://api.ps2alerts.com/instances/active")

    # Check the response
    if response.status_code == 200:
        # Parse the JSON
        data = response.json()

        for item in data:
            # Check if the item has world 10
            current_alert_data = None
            if str(item["world"]) == str(server_id):
                # Store the item in the alert_data
                current_alert_data = item
                break
        # print of the API return call
        print(current_alert_data)

        # Check if the alert_data is not None
        if current_alert_data is not None and current_alert_data["zone"] != previous_alert_data:
            # Dictionary of continents
            continent_names = {2: "Indar", 4: "Hossin", 6: "Amerish", 8: "Esamir", 344: "Oshur"}

            # Get the value of the zone
            event_type = current_alert_data["zone"]

            # Get the continent name from the dictionary
            continent_name = continent_names[event_type]
            # Get the value
            time_started = current_alert_data["timeStarted"]

            # Convert the string
            time_started = datetime.datetime.strptime(time_started, "%Y-%m-%dT%H:%M:%S.%fZ")

            # Create a time interval of 3 hours and how long is the alert running which is 1:30
            three_hours = datetime.timedelta(hours=2)
            alert_time = datetime.timedelta(hours=1, minutes=30)

            # Time managment
            time_started_plus_three = time_started + three_hours
            alert_end_time = time_started_plus_three + alert_time
            time_started_plus_three = time_started_plus_three.strftime("%H:%M:%S %d-%m-%Y")
            alert_end_time = alert_end_time.strftime("%H:%M:%S %d-%m-%Y")

            channel = bot.get_channel(channel_id)
            role_id = 1139520199217905766

            # get the role object from the role id
            role = discord.utils.get(channel.guild.roles, id=role_id)

            message = f"{role.mention}There is an alert on {continent_name}!\n" \
                      f"Start time: {time_started_plus_three}\n" \
                      f"End time: {alert_end_time}\n"

            previous_alert_data = current_alert_data["zone"]

            # Send the message
            await channel.send(message)

        if current_alert_data is None and previous_alert_data is not None:
            # Get the channel
            channel = bot.get_channel(channel_id)
            # Send the message
            await channel.send("___________________________The alert has ended___________________________")
            previous_alert_data = None
@bot.command()
async def commands(ctx):
    message =f"!setserver number - Sets the Planetside 2 server by number.\n"\
             f"!setchannel channelname - Sets the channel where the information about alerts will be send.\n" \
             f"!map - Chek which maps are locked and which arent.\n" \
             f"!credit - Link to BOT Github page.\n"
    await ctx.send(message)

@bot.command()
async def credit(ctx):
    channel = bot.get_channel(ctx.channel)
    await channel.send("https://github.com/Jiri-Slaby/Alertoid")
@bot.command()
async def setserver(ctx, world_id):
    global server_id
    server_id = world_id
    channel = bot.get_channel(ctx.channel.id)
    await channel.send("Server is set to " + str(server_id))
@bot.command()
async def setchannel(ctx, channel_name):
    global channel_id
    channel_id = discord.utils.get(ctx.guild.channels, name=channel_name)
    channel = bot.get_channel(ctx.channel.id)
    await channel.send("Channel is set to " + str(channel_name))

@bot.command()
async def map(ctx):

    # Define the zone names
    zone_names = {2: "Indar", 4: "Hossin", 6: "Amerish", 8: "Esamir", 344: "Oshur"}

    # Define the faction names
    faction_names = {0: "NS", 1: "VS", 2: "NC", 3: "TR"}

    # Define the zone ids
    zone_ids = [2, 4, 6, 8, 344]

    # Initialize a list to store locked zone information
    locked_zones_info = []

    # Loop through the zone ids
    for zone_id in zone_ids:
        # Construct the full url
        full_url = "https://census.daybreakgames.com/s:"+str(ps2_api_token)+"/get/ps2:v2/map/?world_id=" + str(server_id) + "&zone_ids=" + str(zone_id)
        # Make a GET request
        response = requests.get(full_url).json()
        # Get the map data from the response
        map_data = response["map_list"][0]["Regions"]["Row"]
        # Initialize a set to store the faction ids
        faction_ids = set()
        # Loop through the map data
        for row in map_data:
            # Get the faction id from the row
            faction_id = row["RowData"]["FactionId"]
            # Add the faction id to the set if it is not 0 which are NS, that cannot lock the continent.
            # API calls return that on Oshur NS are controlling the region even if the continent is locked
            if faction_id != "0":
                faction_ids.add(faction_id)

        zone_id = zone_names[zone_id]
        # Check if the set has only one element
        if len(faction_ids) == 1:
            # Continent is locked, get the faction name
            faction_name = faction_names[int(faction_ids.pop())]
            locked_zones_info.append(f"{zone_id} is LOCKED by: {faction_name}")
        else:
            # Continent is not locked
            locked_zones_info.append(f"{zone_id} is OPEN")

    # Join information into a single string
    locked_zones_summary = "\n".join(locked_zones_info)
    print(locked_zones_summary + "locked zone summary")

    # Get the channel and send message
    channel = bot.get_channel(ctx.channel.id)
    await channel.send(locked_zones_summary)


async def loop_alert():
    while True:
        await alert()  # Call the alert
        await asyncio.sleep(120)  # Wait for 120 seconds


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")  # Connect message
    await loop_alert()  # Call the loop_alert


# Discord bot token
bot.run(bot_token)
