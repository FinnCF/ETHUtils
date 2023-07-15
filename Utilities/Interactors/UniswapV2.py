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

class UniswapV2Interactor(ERC20):
    def __init__(self, provider_url: str):
        """Initializes the UniswapV2Utilities class.

        Inherits from the ERC20 class and sets up the Uniswap V2 Factory contract.
        
        Args:
            provider_url (str): The URL of the Ethereum provider.
        """
        super().__init__(provider_url)
        self.v2_factory_contract = self.get_contract(UNISWAP_V2_FACTORY_CONTRACT_ADDRESS, UNISWAP_V2_FACTORY_ABI)

    def get_uniswap_v2_pair_address(self, tokenA: str, tokenB: str) -> str:
        """Fetches the address of the Uniswap V2 Pair for the given tokens.

        Args:
            tokenA (str): The address of token A.
            tokenB (str): The address of token B.

        Returns:
            The address of the Uniswap V2 Pair or None if an error occurred.
        """
        try:
            v2_pair_address = self.v2_factory_contract.functions.getPair(tokenA, tokenB).call()
            if v2_pair_address == '0x0000000000000000000000000000000000000000':
                return None
            else:
                return v2_pair_address
        except Exception as e:
            logger.error(f"Failed to get Pair address: {e}")
            return None

    def get_uniswap_v2_pair(self, v2_pair_address) -> str:
        """Gets the Uniswap V2 Pair contract based on the pair address.

        Args:
            v2_pair_address (str): The address of the Uniswap V2 Pair.

        Returns:
            The Uniswap V2 Pair contract or None if an error occurred.
        """
        try:
            v2_pair = self.get_contract(v2_pair_address, UNISWAP_V2_PAIR_ABI)
            return v2_pair
        except Exception as e:
            logger.error(f"Failed to get Pair: {e}")
            return None

    def v2_pair_token_order_correct(self, v2_pair, tokenA_address: str, tokenB_address: str) -> bool:
        """Checks the token order in the Uniswap V2 Pair contract.

        Args:
            v2_pair: The Uniswap V2 Pair contract.
            tokenA_address (str): The address of token A.
            tokenB_address (str): The address of token B.

        Returns:
            True if the order is correct, False if the order is incorrect, or None if an error occurred.
        """
        try:
            token0_address = v2_pair.functions.token0().call()
            token1_address = v2_pair.functions.token1().call()
            if tokenA_address == token0_address and tokenB_address == token1_address:
                return True
            elif tokenA_address == token1_address and tokenB_address == token0_address:
                return False
        except Exception as e:
            logger.error(f"Failed to get token order: {e}")
            return None

    def get_uniswap_v2_price(self, block_number: int, v2_pair, order_correct: bool, decimal_adj: int):
        """Fetches the price of the token pair at the given block number.

        Only calls get reserves to ensure no more than one call is made. 

        Args:
            block_number (int): The block number.
            v2_pair: The Uniswap V2 Pair contract.
            order_correct (bool): Whether the order of tokens in the pair contract is correct.
            decimal_adj (int): The number of decimals to adjust the price.

        Returns:
            The price of the token pair or None if an error occurred.
        """
        try:
            reserve0, reserve1, _ = v2_pair.functions.getReserves().call(block_identifier=block_number)
            if reserve1 != 0:  # Avoid ZeroDivisionError
                if order_correct:
                    return (reserve0 / reserve1) * 10**decimal_adj
                elif order_correct == False:
                    return (reserve1 / reserve0) * 10**decimal_adj
        except ZeroDivisionError as e:
            logger.error(f"Division by zero encountered while getting price: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get price: {e}")
            return None