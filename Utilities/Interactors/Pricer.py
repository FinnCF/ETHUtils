import UniswapV2, UniswapV3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pricer:
    def __init__(self, provider_url: str):
        """Initializes Uniswap V2 and V3 utilities.

        Args:
            provider_url (str): The URL of the Ethereum provider.
        """
        self.uniswap_v2 = UniswapV2.UniswapV2Utilities(provider_url)
        self.uniswap_v3 = UniswapV3.UniswapV3Utilities(provider_url)

    def get_fallbacked_price(self, v2_pair, v3_pool, v2_order_correct: bool, v3_order_correct: bool, decimal_adj: int):
        """Fetches the price of a token in the fallback order of UniswapV3 -> UniswapV2.

        If the price cannot be fetched from Uniswap V3, it attempts to fetch from Uniswap V2.
        If the price cannot be fetched from either, it returns None and logs an error message.

        Args:
            v2_pair: The pair address on Uniswap V2.
            v3_pool: The pool address on Uniswap V3.
            v2_order_correct (bool): Whether the pair order on Uniswap V2 is correct.
            v3_order_correct (bool): Whether the pool order on Uniswap V3 is correct.
            decimal_adj (int): The number of decimals to adjust the price.

        Returns:
            The price of the token or None if it cannot be fetched.
        """
        try:
            if v3_pool is not None:
                return self.uniswap_v3.get_uniswap_v3_price(v3_pool, v3_order_correct, decimal_adj)
        except Exception as e:
            logger.error(f"Failed to get price from Uniswap V3 due to: {e}. Falling back to Uniswap V2.")

        try:
            if v2_pair is not None:
                return self.uniswap_v2.get_uniswap_v2_price(v2_pair, v2_order_correct, decimal_adj)
        except Exception as e:
            logger.error(f"Failed to get price from Uniswap V2 due to: {e}. No other fallbacks available.")

        logger.error("Failed to get price from both Uniswap V3 and V2.")
        return None