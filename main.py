import discord
from discord.ext import commands
from configparser import ConfigParser

# Wikipedia's API and WEB SCRAPING Libaries 
import wikipedia
import requests
from bs4 import BeautifulSoup
import country_converter as coco # Converts weather ISO2 codes in country name.
cc = coco.CountryConverter()
import datetime
from datetime import date 
today = date.today() # Gets the current date


client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("Wikipedia"))
    print("Bot Ready!")

@client.command()
async def ping (ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms.")

# Weather API
config_file = "config.ini"
config = ConfigParser()
config.read(config_file)
api_key = config["api_key"]["key"]

# Weather Command
@client.command()
async def weather(ctx, *, city):
    result = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}")
    if result:
        json = result.json()
        city = json["name"]
        country = json["sys"]["country"]
        standard_country = coco.convert(names=country, to='name_short')
        temp_kelvin = json["main"]["temp"]
        temp_celsius = int(temp_kelvin - 273.15)
        todays_date = today.strftime("%d-%m-%Y")
        weather = json["weather"][0]["description"]
        await ctx.send(f"City: {city}\nCountry: {country} ({standard_country})\nDate: {todays_date}\nTemperature: {str(temp_celsius)}°C\nWeather: {weather.title()}")
    else:
        await ctx.send("We couldn't verify which city you wanted. Please make sure you spelled it correctly and try again.")


# Wikipedia Command
@client.command()
async def wiki(ctx, *, wiki_page):
    new_wiki_page = wiki_page.replace(" ", "_")
    website = requests.get(f"https://en.wikipedia.org/wiki/{new_wiki_page}")
    soup = BeautifulSoup(website.content, features="html.parser")
    wiki_title = soup.find("h1", class_ = "firstHeading").text
    modified_wiki_title = wiki_title.replace(" ", "_")
    article = wikipedia.summary(f"{modified_wiki_title}", sentences = 3)
    await ctx.send(f"**{wiki_title}:** \n{article}\nLearn more at: https://en.wikipedia.org/wiki/{new_wiki_page}")
    print()

# ADD: Account for spaces in words, fix delay if possible. 
# Fix: Error where 
# ADD: Try and Except Feature https://wikipedia.readthedocs.io/en/latest/quickstart.html

@wiki.error
async def wiki_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Please add the wiki page you would like to search.** (Tip: If the page title has multiple words, put an underscore between them. Example: Northern_Ireland).")

    if isinstance(error, NameError):
        search_wiki = wikipedia.search(wiki_title, results=4)
        ctx.send(f"{wiki_title} may refer to: {search_wiki}. Please specify which one.")

# ADD: If name cannot be found then say that it cannot be found.


@client.command()
async def wikirandom(ctx):
    random_article = wikipedia.random(pages=1).replace(" ", "_")
    await ctx.send(f"**Random article:**\n{wikipedia.summary(random_article)}\n**Learn more at:** https://en.wikipedia.org/wiki/{random_article}")


# Bot Token
client.run("") # Enter your Discord Bot Token Here.
