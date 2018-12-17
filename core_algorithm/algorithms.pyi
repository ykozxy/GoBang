from board import ChessBoard


def fit_pattern(
        sequence: list, pattern: tuple, main_player: int, margin_effect: bool = True
) -> int: ...


def evaluate_point(board: ChessBoard, point: tuple, player: int) -> int: ...
