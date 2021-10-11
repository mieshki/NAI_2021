#from curses.ascii import isupper

from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax
import chess
import chess.engine
import time

BOARD_WIDTH = 8
BOARD_HEIGHT = 8

class ChessGame(TwoPlayerGame):

    def __init__(self, players=None):
        self.board = chess.Board()
        self.players = players
        self.score = 53
        self.current_player = 2
        self.scores = [0, 0]
        self.score_to_decrement = 0
        self.last_move = None
        self.beated_piece = None
        self.start_time = time.time()

    def possible_moves(self):
        moves = list(self.board.legal_moves)
        return moves

    def make_move(self, move):
        self.board.push_san(str(move))

    def win(self):
        return self.board.is_variant_win()

    def is_over(self):
        return self.board.is_game_over()

    def show(self):
        print(f'Time of execution: {time.time() - self.start_time} seconds')
        print(self.board)
        outcome = self.board.outcome()
        if outcome is not None:
            print(f'Termination: {outcome.termination.name}, result: {outcome.result()}')
        self.start_time = time.time()
        #print(self.board.unicode(borders=True, empty_square='- '))

    def scoring(self):
        total_score = 0
        score = 0
        white_score = 0
        black_score = 0
        #print(self.current_player)
        for c in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            for i in range(1, 9):
                current_piece = self.board.piece_at(chess.parse_square(f'{c}{i}'))
                if current_piece is not None:
                    piece_type = current_piece.piece_type
                    # [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]
                    if piece_type == 1:  # PAWN
                        score = 10
                    elif piece_type == 2:  # KNIGHT
                        score = 30
                    elif piece_type == 3:  # BISHOP
                        score = 30
                    elif piece_type == 4:  # ROOK
                        score = 50
                    elif piece_type == 5:  # QUEEN
                        score = 90
                    elif piece_type == 6:  # KING
                        score = 1000

                #current_player = 1 - white
                #current_player = 2 - black

                if str(current_piece).isupper():
                    # White
                    white_score += score
                    if self.current_player == 1:
                        # White playing
                        total_score += score
                    else:
                        # Black playing
                        total_score -= score
                else:
                    # Black
                    black_score += score
                    if self.current_player == 2:
                        # Black playing
                        total_score += score
                    else:
                        # White playing
                        total_score -= score

        #is_check_or_check_mate = self.board.is_check() or self.board.is_checkmate()
        if self.board.is_check():
            total_score += 100
        elif self.board.is_checkmate():
            total_score += 10000

        if self.board.is_seventyfive_moves() or self.board.is_fivefold_repetition():
            total_score -= 1000

        if self.board.is_repetition(2):
            total_score -= 90

        if self.board.is_stalemate():
            total_score -= 300

        return total_score

# Start a match (and store the history of moves when it ends)
depth = 4
ai = Negamax(depth) # The AI will think 13 moves in advance
#ai2 = Negamax(depth) # The AI will think 13 moves in advance
#game = ChessGame( [ AI_Player(ai), Human_Player() ] )
game = ChessGame([AI_Player(ai), AI_Player(ai)])
history = game.play()
