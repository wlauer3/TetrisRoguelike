class LevelManager:
    def __init__(self):
        self.level = 1

    def update_level(self, lines_cleared):
        self.level = lines_cleared // 10 + 1

    def get_level(self):
        return self.level
