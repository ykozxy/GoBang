from random import sample
from typing import Tuple

import tqdm

from board import ChessBoard


def min_max_search(board: ChessBoard, ai_num: int, depth: int = 4) -> Tuple[int, int]:
    """
    Min-max search to find the best place of setting chess
    :param ai_num: The player number which ai is
    :param board: chessboard
    :param depth: depth of calculation NOTE: GREAT NUMBER OF DEPTH MAY SPEND A LONG TIME
    :return: the coordinate of best position
    """
    max_v = -99999999
    points = points_gen(board)
    candidates = []

    # Show progress bar
    bar = tqdm.tqdm(total=len(points))
    for point in points:
        bar.update(1)
        board.board[point[0]][point[1]] = ai_num
        cur_v = evaluate_point(board, ai_num, 1 if ai_num == 2 else 2, depth, -999999999, 999999999)
        if cur_v == max_v:
            candidates.append(point)
        elif cur_v > max_v:
            max_v = cur_v
            candidates = [point]
        board.board[point[0]][point[1]] = 0
    return sample(candidates, 1)[0]


def evaluate_point(board: ChessBoard, ai_num: int, player: int, depth: int, alpha: int, beta: int):
    """
    This function use alpha-beta pruning to calculate best-fit point
    :param board: chessboard
    :param ai_num: The player number which ai is
    :param player: current player number
    :param depth: maximum depth of calculation
    :param alpha: max value when calculate
    :param beta: min value when calculate
    :return: the maximum score of the position
    """
    # Computer - Human
    v = board.evaluate(ai_num) - board.evaluate(1 if ai_num == 2 else 2)
    if depth <= 0 or board.win_determine():
        return v
    points = points_gen(board)

    if player == ai_num:
        # Computer turn, max level
        max_v = -99999999
        for point in points:
            board.board[point[0]][point[1]] = player
            cur_v = evaluate_point(board, ai_num, 1 if player == 2 else 2, depth - 1, alpha, max(beta, max_v))
            board.board[point[0]][point[1]] = 0
            max_v = max(max_v, cur_v)
            # Prune
            if cur_v > alpha:
                break
        return max_v
    else:
        # Human turn, min level
        min_v = 9999999999
        for point in points:
            board.board[point[0]][point[1]] = player
            cur_v = evaluate_point(board, ai_num, 1 if player == 2 else 2, depth - 1, min(alpha, min_v), beta)
            board.board[point[0]][point[1]] = 0
            min_v = min(min_v, cur_v)
            # Prune
            if cur_v < beta:
                break
        return min_v


def points_gen(board: ChessBoard, distance: int = 2):
    """
    Generate all the effective points to put chess on.
    This function return the coordinate of points by determine the distance between nearest chess and the point in order
    :param distance: The max distance to chess when selecting points
    :param board: chessboard
    :return:
    """
    final = []
    for x in range(15):
        for y in range(15):
            if board.board[x][y] == 0 and has_neighbor(board, (x, y), distance):
                final.append((x, y))
    return final


def has_neighbor(board: ChessBoard, point: Tuple[int, int], depth: int) -> bool:
    """
    Determine whether a point has neighbor which is filled
    :param depth: depth of calculation
    :param board: chessboard
    :param point: point wants to calculate
    :return: whether a point has neighbor which is filled
    """
    x, y = point
    all_points = [
        board.board[cx][cy]
        # (cx, cy)
        for cx in range(
            x - depth if x - depth >= 0 else 0, x + depth + 1 if x + depth <= 14 else 15
        )
        for cy in range(
            y - depth if y - depth >= 0 else 0, y + depth + 1 if y + depth <= 14 else 15
        )
    ]
    if any((1 in all_points, 2 in all_points)):
        return True
    return False


if __name__ == '__main__':
    a = ChessBoard('p', 'p')
    a.set_chess(4, 6)
    print(has_neighbor(a, (3, 4), depth=2))
    print(points_gen(a))