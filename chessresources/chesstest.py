import chess
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPDF, renderPM

b = chess.Board()

# for m in b.legal_moves:
#     print(m)

bsvg = b._repr_svg_()
filetowriteto = open("test.SVG", "w")
filetowriteto.write(bsvg)
filetowriteto.close()