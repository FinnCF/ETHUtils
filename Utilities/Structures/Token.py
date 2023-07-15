
class Token:
    def __init__(self, address: str, symbol: str, name: str, decimals: int, total_supply: int, block_timestamp: int, block_number: int, block_hash: str):
        self.address = address
        self.symbol = symbol
        self.name = name
        self.decimals = decimals
        self.total_supply = total_supply
        self.block_timestamp = block_timestamp
        self.block_number = block_number
        self.block_hash = block_hash