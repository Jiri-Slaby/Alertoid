# Add references to discord.py and requests
import discord
from discord.ext import commands
import requests
import datetime
import asyncio
import json


intents = discord.Intents.all() # This will enable the default intents
intents.members = True # This will enable the members intent

# Create a bot instance with a command prefix
bot = commands.Bot(command_prefix="!", intents=intents)
previous_alert_data = None
current_alert_data = None


# Define a command to get the alert data from the planetside 2 api
async def alert():
    # Send a GET request to the api endpoint
    global previous_alert_data
    global current_alert_data
    response = requests.get("https://api.ps2alerts.com/instances/active")

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON data into a dictionary
        data = response.json()
        # Initialize a variable to store the alert data

        # Loop over the data
        for item in data:
            # Check if the item has world 10
            current_alert_data = None;
            if str(item["world"]) == "10":  # Use str() to convert to string
                # Store the item in the alert_data variable
                current_alert_data = item
                # Break out of the loop
                break

        # Create a dictionary to map the values to the continent names
        print(current_alert_data)

        # Check if the alert_data is not None
        if current_alert_data is not None and current_alert_data["zone"] != previous_alert_data:
            continent_names = {2: "Indar", 4: "Hossin", 6: "Amerish", 8: "Esamir", 344: "Oshur"}

            # Get the value of the censusMetagameEventType key from the current_alert_data variable
            event_type = current_alert_data["zone"]

            # Get the continent name from the dictionary using the value as a key
            continent_name = continent_names[event_type]
            # Get the value of the timeStarted key from the alert_data variable
            time_started = current_alert_data["timeStarted"]

            # Convert the string to a datetime object using UTC format
            time_started = datetime.datetime.strptime(time_started, "%Y-%m-%dT%H:%M:%S.%fZ")
            # Create a time interval of 3 hours
            three_hours = datetime.timedelta(hours=2)
            alert_time = datetime.timedelta(hours=1, minutes=30)

            # Add 3 hours to the datetime object
            time_started_plus_three = time_started + three_hours
            alert_end_time = time_started_plus_three + alert_time
            time_started_plus_three = time_started_plus_three.strftime("%H:%M:%S %d-%m-%Y")
            alert_end_time = alert_end_time.strftime("%H:%M:%S %d-%m-%Y")

            channel = bot.get_channel(1137502072086999181)
            role_id = 1139520199217905766
            # get the role object from the role id
            role = discord.utils.get(channel.guild.roles, id=role_id)

            message = f"{role.mention}There is an alert on {continent_name}!\n" \
                      f"Start time: {time_started_plus_three}\n" \
                      f"End time: {alert_end_time}\n"

            # Get the channel object with the id 1137502072086999181 using bot.get_channel()
            previous_alert_data = current_alert_data["zone"]
            print(previous_alert_data)
            # Send the message to that channel using channel.send()
            await channel.send(message)

        if current_alert_data is None and previous_alert_data is not None:
            # Send a message that there is no alert on miller server

            # Get the channel object with the id 1137502072086999181 using bot.get_channel()
            channel = bot.get_channel(1137502072086999181)

            # Send the message to that channel using channel.send()
            await channel.send("___________________________The alert has ended___________________________")
            previous_alert_data = None
@bot.command()
async def map(ctx):
    base_url = "https://census.daybreakgames.com/s:alertoid/get/ps2:v2/map/"

    # Define the zone names
    zone_names = {2: "Indar", 4: "Hossin", 6: "Amerish", 8: "Esamir", 344: "Oshur"}

    # Define the faction names
    faction_names = {0: "NS", 1: "VS", 2: "NC", 3: "TR"}

    # Define the world id
    world_id = 10

    # Define the zone ids
    zone_ids = [2, 4, 6, 8, 344]
    # Loop through the zone ids
    for zone_id in zone_ids:
        # Construct the full url with query parameters
        full_url = base_url + "?world_id=" + str(world_id) + "&zone_ids=" + str(zone_id)
        # Make a GET request and get the response as JSON
        response = requests.get(full_url).json()
        # Get the map data from the response
        map_data = response["map_list"][0]["Regions"]["Row"]
        # Initialize a set to store the faction ids
        faction_ids = set()
        # Loop through the map data
        for row in map_data:
            # Get the faction id from the row
            faction_id = row["RowData"]["FactionId"]
            # Add the faction id to the set if it is not 0 (neutral)
            if faction_id != "0":
                faction_ids.add(faction_id)

        zone_id = zone_names[(zone_id)]
        # Check if the set has only one element
        if len(faction_ids) == 1:

            # Print that the continent is locked by that faction
            faction_name = (faction_ids.pop())
            faction_name = faction_names[int(faction_name)]

            print(zone_id + " is LOCKED by: " + str(faction_name))
            channel = bot.get_channel(1137502072086999181)
            # Send the message to that channel using channel.send()
            await channel.send(zone_id + " is LOCKED by: " + str(faction_name))
        else:
            # Print that the continent is not locked
            print(str(zone_id) + " is OPEN")
            await channel.send(str(zone_id) + " is OPEN")

async def loop_alert():
    while True:
        await alert() # Call the alert function with ctx as an argument
        await asyncio.sleep(120) # Wait for 60 seconds before repeating

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!") # Print a message to indicate that the bot is ready
    await loop_alert() # Call the loop_alert function with None as an argument

# Run the bot with your bot token updated token MTEzNzQ3OTA3MDg4ODc3MTYyNQ.GGMnum._kMg7JLlHL0q2V0_dUq7XGCT34JYBqdB8xl6GI
bot.run("MTEzNzQ3OTA3MDg4ODc3MTYyNQ.GGMnum._kMg7JLlHL0q2V0_dUq7XGCT34JYBqdB8xl6GI")
