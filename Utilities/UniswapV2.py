from decimal import Decimal
import ERC20
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import logging

UNISWAP_V2_FACTORY_ABI = [
    {
        "constant": True,
        "inputs": [
            {
                "name": "tokenA",
                "type": "address"
            },
            {
                "name": "tokenB",
                "type": "address"
            }
        ],
        "name": "getPair",
        "outputs": [
            {
                "name": "pair",
                "type": "address"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]
UNISWAP_V2_PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]
UNISWAP_V2_FACTORY_CONTRACT_ADDRESS = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f' 

class UniswapV2Utilities(ERC20):
    def __init__(self, provider_url: str):
        super().__init__(provider_url)
        self.v2_factory_contract = self.get_contract(UNISWAP_V2_FACTORY_CONTRACT_ADDRESS, UNISWAP_V2_FACTORY_ABI)

    def get_uniswap_v2_pair_address(self, tokenA: str, tokenB: str) -> str:
        v2_pair_address = None
        try:
            v2_pair_address = self.v2_factory_contract.functions.getPair(tokenA, tokenB).call()
            if v2_pair_address != '0x0000000000000000000000000000000000000000':
                return None
            else:
                return v2_pair_address
        except Exception as e:
            logger.error(f"Failed to get Pair address: {e}")
            return None, None
    
    def get_uniswap_v2_pair(self, v2_pair_address) -> str:
        v2_pair = None
        try:
            v2_pair = self.get_contract(v2_pair_address, UNISWAP_V2_PAIR_ABI)
            return v2_pair
        except Exception as e:
            logger.error(f"Failed to get Pair: {e}")
            return None

    def calculate_decimal_adj(self, tokenA: str, tokenB: str, decimal_adj: int):
        # Calculate adjusted decimals between two tokens
        return self.get_decimals(tokenA) - self.get_decimals(tokenB)

    def calculate_v2_price(self, reserve_ratio: Decimal, decimal_adj: int):
        # Calculate price with adjusted decimals
        return reserve_ratio * 10**decimal_adj
    
    def get_uniswap_v2_price(self, block_number: int, v2_pair, tokenA_address: str, tokenB_address:str, decimal_adj: int):
        reserve0, reserve1, _ = v2_pair.functions.getReserves().call(block_identifier=block_number)
        token0_address = v2_pair.functions.token0().call()
        token1_address = v2_pair.functions.token1().call()
        if reserve1 != 0:  # to avoid ZeroDivisionError
            # Check if the order of tokens is as expected
            if tokenA_address == token0_address and tokenB_address == token1_address:
                return (reserve0 / reserve1) * 10**decimal_adj
            elif tokenA_address == token1_address and tokenB_address == token0_address:
                return (reserve1 / reserve0) * 10**decimal_adj

    def get_price_dict(self, start_block: int, finish_block: int, tokenA: str, tokenB: str) -> Dict[int, float]:
        """
        Fetch the price of WETH/USDC as a dictionary between two blocks inclusive.
        The dictionary keys are block numbers, and the values are the prices at those blocks.
        """
        prices = {}
        for block_number in range(start_block, finish_block + 1):
            price = self.get_uniswap_price(block_number, tokenA, tokenB)
            print(price)
            prices[block_number] = price
        return prices