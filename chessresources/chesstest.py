import chess
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from random import choice

b = chess.Board()

n = "test"
def renderBoard(board, name):
    bsvg = board._repr_svg_()
    bfile = open("chessresources/" + n + ".svg", "w")
    bfile.write(bsvg)
    bfile.close()
    bpic = svg2rlg("chessresources/" + n + ".svg")
    renderPM.drawToFile(bpic, "chessresources/" + n + ".png")
# renderBoard(b, n)

movenum = 0
print(str(b), "\nMove Number:", movenum, "\nCurrent Status:", b.result(), type(b.result()))
while not b.is_game_over():
    b.push(choice(list(b.legal_moves)))
    movenum += 1
    print(str(b), "\nMove Number:", movenum, "\nCurrent Status:", b.result())
print("Is Checkmate:", b.is_checkmate())
print("Is Stalemate:", b.is_stalemate())
print("Is FUBAR:", b.is_insufficient_material())

# print(str(b), b.result())
# print(list(b.legal_moves))

# c = chess.Move.from_uci("a1a2")
# print(c in b.legal_moves)