from cmath import nan
import string
from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Any, Dict, List
import pandas as pd
import logging
import time
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STANDARD_ERC20_ABI  = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    },
]
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
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [
            {"internalType": "address", "name": "", "type": "address"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [
            {"internalType": "address", "name": "", "type": "address"}
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
    },
    {
        "inputs": [],
        "name": "token0",
        "outputs": [
            {"internalType": "address", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "token1",
        "outputs": [
            {"internalType": "address", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

WETH_TOKEN_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
USDC_TOKEN_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
UNISWAP_V2_FACTORY_CONTRACT_ADDRESS = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
UNISWAP_V3_FACTORY_CONTRACT_ADDRESS = '0x1F98431c8aD98523631AE4a59f267346ea31F984'

class BaseWeb3Client:
    """
    This is a base class for interacting with the Ethereum blockchain. It creates a connection 
    to the Ethereum blockchain using a specified provider URL.
    """
    def __init__(self, provider_url: str):
        try:
            self.w3 = Web3(Web3.HTTPProvider(provider_url))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception as e:
            logger.error(f"Failed to initiate Web3: {e}")
            raise

    def get_contract(self, address: str, abi: List[Dict[str, Any]]) -> Any:
        """
        Retrieves a contract object based on its address and ABI.
        """
        try:
            return self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
        except Exception as e:
            logger.error(f"Failed to get contract: {e}")
            raise

class ERC20Utilities(BaseWeb3Client):
    def __init__(self, provider_url: str):
        super().__init__(provider_url)

    def get_decimals(self, token_address: str) -> int:
        """
        Fetch the decimal precision of the ERC20 token at a given address.
        """
        try:
            token_contract = self.get_contract(token_address, STANDARD_ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            return decimals
        except Exception as e:
            # logger.error(f"Failed to get decimals for token at {token_address}: {e}")
            return False    

class UniswapUtilities(BaseWeb3Client):
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
      
if __name__ == '__main__':
    provider_url = 'https://mainnet.infura.io/v3/ba4743fed5204b35a6da5317fce4e103'
    transfers = pd.read_csv('./transfers.csv')

    # Create new columns for the added data
    transfers['price'] = 0.0
    transfers['pool_address'] = ''
    
    # Getting the minimum and maximum block and then the pandas dataframe of the WETH/USDC price for it. 
    min_block = transfers['block_number'].min()
    max_block = transfers['block_number'].max()
 
    # Initiating the objects for utilities
    uniswap_util = UniswapUtilities(provider_url)
    erc20_util = ERC20Utilities(provider_url)

    # Finding a dictionary of WETH/USDC prices - to be used in cross prices
    print('Retrieving WETH/USDC Price Dictionary For Time Period...')
    WETH_USDC_DIC = uniswap_util.get_price_dict(min_block, max_block, WETH_TOKEN_ADDRESS, USDC_TOKEN_ADDRESS)
    print(WETH_USDC_DIC)
    print('Retrieved WETH/USDC Price Dictionary For Time Period...') if WETH_USDC_DIC else (print('Error Retrieving WETH/USDC Price Dictionary'))
    
    # Group the DataFrame by token_address - then looping through each token-address specific group
    grouped = transfers.groupby('token_address')
    for token_address, group in grouped: #For each token
        token_address = Web3.to_checksum_address(token_address)
        
        # Checking if decimals exist for the token
        decimals = erc20_util.get_decimals(token_address)
        if decimals == False: continue

        # Retrieving the tokens V2 and V3 
        TOKEN_WETH_V2_PAIR_ADDRESS = uniswap_util.get_v2_pair_address(WETH_TOKEN_ADDRESS, token_address)
        TOKEN_WETH_V3_PAIR_ADDRESS = uniswap_util.get_v3_pool_address(WETH_TOKEN_ADDRESS, token_address)
        TOKEN_WETH_V2_PAIR = uniswap_util.get_v2_pair(TOKEN_WETH_V2_PAIR_ADDRESS)
        TOKEN_WETH_V3_POOL = uniswap_util.get_v3_pool(TOKEN_WETH_V3_PAIR_ADDRESS)
        pool_address = TOKEN_WETH_V3_PAIR_ADDRESS if TOKEN_WETH_V3_POOL else (TOKEN_WETH_V2_PAIR_ADDRESS if TOKEN_WETH_V2_PAIR else None)

        #For each Transaction of each token...
        for index, row in group.iterrows():
            block_number = row['block_number']
            price_token_weth = uniswap_util.get_uniswap_price(block_number, TOKEN_WETH_V2_PAIR, TOKEN_WETH_V3_POOL, decimals)
            weth_usdc_price = 0
            price = None
            if price_token_weth:
                weth_price = WETH_USDC_DIC[block_number]
                price = price_token_weth * weth_price
            print(price, price_token_weth, token_address, pool_address)
            transfers.at[index, 'price'] = price
            transfers.at[index, 'pool_address'] = pool_address if pool_address else None
    transfers.to_csv('new.csv')

