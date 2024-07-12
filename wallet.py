class wallet:
    def __init__(self):
        self.wallet = {
            "tspin_doubles": 0,
            "tspin_triples": 0,
            "lspins": 0,
            "jspins": 0,
            "sspins": 0,
            "zspins": 0,
            "ispins": 0,
            "tetrises": 0,
            "all_clears": 0
        }

    def add_currency(self, event):
        if event in self.wallet:
            self.wallet[event] += 1

    def get_currency(self, event):
        return self.wallet.get(event, 0)

    def reset(self):
        for key in self.wallet:
            self.wallet[key] = 0