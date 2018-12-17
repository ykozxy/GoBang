from constants import PATTERNS, STANDARDS

def fit_pattern(list sequence, tuple pattern, int main_player, margin_effect = True):
    """
    Find the number of patterns appear in sequence
    :param main_player: Main player number in pattern
    :param margin_effect: Whether the margin of board will be consider as an obstacle when calculate
    :param sequence: The main sequence
    :param pattern: Pattern in the object sequence
    :return: The number of patterns appear in the sequence
    """
    cdef int main_length = len(sequence)
    cdef int sub_length = len(pattern)

    sequence = sequence[:]
    cdef int add_player
    cdef int count
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


def evaluate_point(board, tuple point, int player):
    """
    Evaluate the score of a specific point in the board
    :param board: Chessboard object
    :param player: 1 for black and 2 for white
    :param point: Coordinate of the point
    :return: Score of the point
    """
    assert board.board[point[0]][point[1]] == 0

    cdef list cases = [board.board[point[0]], [board.board[x][point[1]] for x in range(15)]]
    # Diagonal
    cdef list diagonal = []
    cdef int to_margin = min(point)
    cdef tuple start = (point[0] - to_margin, point[1] - to_margin)
    cdef int i = 0
    cdef int t_x = start[0] + i
    cdef int t_y = start[1] + i
    while t_x < 15 and t_y < 15:
        diagonal.append(board.board[t_x][t_y])
        i += 1
        t_x, t_y = start[0] + i, start[1] + i
    cases.append(diagonal)

    cdef list diagonal1 = []
    cdef int to_margin1 = min(14 - point[0], point[1])
    cdef tuple start1 = (point[0] + to_margin1, point[1] - to_margin1)
    cdef int i1 = 0
    cdef int t_x1 = start1[0] - i1
    cdef int t_y1 = start1[1] + i1
    while t_x1 >= 0 and t_y1 < 15:
        # print(t_x1, t_y1, i1, start1, point, to_margin1)
        diagonal1.append(board.board[t_x1][t_y1])
        i1 += 1
        t_x1, t_y1 = start1[0] - i1, start1[1] + i1
    cases.append(diagonal1)

    ori_score = 0
    for case in cases:
        for pattern in PATTERNS:
            all_pattern = PATTERNS[pattern][player]
            for each in all_pattern:
                ori_score += STANDARDS[pattern] * fit_pattern(case, each, player)

    board.board[point[0]][point[1]] = player
    cases = [board.board[point[0]], [board.board[x][point[1]] for x in range(15)]]
    # Diagonal
    cdef list diagonal2 = []
    cdef int to_margin2 = min(point)
    cdef tuple start2 = (point[0] - to_margin2, point[1] - to_margin2)
    cdef int i2 = 0
    cdef int t_x2 = start2[0] + i2
    cdef int t_y2 = start2[1] + i2
    while t_x2 < 15 and t_y2 < 15:
        diagonal2.append(board.board[t_x2][t_y2])
        i2 += 1
        t_x2, t_y2 = start2[0] + i2, start2[1] + i2
    cases.append(diagonal2)

    cdef list diagonal3 = []
    cdef int to_margin3 = min(14 - point[0], point[1])
    cdef tuple start3 = (point[0] + to_margin3, point[1] - to_margin3)
    cdef int i3 = 0
    cdef int t_x3 = start3[0] - i3
    cdef int t_y3 = start3[1] + i3
    while t_x3 >= 03 and t_y3 < 15:
        # print(t_x3, t_y33, i3, start3, point, to_margin)
        diagonal3.append(board.board[t_x3][t_y3])
        i3 += 1
        t_x3, t_y3 = start3[0] - i3, start3[1] + i3
    cases.append(diagonal3)

    new_score = 0
    for case in cases:
        for pattern in PATTERNS:
            all_pattern = PATTERNS[pattern][player]
            for each in all_pattern:
                new_score += STANDARDS[pattern] * fit_pattern(case, each, player)

    board.board[point[0]][point[1]] = 0
    return new_score - ori_score
