import discord

gameboi = discord.Client()


#############################################################################
############################################################################# CLIENT
#############################################################################

class GameboiException(Exception):
    pass

class Lobby:
    idsInLobby = {}
    def __init__(self, people):
        self.people = people
        self.initMessage = []
    def close(self):
        for person in self.people:
            Lobby.idsInLobby.pop(person.id)

class WaitingLobby(Lobby):
    def __init__(self, game, people):
        super().__init__(people)
        for person in people:
            Lobby.idsInLobby[person.id] = self
        self.game = game
        self.checklist = set(people[1:])
        peoplestr = ""
        for person in people[1:]:
            peoplestr += person.mention + " "
        self.initMessage.append("" + people[0].mention + " has challenged " + peoplestr + "to a game of " + game.name + "!\n You must all type 'yes' to begin the game. Anyone may type 'no' to decline or cancel.")
    def eval(self, message):
        content = message.content.lower()
        if content == 'no':
            self.close()
            return ["Someone has declined the challenge. Cancelling game."]
        elif content == 'yes' and message.author in self.checklist:
            self.checklist.remove(message.author)
            if len(self.checklist) == 0:
                newGame = self.game(self.people)
                return [self.game.name + " started."] + newGame.initMessage
            else:
                return [message.author.name + " has confirmed. " + str(len(self.checklist)) + " more people needed to confirm."]

class GameLobby(Lobby):
    gamesList = {}
    name = ""
    numPlayers = 0

@gameboi.event
async def on_ready():
    print('Gameboi successfully booted!')
    print('Account: "'+gameboi.user.name+'", ID: '+gameboi.user.id)

@gameboi.event
async def on_message(message):
    if message.author.id in Lobby.idsInLobby:
        await sendOutputs(message.channel, Lobby.idsInLobby[message.author.id].eval(message))
    elif message.content.startswith(gameboi.user.mention):
        msgIter = iter(message.content.split())
        next(msgIter)
        try:
            command = next(msgIter).lower()
            if command == 'help':
                await gameboi.send_message(message.channel, "Mention me with these commands: \n"
                                                            "- '"+gameboi.user.mention+" help' : see commands \n"
                                                            "- '"+gameboi.user.mention+" games' : see list of game names \n"
                                                            "- '"+gameboi.user.mention+" play <game name> with <username or mention> <username or mention> ...' : invite people to play a game\n")
            elif command == 'games':
                gamesstr = "Games you can play: "
                for game in GameLobby.gamesList:
                    gamesstr = gamesstr + "\n-" + game + ". "
                    maxPlayers = GameLobby.gamesList[game].numPlayers[1]
                    minPlayers = GameLobby.gamesList[game].numPlayers[0]
                    if maxPlayers-minPlayers > 1:
                        gamesstr += str(minPlayers) + " to " + str(maxPlayers-1) + " players."
                    else:
                        gamesstr += str(minPlayers) + " players"
                await gameboi.send_message(message.channel, gamesstr)
            elif command == 'play':
                gameAndPeople = list(msgIter)
                wIndex = gameAndPeople.index('with')
                gameName = " ".join(gameAndPeople[:wIndex])
                inviteList = gameAndPeople[wIndex+1:]
                if not (gameName in GameLobby.gamesList):
                    raise GameboiException("Game name not found. Type '" + gameboi.user.mention + " games' : see list of game names.")
                game = GameLobby.gamesList[gameName]
                if not (game.numPlayers[0] <= (len(inviteList)+1) < game.numPlayers[1]):
                    if game.numPlayers[1]-game.numPlayers[0] > 1:
                        raise GameboiException("Wrong number of players for " + gameName + ". Need between " + str(game.numPlayers[0]) + " to " + str(game.numPlayers[1]-1) + " players.")
                    else:
                        raise GameboiException("Wrong number of players for " + gameName + ". Need " + str(game.numPlayers[0]) + " players.")
                players = [message.author]
                for name in inviteList:
                    person = findUser(name, message.channel)
                    if person in players:
                        raise GameboiException("Duplicate players found.")
                    if person.id in Lobby.idsInLobby:
                        raise GameboiException(person.name + " is already in a game.")
                    players.append(person)
                newLobby = WaitingLobby(game, players)
                await sendOutputs(message.channel, newLobby.initMessage)
            else:
                raise GameboiException("Command not found. \nType '"+gameboi.user.mention+" help' to see usage of commands.")
        except GameboiException as ge:
            await gameboi.send_message(message.channel, "Error: " + str(ge))
        except (StopIteration, ValueError):
            await gameboi.send_message(message.channel, "Type '"+gameboi.user.mention+" help' to see usage of commands.")

def findUser(theName, theChannel):
    for theUser in theChannel.server.members:
        if theUser.nick==theName or theUser.name==theName or theUser.mention==theName:
            if theUser.status != discord.Status.online:
                raise GameboiException("User not online or active: " + theName)
            else:
                return theUser
            break
    else:
        raise GameboiException("User not found: " + theName)

async def sendOutputs(thechannel, thelist):
    # A way to send the list of outputs spit out by a game object, and can upload .png's
    if thelist:
        for item in thelist:
            if ".png" in item:
                await gameboi.send_file(thechannel, fp=item)
            else:
                await gameboi.send_message(thechannel, item)


#############################################################################
############################################################################# GAMES
#############################################################################

class countToThree(GameLobby):
    name = "Co-op Counting"
    numPlayers = (2, 4)
    def __init__(self, people):
        super().__init__(people)
        for person in people:
            Lobby.idsInLobby[person.id] = self
        self.count = 0
        self.goal = 3
        self.initMessage = ["Type 'yee' (anyone of you) to advance the count to 3. Current count at: " + str(self.count)]
    def eval(self, message):
        print(message.content)
        if message.content.lower() == ("yee"):
            self.count += 1
            if self.count >= self.goal:
                self.close()
                return ["Yay yall counted to three!"]
            return ["Current count at: " + str(self.count)]
GameLobby.gamesList[countToThree.name] = countToThree



#############################################################################
############################################################################# RUN
#############################################################################

# gameboi.run("MjYyODE4Mzg4MDk3NzYxMjgw.DBY6Rw.ugTBLNQMhX7ImQ0sgrS4CPAI-Mg")  # runs on account "gameboi"
gameboi.run("MjUzMzA3ODIwNjk3NDUyNTQ1.DBY7VQ.ABcabZxrv0JDU722RO2YuWn07L0")  # runs on account "testboi"


