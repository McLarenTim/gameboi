import discord
from PIL import Image
import chess
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import pokerlib

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
        for person in people:
            Lobby.idsInLobby[person.id] = self
        self.initMessage = []
    def close(self):
        for person in self.people:
            Lobby.idsInLobby.pop(person.id)

class WaitingLobby(Lobby):
    def __init__(self, game, people):
        super().__init__(people)
        self.game = game
        self.checklist = set(people[1:])
        peoplestr = ""
        for person in people[1:]:
            peoplestr += person.mention + " "
        self.initMessage.append("" + people[0].mention + " has challenged " + peoplestr + "to a game of " + game.name + "!\n All challengees must type 'yes' to begin the game. Anyone may type 'no' to decline or cancel.")
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
    minPlayers = 0
    maxPlayers = 0

@gameboi.event
async def on_ready():
    print('Gameboi successfully booted!')
    print('Account: "'+gameboi.user.name+'", ID: '+gameboi.user.id)
    await gameboi.change_presence(game=discord.Game(name="type '@" + gameboi.user.name + " help'"))

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
                    maxPlayers = GameLobby.gamesList[game].maxPlayers
                    minPlayers = GameLobby.gamesList[game].minPlayers
                    if maxPlayers-minPlayers > 0:
                        gamesstr += str(minPlayers) + " to " + str(maxPlayers) + " players."
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
                if not (game.minPlayers <= (len(inviteList)+1) <= game.maxPlayers):
                    if game.maxPlayers-game.minPlayers > 0:
                        raise GameboiException("Wrong number of players for " + gameName + ". Need between " + str(game.minPlayers) + " to " + str(game.maxPlayers) + " players.")
                    else:
                        raise GameboiException("Wrong number of players for " + gameName + ". Need " + str(game.numPlayers[0]) + " players.")
                players = [message.author]
                for name in inviteList:
                    person = findUser(name, message.channel)
                    if person in players:
                        raise GameboiException("Duplicate players found.")
                    if person == gameboi.user:
                        raise GameboiException("Thanks, but no thanks.")
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

async def sendOutputs(destination, thelist):
    if thelist:
        for item in thelist:
            if type(item) == list:
                await sendOutputs(item[0], item[1:])
            elif item.endswith(".png"):
                await gameboi.send_file(destination, fp=item)
            else:
                await gameboi.send_message(destination, item)


#############################################################################
############################################################################# GAMES
#############################################################################

class connect4(GameLobby):
    name = "Connect Four"
    minPlayers = 2
    maxPlayers = 2
    activeGamenumbers = []
    red = Image.open("connect4resources/connect4red.png")
    blue = Image.open("connect4resources/connect4blue.png")
    def __init__(self, people):
        super().__init__(people)
        self.currentPlayer = 0
        self.gameNumber = 0
        while self.gameNumber in connect4.activeGamenumbers:
            self.gameNumber += 1
        connect4.activeGamenumbers.append(self.gameNumber)
        self.board = []
        for _ in range(6):
            row = []
            for _ in range(7):
                row.append('')
            self.board.append(row)
        self.rowlength = len(self.board[0])
        self.collength = len(self.board)
        self.image = Image.open("connect4resources/connect4background.png")
        self.image.save("connect4resources/connect4game" + str(self.gameNumber) + ".png")
        self.initMessage = ["connect4resources/connect4game" + str(self.gameNumber) + ".png", "Game Instructions: \n- Get 4 pieces in a row! \n- Type the number of the column to drop a piece! \n- 'concede' to give up", self.people[self.currentPlayer].name + ", it's your turn!"]
    def eval(self, message):
        if message.content.lower() == "concede":
            winner = self.people[1-self.people.index(message.author)]
            return self.gameover(winner)
        elif self.people[self.currentPlayer] == message.author:
            if message.content in [str(i) for i in range(1,self.rowlength+1)]:
                col = int(message.content)-1
                row = -1
                while (row+1)<self.collength and not self.board[row+1][col]:
                    row += 1
                if row == -1:
                    return ["Column is full"]
                self.updateBoard(row, col)
                if self.check_row_win(row, col) or self.check_col_win(row, col) or self.check_leftdiag_win(row, col) or self.check_rightdiag_win(row, col):
                    return self.gameover(self.people[self.currentPlayer])
                if self.check_stalemate():
                    return self.gameover(None)
                self.currentPlayer = 1 - self.currentPlayer
                return ["connect4resources/connect4game" + str(self.gameNumber) + ".png", self.people[self.currentPlayer].name + ", it's your turn!"]
    def gameover(self, winner):
        self.close()
        connect4.activeGamenumbers.pop(self.gameNumber)
        if not winner:
            winnertext = "Draw! Good game!"
        else:
            winnertext = winner.name+" is the winner!"
        return ["connect4resources/connect4game" + str(self.gameNumber) + ".png", winnertext]
    def updateBoard(self, row, col):
        if self.currentPlayer == 0:
            piecename = 'r'
            pieceimg = connect4.red
        else:
            piecename = 'b'
            pieceimg = connect4.blue
        self.board[row][col] = piecename
        self.image.paste(pieceimg, (col*pieceimg.width, row*pieceimg.width), mask=pieceimg)
        self.image.save("connect4resources/connect4game" + str(self.gameNumber) + ".png")
    def check_row_win(self, row, col):
        color = self.board[row][col]
        combo = 0
        for i in range(self.rowlength):
            if self.board[row][i]==color:
                combo += 1
                if combo==4:
                    return True
            else:
                combo = 0
        return False
    def check_col_win(self, row, col):
        color = self.board[row][col]
        combo = 0
        for i in range(self.collength):
            if self.board[i][col]==color:
                combo += 1
                if combo==4:
                    return True
            else:
                combo = 0
        return False
    def check_leftdiag_win(self, row, col):
        color = self.board[row][col]
        combo = 0
        i, j = row - min(row, col), col - min(row, col)
        while i<self.collength and j<self.rowlength:
            if self.board[i][j]==color:
                combo += 1
                if combo==4:
                    return True
            else:
                combo = 0
            i, j = i+1, j+1
        return False
    def check_rightdiag_win(self, row, col):
        color = self.board[row][col]
        combo = 0
        i, j = row - min(row, self.rowlength-1-col), col + min(row, self.rowlength-1-col)
        while i<self.collength and j>=0:
            if self.board[i][j]==color:
                combo += 1
                if combo==4:
                    return True
            else:
                combo = 0
            i, j = i+1, j-1
        return False
    def check_stalemate(self):
        for i in range(self.rowlength):
            if not self.board[0][i]:
                return False
        return True
GameLobby.gamesList[connect4.name] = connect4

class chessgame(GameLobby):
    name = "Chess"
    minPlayers = 2
    maxPlayers = 2
    activeGamenumbers = []
    def __init__(self, people):
        super().__init__(people)
        self.gameNumber = 0
        while self.gameNumber in chessgame.activeGamenumbers:
            self.gameNumber += 1
        chessgame.activeGamenumbers.append(self.gameNumber)
        self.imgname = "chessresources/chessgame" + str(self.gameNumber)
        self.board = chess.Board()
        self.renderBoard(self.board, self.imgname)
        self.currentPlayer = 1
        self.initMessage = [self.imgname + ".png", "Game Instructions: \n"
                            "- " + self.people[self.currentPlayer].name + " is white.\n"
                            "- " + self.people[1 - self.currentPlayer].name + " is black.\n- Standard chess rules apply.\n"
                            "- Type your moves in UCI format. For example, a move from A7 to A8 would be a7a8 or a7a8q if it is a promotion to a queen.\n"
                            "- Type 'help' during your turn for a list of valid moves."
                            , self.people[self.currentPlayer].name + ", it's your turn!"] # need game instructions! And say who's which color.
    def eval(self, message):
        if message.content.lower() == "concede":
            concedeWinner = self.people[1-self.people.index(message.author)]
            return self.gameover(concedeWinner)
        elif self.people[self.currentPlayer] == message.author:
            try:
                playerMove = chess.Move.from_uci(message.content)
                if playerMove in self.board.legal_moves:
                    self.board.push(playerMove)
                    self.renderBoard(self.board, self.imgname)
                    if self.board.is_game_over(claim_draw=False):
                        return self.gameover(None)
                    else:
                        self.currentPlayer = 1 - self.currentPlayer
                        retval = [self.imgname + ".png"]
                        if self.board.is_check():
                            retval += ["Check!"]
                        retval += [self.people[self.currentPlayer].name + ", it's your turn!"]
                else:
                    retval = ["Move is not legal. Type 'help' for a list of valid moves."]
                return retval
            except ValueError:
                if message.content.lower() == "help":
                    return ["Current legal moves: " + ", ".join([m.uci() for m in self.board.legal_moves])]
    def gameover(self, concedeWinner):
        self.close()
        chessgame.activeGamenumbers.pop(self.gameNumber)
        if not concedeWinner:
            if self.board.is_checkmate():
                text = "Checkmate!" + self.people[self.currentPlayer].name + "is the winner!"
            elif self.board.is_stalemate():
                text = "Stalemate! Good game!"
            elif self.board.is_insufficient_material():
                text = "Draw! Insufficient mating material!"
            elif self.board.is_seventyfive_moves():
                text = "Draw! 75 move rule!"
            elif self.board.is_fivefold_repetition():
                text = "Draw! 5-fold repetition!"
            else:
                text = self.people[self.currentPlayer].name + " has declared a draw!" # need to allow players to claim draws due to 3-fold or 50 move rule
        else:
            text = concedeWinner.name + " is the winner due to concession!"
        return [self.imgname + ".png", text]
    def renderBoard(self, b, n):
        bsvg = b._repr_svg_()
        bfile = open(n + ".svg", "w")
        bfile.write(bsvg)
        bfile.close()
        bpic = svg2rlg(n + ".svg")
        renderPM.drawToFile(bpic, n + ".png")
GameLobby.gamesList[chessgame.name] = chessgame

# class poker(GameLobby):
#     name = "Texas Holdem"
#     minPlayers = 2
#     maxPlayers = 10
#     def __init__(self, people):
#         super().__init__(people)
#         self.count = 0
#         self.goal = 1
#         self.deck = pokerlib.Deck()
#         pmList = []
#         for person in people:
#             pmList.append([person, "Your card this game is: " + str(self.deck.draw())])
#         self.initMessage = ["Type 'yee' to end test."] + pmList
#     def eval(self, message):
#         if message.content.lower() == ("yee"):
#             self.close()
#             return ["Quitting"]
# GameLobby.gamesList[poker.name] = poker


#############################################################################
############################################################################# RUN
#############################################################################

keyFile = open("botaccountkeys.txt", 'r')
key = keyFile.readline().rstrip('\n')
gameboi.run(key)
