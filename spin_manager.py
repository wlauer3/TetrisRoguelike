class SpinDetector:
    def detect_spin(piece):
        piece_type = piece.type
        print(f"Piece type: {piece_type}")
        print(f"Wall kick data: {piece.currentWallkick}")
        if piece_type == 'I':  # I piece
            return "I spin"
        elif piece_type == 'T':  # T piece
            return "T spin"
        elif piece_type == 'J':  # J piece
            return "J spin"
        elif piece_type == 'L':  # L piece
            return "L spin"
        elif piece_type == 'S':  # S piece
            return "S spin"
        elif piece_type == 'Z':  # Z piece
            return "Z spin"
        return "No Spin"

    