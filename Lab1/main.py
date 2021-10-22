"""
Chess rules [PL]: https://www.ikonka.com.pl/kontext/file/2236/KX8940.pdf

Authors:
Reiter, Aleksander <https://github.com/block439>
Dziadowiec, Mieszko <https://github.com/mieshki>

How to run:
'python main.py'
"""

from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax
import chess
import chess.engine
import time

PATH_TO_ENGINE = chess.engine.SimpleEngine.popen_uci('.\\chess_engine\\stockfish.exe')


class ChessGame(TwoPlayerGame):
    def __init__(self, players=None):
        self.board = chess.Board()
        self.players = players
        self.current_player = 1
        self.start_time = time.time()

    def possible_moves(self):
        return list(self.board.legal_moves)

    def make_move(self, move):
        self.board.push(move)

    def unmake_move(self, move):
        self.board.pop()

    def win(self):
        return self.board.is_variant_win()

    def is_over(self):
        return self.board.is_game_over()

    def print_termination_reason_if_end(self):
        outcome = self.board.outcome()
        if outcome is not None:
            print(f'Termination: {outcome.termination.name}, result: {outcome.result()}')

    def get_analysis_from_engine(self):
        info = PATH_TO_ENGINE.analyse(self.board, chess.engine.Limit(depth=10))
        return info

    def print_current_score(self):
        info = self.get_analysis_from_engine()
        print("Score:", info["score"])

    def print_possible_moves(self):
        moves = list(self.board.legal_moves)
        print(moves)

    def print_last_move_execution_time(self):
        print(f'Time of execution: {time.time() - self.start_time} seconds')
        # reset start_time to current time
        self.start_time = time.time()

    def show(self):
        self.print_last_move_execution_time()

        print(self.board)

        self.print_termination_reason_if_end()
        self.print_current_score()
        self.print_possible_moves()

    def scoring(self):
        if self.board.is_checkmate():
            """
            That means current player is being checkmated
            not that current player can check mate an opponent
            """
            return -100000

        info = self.get_analysis_from_engine()

        try:
            """
            Example output from engine:
            PovScore(Cp(+32), WHITE)
            Means that WHITE in this situation is in a little better position
            """
            return info["score"].relative.cp

        except:
            """
            Example: PovScore(Mate(+2), WHITE)
            Means that WHITE can check mate opponent in 2 moves
            Give more score when check mate is available in less moves
            """
            return 20000 - 2000 * info["score"].relative.moves


# Start a match (and store the history of moves when it ends)
ai = Negamax(1, win_score=20000)
#game = ChessGame( [ Human_Player(), AI_Player(ai) ] )
game = ChessGame( [ AI_Player(ai), AI_Player(ai) ] )
history = game.play()
