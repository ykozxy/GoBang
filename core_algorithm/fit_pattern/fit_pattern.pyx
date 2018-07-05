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
