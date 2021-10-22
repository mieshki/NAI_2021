"""
    Zmierz się ze sztuczną intelignecją w szachach :)
    Zasady gry w szachy: https://pl.wikipedia.org/wiki/Zasady_gry_w_szachy
    W celu dokonania ruchu użyj notacji algebraicznej wpisując do konsoli swój ruch.
    Na przykład: ruch pionkiem z pola a2 na pole a3 będzie wyglądać następująco a2a3.

    W celu możliwości uruchomienia gry należy pobrać i zainstalować bibliotekę easyAi i chess.
    W konsoli użyj komendy 'pip install -r /path/to/requirements.txt' pozwoli na automatyczną instalację potrzebnych bibliotek

    Autorzy: Mieszko Dziadowiec, Aleksander Reiter
"""
from easyAI import TwoPlayerGame, AI_Player, Human_Player, Negamax
import chess

class Chess(TwoPlayerGame):

    def __init__(self, players=None):
        self.players = players
        self.board = chess.Board()
        self.moves = 0
        self.current_player = 1  # player 1 starts

    def possible_moves(self):
        # pobieramy listę możliwych ruchów dla danego użytkownika
        self.moves = list(self.board.legal_moves)
        return self.moves

    def make_move(self, move):
        self.board.push(move)

    def unmake_move(self, move):
        # usuwamy ostatni ruch ze stosu
        self.board.pop()

    def is_over(self):
        return self.board.is_game_over(claim_draw=True)

    def scoring(self):
        score = 0
        for move in self.possible_moves():
            try:
                opponent_piece = self.board.piece_at(chess.parse_square(str(move)[:-2]))
            except:
                opponent_piece = None
            # Przypisanie punktów za bicie pionków
            if opponent_piece is not None:
                if opponent_piece.piece_type == 1:
                    score += 10
                elif opponent_piece.piece_type == 2:
                    score += 30
                elif opponent_piece.piece_type == 3:
                    score += 30
                elif opponent_piece.piece_type == 4:
                    score += 50
                elif opponent_piece.piece_type == 5:
                    score += 90
                elif opponent_piece.piece_type == 6:
                    score += 40
            # premiujemy ruch dający szacha
            if self.board.gives_check(move):
                return 2000
        # punktami karnymi zmuszamy AI do nie powtarzania się
        if self.board.is_repetition(2):
            score -= 150
        # punkty karne za dążenie do przegranej
        if self.board.is_stalemate():
            score -= 1000
        if self.board.is_check():
            score -= 500
        if self.board.is_checkmate():
            score -= 2000
        if self.board.can_claim_fifty_moves() or self.board.can_claim_threefold_repetition():
            score -= 500
        return score

    def show(self):
        print(self.board)
        outcome = self.board.outcome(claim_draw=True)
        if outcome is not None:
            winner = "WHITE" if outcome.winner is True else "BLACK"
            print(outcome.termination.name, winner, outcome.result())


if __name__ == "__main__":
    print(__doc__)
    ai = Negamax(3, win_score=2000)

    # game = CHess([AI_Player(ai), Human_Player()])
    game = Chess([AI_Player(ai), AI_Player(ai)])
    game.play()
