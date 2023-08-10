# Add references to discord.py and requests
import discord
from discord.ext import commands
import requests
import datetime

intents = discord.Intents.all() # This will enable the default intents
intents.members = True # This will enable the members intent

# Create a bot instance with a command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Define a command to get the alert data from the planetside 2 api
@bot.command()
async def alert(ctx):
    # Send a GET request to the api endpoint
    response = requests.get("https://api.ps2alerts.com/instances/active")

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON data into a dictionary
        data = response.json()
        # Initialize a variable to store the alert data
        alert_data = None

        # Loop over the data
        for item in data:
            # Check if the item has world 10
            if str(item["world"]) == "10":  # Use str() to convert to string
                # Store the item in the alert_data variable
                alert_data = item
                # Break out of the loop
                break
        # Create a dictionary to map the values to the continent names
        print(alert_data)

        # Check if the alert_data is not None
        if alert_data is not None:
            continent_names = {2: "Indar", 4: "Hossin", 6: "Amerish", 8: "Esamir", 344: "Oshur"}

            # Get the value of the censusMetagameEventType key from the alert_data variable
            event_type = alert_data["zone"]

            # Get the continent name from the dictionary using the value as a key
            continent_name = continent_names[event_type]
            # Get the value of the timeStarted key from the alert_data variable
            time_started = alert_data["timeStarted"]

            # Convert the string to a datetime object using UTC format
            time_started = datetime.datetime.strptime(time_started, "%Y-%m-%dT%H:%M:%S.%fZ")
            # Create a time interval of 3 hours
            three_hours = datetime.timedelta(hours=2)

            # Add 3 hours to the datetime object
            time_started_plus_three = time_started + three_hours
            time_started_plus_three = time_started_plus_three.strftime("%H:%M:%S %d-%m-%Y")

            message = f"There is an alert on {continent_name}!\n" \
                      f"Event ID: {alert_data['zone']}\n" \
                      f"Event State: {alert_data['state']}\n" \
                      f"Timestamp: {time_started_plus_three}"

            await ctx.send(message)
        else:
            # Send a message that there is no alert on miller server
            await ctx.send("There is no alert on Miller server.")


# Run the bot with your bot token
bot.run("MTEzNzQ3OTA3MDg4ODc3MTYyNQ.Gx94YO.OA47KNWXVh25XI7_vX2peCK8HCyA1eACmG3ktA")
