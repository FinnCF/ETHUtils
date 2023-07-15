from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Any, Dict, List
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseWeb3Client:
    """
    This is a base class for interacting with Ethereum blockchain. It creates a connection 
    to the Ethereum blockchain using a specified provider URL.
    """
    def __init__(self, provider_url: str):
        try:
            self.w3 = Web3(Web3.HTTPProvider(provider_url))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception as e:
            logger.exception(f"Failed to initiate Web3: {e}")
            raise e

    def get_latest_block(self):
        """
        Retrieves the latest ERC20 block.
        """
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.exception(f"Failed to get contract: {e}")
            raise e        

    def get_contract(self, address: str, abi: list[Dict[str, Any]]) -> Any:
        """
        Retrieves contract object based on its address and abi.
        """
        try:
            return self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
        except Exception as e:
            logger.exception(f"Failed to get contract: {e}")
            raise e

    def get_balance(self, address: str) -> int:
        """
        Retrieves the eth balance of a given address.
        """
        try:
            return self.w3.eth.get_balance(address)
        except Exception as e:
            logger.exception(f"Failed to get balance: {e}")
            raise e

    def send_transaction(self, transaction: Dict[str, Any]) -> str:
        """
        Sends a transaction to the Ethereum network.
        """
        try:
            tx_hash = self.w3.eth.send_transaction(transaction)
            return tx_hash.hex()
        except Exception as e:
            logger.exception(f"Failed to send transaction: {e}")
            raise e

    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """
        Retrieves a transaction detail given its hash.
        """
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            return tx
        except Exception as e:
            logger.exception(f"Failed to get transaction: {e}")
            raise e

    def get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """
        Retrieves a transaction receipt given its hash.
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return receipt
        except Exception as e:
            logger.exception(f"Failed to get transaction receipt: {e}")
            raise e

    def is_address(self, address: str) -> bool:
        """
        Check if a string is a valid Ethereum address.
        """
        try:
            return self.w3.isAddress(address)
        except Exception as e:
            logger.exception("Failed to check if the string is a valid Ethereum address.", exc_info=True)
            raise e

    def to_wei(self, ether: float) -> int:
        """
        Convert ether to wei.
        """
        try:
            return self.w3.toWei(ether, 'ether')
        except Exception as e:
            logger.exception("Failed to convert ether to wei.", exc_info=True)
            raise e

    def from_wei(self, wei: int) -> float:
        """
        Convert wei to ether.
        """
        try:
            return self.w3.fromWei(wei, 'ether')
        except Exception as e:
            logger.exception("Failed to convert wei to ether.", exc_info=True)
            raise e

    def wait_for_receipt(self, tx_hash: str, polls: int = 200, timeout: int = 120) -> Dict[str, Any]:
        """
        Wait for a transaction to be mined, and return the transaction receipt.
        """
        try:
            receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=timeout, poll_latency=polls)
            return receipt
        except Exception as e:
            logger.exception("Failed to get transaction receipt.", exc_info=True)
            raise e