from functools import lru_cache
from random import sample
from typing import Tuple

from core_algorithm.algorithms import evaluate_point

from board import ChessBoard
from constants import *


def min_max_search(board: ChessBoard, ai_num: int, control_bar, depth: int = 6):
    """
    Min-max search to find the best place of setting chess
    :param control_bar: class Bar from main.py
    :param ai_num: The player number which ai is
    :param board: chessboard
    :param depth: depth of calculation NOTE: GREAT NUMBER OF DEPTH MAY SPEND A LONG TIME
    :return: the coordinate of best position
    """
    # If the board is empty
    for x in board.board:
        for y in x:
            if y != 0:
                break
        else:
            continue
        break
    else:
        control_bar.exit()
        return 7, 7

    max_v = -99999999
    points = points_gen(board, ai_num)
    candidates = []

    # Show progress bar
    for point in points:
        control_bar.step_in()

        board.board[point[0]][point[1]] = ai_num
        cur_v = search_point(
            board, ai_num, 1 if ai_num == 2 else 2, depth, -9999999999, 9999999999
        )
        if cur_v == max_v:
            candidates.append(point)
        elif cur_v > max_v:
            max_v = cur_v
            candidates = [point]
        board.board[point[0]][point[1]] = 0
    result = sample(candidates, 1)[0]
    control_bar.exit()
    return result


# TODO: need speed up
@lru_cache()
def search_point(
        board: ChessBoard, ai_num: int, player: int, depth: int, alpha: int, beta: int
):
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
    split_board = list(board.split_board())
    v = board.evaluate(ai_num, split_board) - board.evaluate(
        1 if ai_num == 2 else 2, split_board
    )
    if depth <= 0 or board.win_determine() in [WHITE_WIN, BLACK_WIN, TIE]:
        return v
    points = points_gen(board, player)

    if player == ai_num:
        # Computer turn, max level
        for point in points:
            board.board[point[0]][point[1]] = player
            cur_v = search_point(
                board, ai_num, 1 if player == 2 else 2, depth - 1, alpha, beta
            )
            board.board[point[0]][point[1]] = 0
            alpha = max(alpha, cur_v)
            # Prune
            if beta < alpha:
                # print("Pruned {} nodes".format(len(points) - points.index(point) - 1))
                break
        return alpha
    else:
        # Human turn, min level
        for point in points:
            board.board[point[0]][point[1]] = player
            cur_v = search_point(
                board, ai_num, 1 if player == 2 else 2, depth - 1, alpha, beta
            )
            board.board[point[0]][point[1]] = 0
            beta = min(beta, cur_v)
            # Prune
            if beta < alpha:
                print("Pruned {} nodes".format(len(points) - points.index(point) - 1))
                break
        return beta


def points_gen(board: ChessBoard, player: int, distance: int = 2) -> list:
    """
    Generate all the effective points to put chess on.
    This function return the coordinate of points by determine the distance between nearest chess and the point in order
    :param player: current player number
    :param distance: The max distance to chess when selecting points
    :param board: chessboard
    :return:
    """
    five, four, double_three, three, two, others, far = [], [], [], [], [], [], []
    for x in range(15):
        for y in range(15):
            if board.board[x][y] == 0:
                if has_neighbor(board, (x, y), 1):
                    score_com = evaluate_point(board, (x, y), player)
                    score_hum = evaluate_point(board, (x, y), 1 if player == 2 else 2)

                    if score_com >= STANDARDS["5+"]:
                        return [(x, y)]
                    elif score_hum >= STANDARDS["5+"]:
                        five.append((x, y))
                    elif score_com >= STANDARDS["4+"]:
                        four.insert(0, (x, y))
                    elif score_hum >= STANDARDS["4-"]:
                        four.append((x, y))
                    elif score_com >= STANDARDS["3+"] * 2:
                        double_three.insert(0, (x, y))
                    elif score_hum >= STANDARDS["3+"] * 2:
                        double_three.append((x, y))
                    elif score_com >= STANDARDS["3+"]:
                        three.insert(0, (x, y))
                    elif score_hum >= STANDARDS["3+"]:
                        three.append((x, y))
                    elif score_com >= STANDARDS["2+"]:
                        two.insert(0, (x, y))
                    elif score_hum >= STANDARDS["2+"]:
                        two.append((x, y))
                    else:
                        others.append((x, y))
                elif has_neighbor(board, (x, y), 2):
                    far.append((x, y))
    if five:
        return [five[0]]
    if four:
        return four
    if double_three:
        return double_three
    three.extend(two)
    three.extend(others)
    three.extend(far)
    return three


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


if __name__ == "__main__":
    a = ChessBoard("p", "p")
    a.set_chess(4, 6)
    print(has_neighbor(a, (3, 4), depth=2))
    print(points_gen(a, 1))
