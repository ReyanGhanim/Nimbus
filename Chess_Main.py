"""
This is the main driver file. It is responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
import Chess_Engine, Chess_AI

WIDTH = HEIGHT = 512
DIMENSION = 8 #chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #animations
IMAGES = {}

'''
Initialize dictionary of images, this will be called just once in the main
'''
def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.image.load("Images/" + piece + ".png")
    # images can be accessed by saying 'IMAGES['wP']'

'''
Main driver for the code. Handles user input and updating the graphics
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Chess_Engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag for when a move is made
    animate = False #flag vairable for when we should animate a move
    loadImages() #only done once, before the while loop
    running = True
    sqSelected = () #initializes square selection, keeps track of last click of the user (tuple: row, col)
    playerClicks = [] #keeps track of player clicks (two tuples: [(6, 4), (4, 4)]
    gameOver = False
    playerOne = False # human playing white = True, AI playing white = False
    playerTwo = True # human playing black = True, AI playing black = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # if you add a sidebar or border, adjust this so it's relative to board
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # user clicked same square
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    if len(playerClicks) == 2:  # after 2nd click:
                        move = Chess_Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () #resets user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z is pressed on keyboard
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r: #board resets if 'r' is pressed
                    gs = Chess_Engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        #move finder for AI
        if not gameOver and not humanTurn:
            AIMove = Chess_AI.findActualBestMove(gs, validMoves)
            if AIMove is None: # this shouldn't happen
                AIMove = Chess_AI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False


        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
                """if e.type == p.KEYDOWN:
                    if e.key == p.K_r:
                        gameOver = False"""
            else:
                drawText(screen, 'White wins by checkmate')
                """if e.type == p.KEYDOWN:
                    if e.key == p.K_r:
                        gameOver = False"""
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')
            """if e.type == p.KEYDOWN:
                if e.key == p.K_r:
                    gameOver = False"""

        clock.tick(MAX_FPS)
        p.display.flip()

"""
Highlights square selected and valid moves for selected piece
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE)) #actual highlight func
            s.set_alpha(100) #sets a transparency value
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight possible moves
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
"""if len(gs.moveLog) != 0:
lastMove = []
lastMove.append(gs.moveLog[-1])
print(move.getChessNotation())
if lastMove != ():
    r_initial = lastMove[0]
    print(r_initial)
    r_final = lastMove[2]
    c_initial = lastMove[1]
    c_final = lastMove[3]
    s = p.Surface((SQ_SIZE, SQ_SIZE))  # actual highlight func
    s.set_alpha(100)  # sets a transparency value
    s.fill(p.Color('blue'))
    screen.blit(s, (c_final * SQ_SIZE, r_final * SQ_SIZE))"""

"""
Responsible for all graphics in a current game state
"""

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range (DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

""""
Draw the pieces on the board using the current GameState.board
"""

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Animates moves
"""
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames through one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erases piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont('Helvitca', 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()











