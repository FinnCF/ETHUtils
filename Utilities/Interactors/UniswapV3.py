from Utilities.Clients import BaseWeb3Client
import ERC20
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import logging

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
UNISWAP_V3_FACTORY_CONTRACT_ADDRESS = '0x1F98431c8aD98523631AE4a59f267346ea31F984'

class UniswapV3Interactor(ERC20):
    def __init__(self, provider_url: str):
        """Initializes the UniswapV3Utilities class.

        Inherits from the ERC20 class and sets up the Uniswap V3 Factory contract.
        
        Args:
            provider_url (str): The URL of the Ethereum provider.
        """
        super().__init__(provider_url)
        self.v3_factory_contract = self.get_contract(UNISWAP_V3_FACTORY_CONTRACT_ADDRESS, UNISWAP_V3_FACTORY_ABI)

    def get_uniswap_v3_pool_address(self, tokenA: str, tokenB: str, fee: int) -> str:
        """Fetches the address of the Uniswap V3 Pool for the given tokens and fee tier.

        Args:
            tokenA (str): The address of token A.
            tokenB (str): The address of token B.
            fee (int): The fee tier.

        Returns:
            The address of the Uniswap V3 Pool or None if an error occurred.
        """
        try:
            v3_pool_address = self.v3_factory_contract.functions.getPool(tokenA, tokenB, fee).call()
            if v3_pool_address == '0x0000000000000000000000000000000000000000':
                return None
            else:
                return v3_pool_address
        except Exception as e:
            logger.error(f"Failed to get Pool address: {e}")
            return None

    def get_uniswap_v3_pool(self, v3_pool_address):
        """Gets the Uniswap V3 Pool contract based on the pool address.

        Args:
            v3_pool_address (str): The address of the Uniswap V3 Pool.

        Returns:
            The Uniswap V3 Pool contract or None if an error occurred.
        """
        try:
            v3_pool = self.get_contract(v3_pool_address, UNISWAP_V3_POOL_ABI)
            return v3_pool
        except Exception as e:
            logger.error(f"Failed to get Pool: {e}")
            return None

    def v3_pool_token_order_correct(self, v3_pair, tokenA_address: str, tokenB_address: str) -> bool:
        """Checks the token order in the Uniswap V3 Pair contract.

        Args:
            v3_pair: The Uniswap V3 Pair contract.
            tokenA_address (str): The address of token A.
            tokenB_address (str): The address of token B.

        Returns:
            True if the order is correct, False if the order is incorrect, or None if an error occurred.
        """
        try:
            token0_address = v3_pair.functions.token0().call()
            token1_address = v3_pair.functions.token1().call()
            if tokenA_address == token0_address and tokenB_address == token1_address:
                return True
            elif tokenA_address == token1_address and tokenB_address == token0_address:
                return False
        except Exception as e:
            logger.error(f"Failed to get token order: {e}")
            return None

    def get_uniswap_v3_price(self, v3_pool, order_correct: bool, decimal_adj: int):
        """Fetches the current price of the token pair in the Uniswap V3 Pool.

        Args:
            v3_pool: The Uniswap V3 Pool contract.
            order_correct (bool): Whether the order of tokens in the pool contract is correct.
            decimal_adj (int): The number of decimals to adjust the price.

        Returns:
            The price of the token pair or None if an error occurred.
        """
        try:
            slot0 = v3_pool.functions.slot0().call()
            sqrtPriceX96 = slot0[0]
            if order_correct:
                price = (sqrtPriceX96**2 / 2**96) * 10**decimal_adj
            else:
                price = 1 / ((sqrtPriceX96**2 / 2**96) * 10**decimal_adj)
            return price
        except Exception as e:
            logger.error(f"Failed to get price: {e}")
            return None