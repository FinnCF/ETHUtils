from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Any, Dict, List
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from web3.exceptions import TransactionNotFound

class BaseWeb3Client:
    """
    This is a base class for interacting with the Ethereum blockchain. 
    It creates a connection to the Ethereum blockchain using a specified provider URL.
    """
    def __init__(self, provider_url: str):
        """
        Initializes the BaseWeb3Client class.

        Args:
            provider_url (str): The URL of the Ethereum provider.
        """
        try:
            self.w3 = Web3(Web3.HTTPProvider(provider_url))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception as e:
            logger.exception(f"Failed to initiate Web3: {e}")
            raise e

    def get_latest_block(self):
        """
        Retrieves the latest Ethereum block.

        Returns:
            The latest Ethereum block number.
        """
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.exception(f"Failed to get latest block: {e}")
            raise e        

    def get_contract(self, address: str, abi: List[Dict[str, Any]]) -> Any:
        """
        Retrieves a contract object based on its address and ABI.

        Args:
            address (str): The address of the contract.
            abi (list[Dict[str, Any]]): The ABI (Application Binary Interface) of the contract.

        Returns:
            An instance of the contract.
        """
        try:
            return self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
        except Exception as e:
            logger.exception(f"Failed to get contract: {e}")
            raise e

    def get_balance(self, address: str) -> int:
        """
        Retrieves the ETH balance of a given address.

        Args:
            address (str): The address to check the balance of.

        Returns:
            The ETH balance of the address.
        """
        try:
            return self.w3.eth.get_balance(address)
        except Exception as e:
            logger.exception(f"Failed to get balance: {e}")
            raise e

    def send_transaction(self, transaction: Dict[str, Any]) -> str:
        """
        Sends a transaction to the Ethereum network.

        Args:
            transaction (Dict[str, Any]): The transaction details.

        Returns:
            The transaction hash as a hexadecimal string.
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

        Args:
            tx_hash (str): The hash of the transaction.

        Returns:
            The transaction details as a dictionary.
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

        Args:
            tx_hash (str): The hash of the transaction.

        Returns:
            The transaction receipt as a dictionary.
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return receipt
        except Exception as e:
            logger.exception(f"Failed to get transaction receipt: {e}")
            raise e
        
    def get_contract_creator_address(self, contract_address: str):
        """
        Retrieves the creator address of a contract.

        Args:
            contract_address (str): The address of the contract.

        Returns:
            The creator address.
        """
        current_block_number = self.get_latest_block()
        tx_found = False

        while current_block_number >= 0 and not tx_found:
            block = self.get_block(current_block_number)
            transactions = block['transactions']
            print('checking: ', current_block_number)

            for tx in transactions:
                # We know this is a Contract deployment
                if not tx['to']:
                    try:
                        receipt = self.w3.eth.get_transaction_receipt(tx['hash'])
                    except TransactionNotFound:
                        print('Transactions Not Found In: ', current_block_number)
                        continue

                    if 'contractAddress' in receipt and receipt['contractAddress'].lower() == contract_address.lower():
                        tx_found = True
                        print(f'Contract Creator Address: {tx["from"]}')
                        break
                    else:
                        print('Creation Transaction Not Found In: ', current_block_number)



            current_block_number -= 1

    def is_address(self, address: str) -> bool:
        """
        Checks if a string is a valid Ethereum address.

        Args:
            address (str): The string to check.

        Returns:
            True if the string is a valid Ethereum address, False otherwise.
        """
        try:
            return self.w3.isAddress(address)
        except Exception as e:
            logger.exception("Failed to check if the string is a valid Ethereum address.", exc_info=True)
            raise e
        
    def to_address(self, address: str) -> str:
        """
        Checks if a string is a valid Ethereum address and returns its checksummed format.

        Args:
            address (str): The string to check.

        Returns:
            The checksummed Ethereum address.

        Raises:
            Exception: If the string is not a valid Ethereum address.
        """
        try:
            return self.w3.to_checksum_address(address)
        except Exception as e:
            logger.exception("Failed to translate to a valid Ethereum address.", exc_info=True)
            raise e

    def to_wei(self, ether: float) -> int:
        """
        Converts ETH to wei.

        Args:
            ether (float): The amount of ETH to convert.

        Returns:
            The equivalent amount in wei as an integer.
        """
        try:
            return self.w3.toWei(ether, 'ether')
        except Exception as e:
            logger.exception("Failed to convert ETH to wei.", exc_info=True)
            raise e

    def from_wei(self, wei: int) -> float:
        """
        Converts wei to ETH.

        Args:
            wei (int): The amount of wei to convert.

        Returns:
            The equivalent amount in ETH as a float.
        """
        try:
            return self.w3.fromWei(wei, 'ether')
        except Exception as e:
            logger.exception("Failed to convert wei to ETH.", exc_info=True)
            raise e

    def wait_for_receipt(self, tx_hash: str, polls: int = 200, timeout: int = 120) -> Dict[str, Any]:
        """
        Waits for a transaction to be mined and returns the transaction receipt.

        Args:
            tx_hash (str): The hash of the transaction.
            polls (int): The number of times to poll for the receipt.
            timeout (int): The maximum time to wait for the receipt in seconds.

        Returns:
            The transaction receipt as a dictionary.
        """
        try:
            receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=timeout, poll_latency=polls)
            return receipt
        except Exception as e:
            logger.exception("Failed to get transaction receipt.", exc_info=True)
            raise e
        
    def get_block(self, block_number: int, full_transactions=True) -> Dict[str, Any]:
        """
        Retrieves a block by its block number.

        Args:
            block_number (int): The number of the block.

        Returns:
            The block information as a dictionary.
        """
        try:
            block = self.w3.eth.get_block(block_number, full_transactions)
            return block
        except Exception as e:
            logger.exception(f"Failed to get block: {e}")
            raise e