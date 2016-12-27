import discord
import asyncio
from PIL import Image

gameboi = discord.Client()   

#############################################################################
############################################################################# CLIENT
#############################################################################

@gameboi.event
async def on_ready():
    print('Gameboi Successfully Booted!')
    print('  -user name: '+gameboi.user.name)
    print('  -user id: '+gameboi.user.id)

waiting = ([], [], [])
@gameboi.event
async def on_message(message):
    if message.author in Game.currently_playing:
        await send_list(message.channel, Game.currently_playing[message.author].play(message.content, message.author))
    elif message.author in waiting[1]:
        i = waiting[1].index(message.author)
        p1 = waiting[0].pop(i)
        p2 = waiting[1].pop(i)
        if message.content.lower() == "yes":
            thegame = waiting[2].pop(i)
            await gameboi.send_message(message.channel, "Launching "+thegame.name)
            game = thegame(p1, p2)
            await send_list(message.channel, game.init_output)
        else:
            await gameboi.send_message(message.channel, "Game challenge has been declined")
    elif message.content.startswith(gameboi.user.mention):
        msgiter = iter(message.content.split())
        next(msgiter)
        try:
            current = next(msgiter).lower()
            if current == 'help':
                await gameboi.send_message(message.channel, "Mention me with these commands: \n-help: see commands \n-games: see list of games \n-play <game name> <your opponent's name or nickname or mention>: play a game \n-cancel: cancel a game challenge")
            elif current == 'games':
                out = ""
                await gameboi.send_message(message.channel, "Games you can play:")
                for game in Game.games_list:
                    out = out + "\n-" + game
                await gameboi.send_message(message.channel, out)
            elif current == 'play':
                current = next(msgiter).lower()
                if message.author in waiting[0]:
                    await gameboi.send_message(message.channel, "You have currently challenged someone to a game\nMention me with 'cancel' to cancel your request")
                elif current in Game.games_list:
                    thegame = Game.games_list[current]
                    other_player = await find_user(next(msgiter), message.channel)
                    if other_player:
                        if other_player == message.author:
                            await gameboi.send_message(message.channel, "Congratulations, you just played yourself")
                        elif other_player == gameboi.user:
                            await gameboi.send_message(message.channel, "Thanks, but I'm sure you would win")
                        elif other_player in Game.currently_playing:
                            await gameboi.send_message(message.channel, "User is in another game")
                        elif other_player in waiting[0] or other_player in waiting[1]:
                            await gameboi.send_message(message.channel, "User is currently challenging someone else or being challenged by someone else")
                        else:
                            await gameboi.send_message(message.channel, other_player.mention+"! "+message.author.name+" has challenged you to a game of "+thegame.name+"!\nType 'yes' to accept or anything else to decline")
                            waiting[0].append(message.author)
                            waiting[1].append(other_player)
                            waiting[2].append(thegame)
                else:
                    await gameboi.send_message(message.channel, "Game not found.\nMention me with 'games' to see the list of games")
            elif current == 'cancel':
                if message.author in waiting[0]:
                    i = waiting[0].index(message.author)
                    waiting[0].pop(i)
                    waiting[1].pop(i)
                    waiting[2].pop(i)
                    await gameboi.send_message(message.channel, "Game challenge canceled")
                else:
                    await gameboi.send_message(message.channel, "You have not challenged anyone to a game")
            elif current == 'imgtest':
                await gameboi.send_file(message.channel, fp="connect4_background.png")
            else:
                await gameboi.send_message(message.channel, "Command not found.\n'"+gameboi.user.mention+" help' to see commands.")
        except StopIteration:
            await gameboi.send_message(message.channel, "Bad Command.\n'"+gameboi.user.mention+" help' to see commands.")

async def find_user(thename, thechannel):
    for person in thechannel.server.members:
        if person.nick==thename or person.name==thename or person.mention==thename:
            if person.status != discord.Status.online:
                await gameboi.send_message(thechannel, "User not online or active")
            else:
                return person
            break
    else:
        await gameboi.send_message(thechannel, "User not found")

async def send_list(thechannel, thelist):
    if thelist:
        for item in thelist:
            if ".png" in item:
                await gameboi.send_file(thechannel, fp=item)
            else:
                await gameboi.send_message(thechannel, item)

#############################################################################
############################################################################# GAMES
#############################################################################

class Game:
    currently_playing = {}
    games_list = {}

class connect4(Game):
    name = "connect4"
    active_gamenumbers = []
    red = Image.open("connect4_red.png")
    blue = Image.open("connect4_blue.png")
    def __init__(self, player1, player2):
        Game.currently_playing[player1], Game.currently_playing[player2] = self, self
        self.players = (player1, player2)
        self.currentplayer = 0
        self.gamenumber = 0
        while self.gamenumber in connect4.active_gamenumbers:
            self.gamenumber += 1
        connect4.active_gamenumbers.append(self.gamenumber)
        self.board = []
        for _ in range(6):
            row = []
            for _ in range(7):
                row.append('')
            self.board.append(row)
        self.rowlength = len(self.board[0])
        self.collength = len(self.board)
        self.image = Image.open("connect4_background.png")
        self.image.save("connect4_game_"+str(self.gamenumber)+".png")
        self.init_output = ["connect4_game_"+str(self.gamenumber)+".png", "Game Instructions: \n-Get 4 pieces in a row! \n-Type the number of the column to drop a piece! \n-'concede' to give up", self.players[self.currentplayer].name+", it's your turn!"]
    def play(self, inp, person):
        if inp.lower() == "concede" and (person in self.players):
            winner = self.players[1-self.players.index(person)]
            return self.gameover(winner)
        elif self.players[self.currentplayer] == person:
            if inp in [str(i) for i in range(1,self.rowlength+1)]:
                col = int(inp)-1
                row = -1
                while (row+1)<self.collength and not self.board[row+1][col]:
                    row += 1
                if row == -1:
                    return ["Column is full"]

                self.update_board(row, col)
                if self.check_row_win(row, col) or self.check_col_win(row, col) or self.check_leftdiag_win(row, col) or self.check_rightdiag_win(row, col):
                    return self.gameover(self.players[self.currentplayer])
                if self.check_stalemate():
                    return self.gameover(None)

                self.currentplayer = 1-self.currentplayer
                return ["connect4_game_"+str(self.gamenumber)+".png", self.players[self.currentplayer].name+", it's your turn!"]
    def gameover(self, winner):
        for player in self.players:
            Game.currently_playing.remove(player)
        connect4.active_gamenumbers.pop(self.gamenumber)
        if not winner:
            winnertext = "Stalemate!"
        else:
            winnertext = winner.name+" is the winner!"
        return ["connect4_game_"+str(self.gamenumber)+".png", winnertext]

    #Helper Functions
    def update_board(self, row, col):
        if self.currentplayer == 0:
            piecename = 'r'
            pieceimg = connect4.red
        else:
            piecename = 'b'
            pieceimg = connect4.blue
        self.board[row][col] = piecename
        self.image.paste(pieceimg, (col*pieceimg.width, row*pieceimg.width), mask=pieceimg)
        self.image.save("connect4_game_"+str(self.gamenumber)+".png")
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
Game.games_list[connect4.name] = connect4

#############################################################################
############################################################################# RUN
#############################################################################

gameboi.run('MjYyODE4Mzg4MDk3NzYxMjgw.C0JAOQ.p5v3J7zFVhzmtfZKW4yX_7QHF6c')