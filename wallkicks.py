# wallkicks.py

WALL_KICKS = {
    'JLSTZ': {
        (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (2, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (0, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]
    },
    'I': {
        (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
    },
    'O': {}
}

def get_wall_kicks(piece_type, from_state, to_state):
    if piece_type == 'O':
        return [(0, 0)]  # O pieces don't have wall kicks
    if piece_type in ['I', 'JLSTZ']:
        return WALL_KICKS[piece_type].get((from_state, to_state), [(0, 0)])
    return [(0, 0)]