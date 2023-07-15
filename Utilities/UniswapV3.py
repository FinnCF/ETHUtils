import BaseWeb3Client

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
UNISWAP_V3_FACTORY_ABI = [
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
        },
        {
            "name": "fee",
            "type": "uint24"
        }
    ],
    "name": "getPool",
    "outputs": [
        {
            "name": "",
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
UNISWAP_V3_POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {
                "internalType": "uint160",
                "name": "sqrtPriceX96",
                "type": "uint160"
            },
            {
                "internalType": "int24",
                "name": "tick",
                "type": "int24"
            },
            {
                "internalType": "uint16",
                "name": "observationIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "observationCardinality",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "observationCardinalityNext",
                "type": "uint16"
            },
            {
                "internalType": "uint8",
                "name": "feeProtocol",
                "type": "uint8"
            },
            {
                "internalType": "bool",
                "name": "unlocked",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

WETH_TOKEN_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
USDC_TOKEN_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
UNISWAP_V2_FACTORY_CONTRACT_ADDRESS = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f' 
UNISWAP_V3_FACTORY_CONTRACT_ADDRESS = '0x1F98431c8aD98523631AE4a59f267346ea31F984'

class UniswapV2Utilities(BaseWeb3Client):
    def __init__(self, provider_url: str):
        super().__init__(provider_url)
        self.v2_factory_contract = self.get_contract(UNISWAP_V2_FACTORY_CONTRACT_ADDRESS, UNISWAP_V2_FACTORY_ABI)
        self.v3_factory_contract = self.get_contract(UNISWAP_V3_FACTORY_CONTRACT_ADDRESS, UNISWAP_V3_FACTORY_ABI)

    def get_uniswap_v2_pair_and_v3_pool(self, tokenA: str, tokenB: str):
        v2_pair_address, v3_pool_address = None, None
        v2_pair, v3_pool = None, None
        try:
            v2_pair_address = self.v2_factory_contract.functions.getPair(tokenA, tokenB).call()
            v3_pool_address = self.v3_factory_contract.functions.getPool(tokenA, tokenB, 500).call()  # Assuming fee_tier=500 for V3
        except Exception as e:
            # logger.error(f"Failed to get Pair/Pool addresses: {e}")
            return None, None

        # Getting pair and pool contracts if addresses are valid
        if v2_pair_address and v2_pair_address != '0x0000000000000000000000000000000000000000':
            v2_pair = self.get_contract(v2_pair_address, UNISWAP_V2_PAIR_ABI)
        if v3_pool_address and v3_pool_address != '0x0000000000000000000000000000000000000000':
            v3_pool = self.get_contract(v3_pool_address, UNISWAP_V3_POOL_ABI)
        return v2_pair, v3_pool

    def calculate_v3_price(self, sqrt_price_x96, decimals):
        # Calculate price with adjusted decimals
        return (sqrt_price_x96 / 2**96)**2 * 10**decimals

    def calculate_v2_price(self, reserve_ratio, decimals):
        # Calculate price with adjusted decimals
        return reserve_ratio * 10**decimals
    
    def get_uniswap_price(self, block_number: int, tokenA: str, tokenB:str):
        v2_pair, v3_pool = self.get_uniswap_v2_pair_and_v3_pool(tokenA, tokenB)
        decimal_adj = erc20_util.get_decimals(tokenA) - erc20_util.get_decimals(tokenB)
        if v3_pool:  # If V3 pair exists
            sqrt_price_x96, _, _, _, _, _, _ = v3_pool.functions.slot0().call(block_identifier=block_number)
            token0_address = v3_pool.functions.token0().call() #Finding the slot0 address of the pool - to check if X/X is correctly defined
            token1_address = v3_pool.functions.token1().call() # Same for token1 
            if sqrt_price_x96 != 0:  # to avoid ZeroDivisionError
                # Check if the order of tokens is as expected
                if tokenA == token0_address and tokenB == token1_address:
                    return self.calculate_v3_price(sqrt_price_x96, decimal_adj)
                elif tokenA == token1_address and tokenB == token0_address:
                    return self.calculate_v3_price(1 / sqrt_price_x96, -decimal_adj)
        elif v2_pair:  # If V2 pool exists
            reserve0, reserve1, _ = v2_pair.functions.getReserves().call(block_identifier=block_number)
            token0_address = v2_pair.functions.token0().call()
            token1_address = v2_pair.functions.token1().call()
            if reserve1 != 0:  # to avoid ZeroDivisionError
                # Check if the order of tokens is as expected
                if tokenA == token0_address and tokenB == token1_address:
                    return self.calculate_v2_price(reserve0 / reserve1, decimal_adj)
                elif tokenA == token1_address and tokenB == token0_address:
                    return self.calculate_v2_price(reserve1 / reserve0, -decimal_adj)
        else:
            return None

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