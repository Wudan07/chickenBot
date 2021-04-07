# bot.py
import os

import discord
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

playerStats = {}
dataRoot = os.getenv('DATA_PATH')
playerStatsYamlPath = '{0}/out/playerStats.yaml'.format(dataRoot)
playerStatsYamlFW = FileWerks(playerStatsYamlPath)
if playerStatsYamlFW.exists is True:
    playerStats = yamlRead(playerStatsYamlPath)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}'.format(self.user))

    async def on_message(self, message):
        takeAction = True
        isAdmin = False
        thisGuild = None
        thisDiscord = None
        messageOut = ''
        #print(type(message))
        #messageMembers = dir(message)
        #for member in messageMembers:
        #    print(member)
        # don't respond to ourselves
        if message.author == self.user:
            takeAction = False
        else:
            print(message.author)
            #print(type(message.author))
            print(dir(message.author))
            print(message.author.name)
            print(message.author.guild)
            print(message.author.id)
            if thisGuild is None:
                thisGuild = message.author.guild.name
                print(type(message.author.guild))
            if stringMatch(message.author.name, AUTHORADMIN):
                isAdmin = True
            else:
                print('not match {0}'.format(AUTHORADMIN))
        
        if thisGuild is not None:
            if stringMatch(thisGuild, 'TheTechTemplar'):
                thisDiscord = 'Chicken Dinner'
            elif stringMatch(thisGuild, 'Chicken Dinner'):
                thisDiscord = 'Chicken Dinner'
            else:
                thisDiscord = thisGuild
        
        if takeAction is True:
            msgContent = message.content
            if stringMatchStart(msgContent, '#'):
                msgContent = stringStripStart(msgContent, '#')
                if msgContent == 'ping':
                    await message.channel.send('pong')
                if stringMatchStart(msgContent.lower(), 'playerstats'):
                    msgVals = stringSplitNoEmpty(msgContent, ' ')
                    if len(msgVals) == 1:
                        print('looking for playerstats')
                        if isAdmin is True:
                            if isinstance(playerStats, dict):
                                guildPlayers = []
                                for playerName in playerStats:
                                    goodPlayer = False
                                    playerInfoPath = '{0}/players/{1}/info.yaml'.format(dataRoot, playerName)
                                    print(playerInfoPath)
                                    playerInfoFW = FileWerks(playerInfoPath)
                                    if playerInfoFW.exists is True:
                                        print('have info on {0}'.format(playerName))
                                        thisPlayerInfo = yamlRead(playerInfoPath)
                                        if isinstance(thisPlayerInfo, dict):
                                            playerGuild = dictGetValue(thisPlayerInfo, 'discord')
                                            print('playerGuild {0} versus thisDiscord {1}'.format(playerGuild, thisDiscord))
                                            if stringMatch(playerGuild, thisDiscord):
                                                goodPlayer = True
                                    if goodPlayer is True:
                                        #messageOut += '{0}\n'.format(playerName)
                                        listAdd(guildPlayers, playerName)
                                for playerName in sorted(guildPlayers):
                                    playerMessage = ''
                                    thisPlayerStats = playerStats[playerName]
                                    survivedTime = dictGetValue(thisPlayerStats, 'totalSurvived')
                                    print(type(survivedTime))
                                    if isinstance(survivedTime, float):
                                        if survivedTime > 0.0:
                                            playerMessage += '{0}\n'.format(playerName)
                                            #for statKey in thisPlayerStats:
                                                #playerMessage += '  {0}\n'.format(statKey)
                                            playerMessage += '    Damage Dealt: {0:0.1f}\n'.format(dictGetValue(thisPlayerStats, 'totalDamage'))
                                            playerMessage += '    Kill Count: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalKills'))
                                            playerMessage += '    Headshot Kills: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalHeadshotKills'))
                                            playerMessage += '    Time Survived (minutes): {0:0.1f}\n'.format(survivedTime / 60.0)
                                            playerMessage += '    Chicken Dinners: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalChickenDinners'))
                                            playerMessage += '    Revive Count: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalRevives'))
                                        #print(' Wrecking Ball: {0} with {1:0.1f} damage'.format(wreckingBall, wreckingBallValue))
                                        #print('     Deadliest: {0} with {1} kills'.format(mostKills, mostKillsValue))
                                        #print('Migraine Maker: {0} with {1} headshot kills'.format(mostHeadshotKills, mostHeadshotKillsValue))
                                        #print('   Survivalist: {0} with {1:0.1f} seconds survived'.format(mostSurvived, mostSurvivedValue))
                                        #print(' Chicken Eater: {0} with {1} chicken dinners'.format(wellFed, wellFedValue))
                                        #print(' Friend Indeed: {0} with {1} revives'.format(friendIndeed, friendIndeedValue))
                                    if len(playerMessage) > 0:
                                        await message.channel.send(playerMessage)
                        else:
                            #messageOut += 'not pog champ'
                            pass
                    elif len(msgVals) == 2:
                        print('looking for playerstats')
                        if isinstance(playerStats, dict):
                            guildPlayers = []
                            playerName = msgVals[1]
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
                                        #playerGuild = dictGetValue(thisPlayerInfo, 'discord')
                                        #if stringMatch(playerGuild, thisDiscord):
                                        goodPlayer = True
                                if goodPlayer is True:
                                    #messageOut += '{0}\n'.format(playerName)
                                    listAdd(guildPlayers, playerName)
                            else:
                                messageOut += 'I do not have stats for {0}, tell {1} you want stats, damnit!'.format(playerName, AUTHORADMIN)
                            for playerName in sorted(guildPlayers):
                                playerMessage = ''
                                playerMessage += '{0}\n'.format(playerName)
                                thisPlayerStats = playerStats[playerName]
                                survivedTime = dictGetValue(thisPlayerStats, 'totalSurvived')
                                hasStats = False
                                if survivedTime is not None:
                                    if survivedTime > 0.0:
                                        playerMessage += '    Damage Dealt: {0:0.1f}\n'.format(dictGetValue(thisPlayerStats, 'totalDamage'))
                                        playerMessage += '    Kill Count: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalKills'))
                                        playerMessage += '    Headshot Kills: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalHeadshotKills'))
                                        playerMessage += '    Time Survived (minutes): {0:0.1f}\n'.format(survivedTime / 60.0)
                                        playerMessage += '    Chicken Dinners: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalChickenDinners'))
                                        playerMessage += '    Revive Count: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalRevives'))
                                        hasStats = True
                                if hasStats is False:
                                    playerMessage += '    Has not played any games in Season 11 (started on 3/31/2021.)'

                                    #print(' Wrecking Ball: {0} with {1:0.1f} damage'.format(wreckingBall, wreckingBallValue))
                                    #print('     Deadliest: {0} with {1} kills'.format(mostKills, mostKillsValue))
                                    #print('Migraine Maker: {0} with {1} headshot kills'.format(mostHeadshotKills, mostHeadshotKillsValue))
                                    #print('   Survivalist: {0} with {1:0.1f} seconds survived'.format(mostSurvived, mostSurvivedValue))
                                    #print(' Chicken Eater: {0} with {1} chicken dinners'.format(wellFed, wellFedValue))
                                    #print(' Friend Indeed: {0} with {1} revives'.format(friendIndeed, friendIndeedValue))
                                await message.channel.send(playerMessage)
                elif stringMatchStart(msgContent.lower(), 'mystats'):
                    print('looking for playerstats')
                    if isinstance(playerStats, dict):
                        guildPlayers = []
                        playerName = message.author.name
                        ## here is where you'd try to map a Discord name to a PUBG name
                        #if stringMatch(playerName, 'Cheech'):
                        #    playerName = 'Chong'
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
                                    #playerGuild = dictGetValue(thisPlayerInfo, 'discord')
                                    #if stringMatch(playerGuild, thisDiscord):
                                    goodPlayer = True
                            if goodPlayer is True:
                                listAdd(guildPlayers, playerName)
                        else:
                            messageOut += 'I do not have stats for {0}, tell {1} you want stats, damnit!'.format(playerName, AUTHORADMIN)
                        for playerName in sorted(guildPlayers):
                            playerMessage = ''
                            playerMessage += '{0}\n'.format(playerName)
                            thisPlayerStats = playerStats[playerName]
                            survivedTime = dictGetValue(thisPlayerStats, 'totalSurvived')
                            hasStats = False
                            if survivedTime is not None:
                                if survivedTime > 0.0:
                                    playerMessage += '    Damage Dealt: {0:0.1f}\n'.format(dictGetValue(thisPlayerStats, 'totalDamage'))
                                    playerMessage += '    Kill Count: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalKills'))
                                    playerMessage += '    Headshot Kills: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalHeadshotKills'))
                                    playerMessage += '    Time Survived (minutes): {0:0.1f}\n'.format(survivedTime / 60.0)
                                    playerMessage += '    Chicken Dinners: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalChickenDinners'))
                                    playerMessage += '    Revive Count: {0}\n'.format(dictGetValue(thisPlayerStats, 'totalRevives'))
                                    hasStats = True
                            if hasStats is False:
                                playerMessage += '    Has not played any games in Season 11 (started on 3/31/2021.)'
                            await message.channel.send(playerMessage)
        if len(messageOut) > 0:
            await message.channel.send(messageOut)

client = MyClient()
client.run(TOKEN)
