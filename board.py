import copy
from typing import List, Tuple, Union

from core_algorithm.algorithms import fit_pattern

from constants import *


def format_number(num: int, format_length: int = 2) -> str:
    if len(str(num)) == format_length:
        return str(num)
    else:
        out = "0" * (format_length - len(str(num)))
        return out + str(num)


def fit_pattern_old(sequence: list, pattern: tuple, main_player: int, margin_effect: bool = True) -> int:
    """
    Find the number of patterns appear in sequence
    :param main_player: Main player number in pattern
    :param margin_effect: Whether the margin of board will be consider as an obstacle when calculate
    :param sequence: The main sequence
    :param pattern: Pattern in the object sequence
    :return: The number of patterns appear in the sequence
    """
    main_length = len(sequence)
    sub_length = len(pattern)

    sequence = sequence[:]
    if margin_effect:
        add_player = 1 if main_player == 2 else 2
        sequence.insert(0, add_player)
        sequence.append(add_player)

    if main_length < sub_length:
        return 0
    elif main_length == sub_length:
        return 1 if sequence == list(pattern) else 0
    else:
        count = 0
        for start in range(main_length - sub_length + 1):
            if sequence[start: start + sub_length] == list(pattern):
                count += 1
        return count


class ChessBoard:
    def __init__(
            self, p1: str, p2: str, data: List[List] = None, size: Tuple = (15, 15)
    ):
        # Create main board
        # Note: the x and y coordinate are stored reversely in self.board than in real board.
        # That is: x is vertical coordinate here, while y is horizontal coordinate
        if not data:
            self.board = [[0 for _ in range(size[0])] for _ in range(size[1])]
        else:
            self.board = data

        # Record all operations
        # Format: (player, (x, y))
        self.operations = []

        # Currently, board size must be 15*15
        assert size == (15, 15), "Currently, board size must be 15*15"
        self.size = size
        # The next player set the chess. 1 for black and 2 for white. Always black first.
        self.next_turn = 1

        # Set mode
        if p1 not in ["p", "c"]:
            raise ValueError("Player must be 'p' or 'c', {} given!".format(p1))
        if p2 not in ["p", "c"]:
            raise ValueError("Player must be 'p' or 'c', {} given!".format(p2))
        # Currently, there are three modes:
        # player vs. player, player vs. computer, computer vs. computer(this will turn into training process in future)
        self.mode = p1, p2

        self.freeze = False

    def win_determine(
            self, x: Union[int, None] = None, y: Union[int, None] = None
    ) -> int:
        """
        Determine if there's player win in the chessboard
        :param x: x coordinate of last chess
        :param y: y coordinate of last chess
        :return: a integer determine who wins the game (1 for black, 2 for white, 3 for tie, and 0 for no on win)
        """
        # Tie
        for line in self.board:
            for each in line:
                if each == 0:
                    break
            else:
                continue
            break
        else:
            return TIE

        # Detect according to the last chess set
        if all((isinstance(x, int), isinstance(y, int))):
            # Horizontal
            start_x = x - 4 if x - 4 >= 0 else 0
            end_x = x if x + 4 < 15 else 10
            for current_x in range(start_x, end_x + 1):
                result = self._all_same(
                    [self.board[new_x][y] for new_x in range(current_x, current_x + 5)]
                )
                if result:
                    return BLACK_WIN if self.board[x][y] == 1 else WHITE_WIN

            # Vertical
            start_y = y - 4 if y - 4 >= 0 else 0
            end_y = y if y + 4 < 15 else 10
            for current_y in range(start_y, end_y + 1):
                result = self._all_same(
                    [self.board[x][new_y] for new_y in range(current_y, current_y + 5)]
                )
                if result:
                    return BLACK_WIN if self.board[x][y] == 1 else WHITE_WIN

            # Diagonal
            # Upper-left to Down-right
            nearest_to_upper_left = min(x, y)
            if nearest_to_upper_left < 4:
                start_x = x - nearest_to_upper_left
                start_y = y - nearest_to_upper_left
            nearest_to_down_right = min(14 - x, 14 - y)
            if nearest_to_down_right < 4:
                end_x = x - (4 - nearest_to_down_right)
            for index, current_x in enumerate(range(start_x, end_x + 1)):
                current_y = start_y + index
                result = self._all_same(
                    [self.board[current_x + d][current_y + d] for d in range(0, 5)]
                )
                if result:
                    return BLACK_WIN if self.board[x][y] == 1 else WHITE_WIN

            # Down-left to Upper-right
            nearest_to_down_left = min(x, 14 - y)
            if nearest_to_down_left < 4:
                start_x = x - nearest_to_down_left
                start_y = y + nearest_to_down_left
            else:
                # Here need to re-calculate start x and y because they are changed previously
                start_x = x - 4
                start_y = y + 4
            nearest_to_upper_right = min(14 - x, y)
            if nearest_to_upper_right < 4:
                end_x = x - (4 - nearest_to_upper_right)
            else:
                # Need to re-calculate end x as the same reason above
                end_x = x
            for index, current_x in enumerate(range(start_x, end_x + 1)):
                current_y = start_y - index
                result = self._all_same(
                    [self.board[current_x + d][current_y - d] for d in range(0, 5)]
                )
                if result:
                    return BLACK_WIN if self.board[x][y] == 1 else WHITE_WIN

        else:
            for each in self.split_board():
                if fit_pattern(each, (1, 1, 1, 1, 1), 1):
                    return BLACK_WIN
                elif fit_pattern(each, (2, 2, 2, 2, 2), 2):
                    return WHITE_WIN
        return CONTINUE

    def get_board(self):
        return copy.copy(self.board)

    def copy_board(self):
        """
        This function is used to calculate winning possibilities
        :return: Chessboard instance with initial data of current board.
        """
        return ChessBoard(self.mode[0], self.mode[1], data=self.board)

    def set_chess(self, x: int, y: int, reset: bool = False):
        """
        Set a chess to board and return if there's a player win the game
        :param x: x coordinate
        :param y: y coordinate
        :param reset: initialize the position (turn the date into 0)
        :return:
        """
        # Check input
        if x not in range(self.size[0]):
            raise ValueError(
                "X coordinate should be in range 0~{}, {} given!".format(self.size[0], x)
            )
        if y not in range(self.size[1]):
            raise ValueError(
                "Y coordinate should be in range 0~{}, {} given!".format(self.size[1], y)
            )

        # Add operation to recorder
        self.operations.append((self.next_turn, (x, y)))
        if reset:
            self.board[x][y] = 0
        else:
            self.board[x][y] = self.next_turn
            # Switch the value of self.next_turn from 1 to 2 or vise versa
            self.next_turn = 1 if self.next_turn == 2 else 2
        return self.win_determine(x, y)

    def withdraw(self):
        """
        Usage: next(self.withdraw())
        :return: Generator, return (player, (x, y))
        """
        operation_length = len(self.operations)
        withdraw_times = 0
        while True:
            withdraw_times += 1
            if not self.operations:
                raise ValueError(
                    "Stored {} operations, {} withdraw times given!".format(operation_length, withdraw_times)
                )
            withdraw_item = self.operations.pop()
            self.set_chess(withdraw_item[1][0], withdraw_item[1][1], reset=True)
            yield withdraw_item

    @staticmethod
    def _all_same(lst: list) -> bool:
        """
        Determine is all the elements in the given iterable is same(despite the condition of all 0)
        :return: if there is player win
        """
        first = lst[0]
        if first == 0:
            return False
        for item in lst[1:]:
            if item != first:
                return False
        return True

    def split_board(self):
        """
        This generator split board vertically, horizontally and diagonally into one-dimension arrays
        :return: Yield all split arrays one by one
        """
        new_board = self.get_board()
        yield from self.board[:]
        for index, _ in enumerate(self.board[:]):
            yield [new_board[x][index] for x in range(15)]
        # Diagonal
        for base in range(29):
            yield [
                new_board[x][base - x]
                for x in range(
                    0 if base <= 14 else base - 14, base + 1 if base <= 14 else 15
                )
            ]
        for diff in range(-14, 15):
            yield [
                new_board[x][x + diff]
                for x in range(
                    abs(diff) if diff < 0 else 0, 15 if diff < 0 else 15 - diff
                )
            ]

    # Evaluate part
    @staticmethod
    def evaluate(player: int, split_board: list) -> int:
        """
        Evaluate the situation on chessboard for one player, calculate an int as the result.
        :param split_board: result list from self.split_board
        :param player: 1 for black and 2 for white
        :return: Current situation. Bigger the outcome, more favourable the situation to the player
        """
        score = 0
        for line in split_board:
            for pattern in PATTERNS.keys():
                all_pattern = PATTERNS[pattern][player]
                # print(all_pattern)
                for each in all_pattern:
                    # print("    " + str(each))
                    score += STANDARDS[pattern] * fit_pattern(line, each, player)
        return score

    def __repr__(self):
        """
        Should output x and y reversely, since they are stored differently in self.board
        """
        out = "   "
        for x in range(self.size[0]):
            temp_x = format_number(x)
            out += "{} ".format(temp_x)
        out += "\n"
        for y in range(self.size[0]):
            temp_y = format_number(y)
            out += "{}".format(temp_y)
            for x in range(self.size[1]):
                out += "  {}".format(str(self.board[x][y]))
            out += "\n"
        return out

    def __hash__(self):
        temp = []
        for each in self.board:
            temp.append(tuple(each))
        return hash(tuple(temp))
