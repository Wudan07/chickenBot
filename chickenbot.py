# bot.py
import os
import random
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv

from plebwerks import FileWerks, stringStripStart, stringStripEnd, stringMatch, stringMatchStart, \
    stringMatchEnd, stringClean, listAdd, listContains, yamlRead, yamlWrite, timeNow, \
    openTextFileWrite, dictGetKeys, dictGetValue, openBinaryFileWrite, stringToFile, stringSplitNoEmpty

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')
AUTHORADMIN = os.getenv('BOT_AUTHOR')

# set up before client
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

playerStats = None
playerStatsYamlHash = None
playerStatsLastTS = None
dataRoot = os.getenv('DATA_PATH')
discordToPUBGLUT = {}
discordToPUBGLUT = yamlRead('discordToPubgLUT.yaml')


def lookupPubgUser(discordName):
    global discordToPUBGLUT
    if discordName in discordToPUBGLUT:
        return discordToPUBGLUT[discordName]
    return discordName


def addPubgUserLookup(discordName, playerName):
    global discordToPUBGLUT
    changed = False
    if discordName in discordToPUBGLUT:
        discordToPUBGLUT[discordName] = playerName
        changed = True
    else:
        discordToPUBGLUT[discordName] = playerName
        changed = True
    if changed is True:
        yamlWrite('discordToPubgLUT.yaml', discordToPUBGLUT)


def loadPlayerStats():
    global dataRoot
    global playerStats
    global playerStatsYamlHash
    global playerStatsLastTS
    parsePlayerStats = False
    rightNow = timeNow(True)
    if playerStatsLastTS is None:
        parsePlayerStats = True
    else:
        if (rightNow - playerStatsLastTS) > 60:
            parsePlayerStats = True
    if parsePlayerStats is True:
        playerStatsYamlPath = '{0}/out/playerStats.yaml'.format(dataRoot)
        playerStatsYamlFW = FileWerks(playerStatsYamlPath)
        if playerStatsYamlFW.exists is True:
            playerStats = yamlRead(playerStatsYamlPath)
            print('loaded player stats')
            playerStatsLastTS = rightNow


def playerFetchStatBlock(playerName):
    global dataRoot
    global playerStats
    guildPlayers = []
    playerMessage = ''
    playerName = lookupPubgUser(playerName)
    for plName in playerStats:
        if stringMatch(playerName.lower(), plName.lower()):
            playerName = plName
    if playerName in playerStats:
        goodPlayer = False
        playerInfoPath = '{0}/players/{1}/info.yaml'.format(dataRoot, playerName)
        playerInfoFW = FileWerks(playerInfoPath)
        if playerInfoFW.exists is True:
            thisPlayerInfo = yamlRead(playerInfoPath)
            if isinstance(thisPlayerInfo, dict):
                goodPlayer = True
        if goodPlayer is True:
            listAdd(guildPlayers, playerName)
    else:
        playerMessage += 'I do not have stats for {0}, tell {1} you want stats, damnit!'.format(playerName, AUTHORADMIN)
    for playerName in sorted(guildPlayers):
        thisPlayerStats = playerStats[playerName]
        survivedTime = dictGetValue(thisPlayerStats, 'totalSurvived')
        print(type(survivedTime))
        if isinstance(survivedTime, float):
            if survivedTime > 0.0:
                playerMessage += '{0}\n'.format(playerName)
                playerMessage += '    Damage Dealt: {0:0.1f}\n'.format(dictGetValue(thisPlayerStats, 'totalDamage'))
                playerMessage += '    Kill Count: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalKills'))
                playerMessage += '    Headshot Kills: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalHeadshotKills'))
                playerMessage += '    Time Survived (minutes): {0:0.1f}\n'.format(survivedTime / 60.0)
                playerMessage += '    Chicken Dinners: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalChickenDinners'))
                playerMessage += '    Revive Count: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalRevives'))
    return playerMessage


class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=commands.Context):
        return await super().get_context(message, cls=cls)

bot = MyBot(command_prefix='#')

@bot.command()
async def mystats(ctx):
    global playerStats
    playerName = ctx.author.name
    guildCalled = ctx.guild
    print('COM[mystats]: looking for mystats for {0}@{1}'.format(playerName, guildCalled))
    if isinstance(playerStats, dict):
        pass
    else:
        loadPlayerStats()
    if isinstance(playerStats, dict):
        messageOut = playerFetchStatBlock(playerName)
        if len(messageOut) > 0:
            await ctx.send(messageOut)

@bot.command()
async def playerstats(ctx, *args):
    global playerStats
    playerName = ctx.author.name
    if len(args) >= 1:
        playerName = args[0]
    playerCalled = ctx.author.name
    guildCalled = ctx.guild
    print('COM[playerstats]: looking for playerstats[{2}], asked by {0}@{1}'.format(playerCalled, guildCalled, playerName))
    if isinstance(playerStats, dict):
        pass
    else:
        loadPlayerStats()
    if isinstance(playerStats, dict):
        messageOut = playerFetchStatBlock(playerName)
        if len(messageOut) > 0:
            await ctx.send(messageOut)

@bot.command()
async def reloadstats(ctx):
    global playerStats
    playerCalled = ctx.author.name
    guildCalled = ctx.guild
    print('COM[reloadstats]: please reload playerstats, asked by {0}@{1}'.format(playerCalled, guildCalled))
    loadPlayerStats()
    await ctx.send('Parsed playerStats.')

@bot.command()
async def playermap(ctx, *args):
    global playerStats
    newMapping = False
    discordName = ctx.author.name
    playerName = discordName
    if len(args) == 1:
        playerName = args[0]
    elif len(args) == 2:
        discordName = args[0]
        playerName = args[1]
    if stringMatch(discordName, playerName):
        pass
    else:
        if stringMatch(lookupPubgUser(discordName), playerName):
            pass
        else:
            addPubgUserLookup(discordName, playerName)
            newMapping = True
    playerCalled = ctx.author.name
    guildCalled = ctx.guild
    print('COM[playermap]: creating mapping for [{2} = {3}], asked by {0}@{1}'.format(playerCalled, guildCalled, discordName, playerName))
    messageOut = ''
    if newMapping is True:
        messageOut += 'mapped {0} to {1}'.format(discordName, playerName)
    if len(messageOut) > 0:
        await ctx.send(messageOut)

loadPlayerStats()
bot.run(TOKEN)
