"""
This class is responsible for storing all the information about the current state of a chess game. It will also be
responsible for determining the valid moves at the current state. It will also keep a move log.
"""

class GameState():
    def __init__(self):
        # Board is an 8x8 2D list, each element of the list has 2 characters.
        # First character represents the color of the piece, "w" or "b"
        # Second character represents the type of piece, "R", "N", "B", "Q", or "K"
        # "--" represents an empty space with no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () #coordinates where enpassant is possible
        self.enPassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]


    """"
    Takes move as a parameter and execute it (doesn't work for castling, en-passant, and pawn promotion
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #logs move, display history or under later
        self.whiteToMove = not self.whiteToMove #swaps turns
        # update the king's location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #Pawn Promotion, possibly extend to more piece options
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #Update enpassantPossible variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: # Only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()

        #En Passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' #Captures the pawn


        #Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves rook
                self.board[move.endRow][move.endCol+1] = '--'
            else: #queenside castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'

        self.enPassantPossibleLog.append(self.enpassantPossible)

        #This updates castling rights - king or rook moves
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    """
    Undo last move made
    """
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure there's a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #swaps turns back
            #update king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo EnPassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #Leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enPassantPossibleLog.pop()
            self.enpassantPossible = self.enPassantPossibleLog[-1]

            #Undo Castling Rights
            self.castleRightsLog.pop() #undoes past castle rights
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs) #sets current castling right to the last on the list

            #Undo Castle Move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #Queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False

    """
    Updates castling rights based on move
    """
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                if move.startCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                if move.startCol == 7: #right rook
                    self.currentCastlingRight.bks = False

        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False
    """
    Moves considering checks
    """
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                       self.currentCastlingRight.wqs, self.currentCastlingRight.bqs) # copies current castling rights
        # generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # for each move, make the move
        for i in range(len(moves)-1, -1, -1): #when removing and iterating through a list, move backwards in the list
            self.makeMove(moves[i])
            # generate opponent's moves
            # see if any opponent move attacks your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) #if they attack king, move isn't valid
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: #stalemate or checkmate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True


        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves


    """
    determines if current play is in check
    """
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    """
    Determine if enemy can attack square r, c
    """
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switches to opponent's view
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switches move back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    """
    Moves not considering checks
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])): #number of columns in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls move function based on piece type
        return moves
    """
    Find all pawn moves for the pawn location at row, column and add these moves to the list
    """
    def getPawnMoves (self, r, c, moves):
        if self.whiteToMove: #white pawns
            if self.board[r-1][c] == "--": #advance pawn 1 square
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #advance pawn 2 squares
                    moves.append(Move((r,c), (r-2, c), self.board))
            if c-1 >= 0: # captures to the left
                if self.board[r-1][c-1][0] == 'b': #black piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == 'b': #black piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
        else: # black pawn moves
            if self.board[r+1][c] == "--": #advance pawn 1 square
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": #advance pawn 2 squares
                    moves.append(Move((r,c), (r+2, c), self.board))
            if c-1 >= 0: #captures to the right
                if self.board[r+1][c-1][0] == 'w': #white piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7: #captures to the left
                if self.board[r+1][c+1][0] == 'w': #white piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))

    """
    Find all rook moves for the rook location at row, column and add these moves to the list
    """
    def getRookMoves(self, r, c, moves):
        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    """
    Find all knight moves for the knight location at row, column and add these moves to the list
    """
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
    """
    Find all bishop moves for the bishop location at row, column and add these moves to the list
    """
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break
    """
    Find all Queen moves for the Queen location at row, column and add these moves to the list
    """
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    """
    Find all King moves for the King location at row, column and add these moves to the list
    """
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (1, 1), (1, -1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Generates all valid castle moves for king at (r, c) and adds them to the list of moves
    """
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return #Castling not allowed while in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # Translates row/column values to rank/file chess notation
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}


    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #Pawn Promotion
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        #En Passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        #Castle Move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


