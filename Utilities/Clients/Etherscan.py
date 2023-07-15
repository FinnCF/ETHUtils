import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EtherscanClient:
    """
    This class is for interacting with the Etherscan API.
    It provides various methods to fetch data from the API.
    """
    def __init__(self, api_key: str):
        """
        Initializes the EtherscanClient class.

        Args:
            api_key (str): The API key for Etherscan.
        """
        self.api_key = api_key
        self.base_url = "https://api.etherscan.io/api"

    def get_request(self, payload: dict) -> dict:
        """
        Sends a GET request to the Etherscan API.

        Args:
            payload (dict): The parameters for the API request.

        Returns:
            The response from the API request as a dictionary.
        """
        try:
            response = requests.get(self.base_url, params=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception(f"Failed to send GET request to Etherscan API: {e}")
            raise e

    def get_contract_abi(self, contract_address: str) -> dict:
        """
        Retrieves the ABI (Application Binary Interface) of a contract.

        Args:
            contract_address (str): The address of the contract.

        Returns:
            The ABI of the contract as a dictionary.
        """
        payload = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
            "apikey": self.api_key
        }
        return self.get_request(payload)

    def get_latest_block(self) -> int:
        """
        Retrieves the latest Ethereum block number.

        Returns:
            The latest Ethereum block number.
        """
        payload = {
            "module": "proxy",
            "action": "eth_blockNumber",
            "apikey": self.api_key
        }
        return int(self.get_request(payload)['result'], 16)
    
    def get_contract_creation_transaction_hash(self, contract_address: str) -> str:
        """
        Retrieves the transaction hash of a contract creation. 
        After this is used, you can use Infura to get the block data (numbear etc)

        Args:
            contract_address (str): The address of the contract.

        Returns:
            The transaction hash as a string.
        """
        try:
            # Get list of normal transactions by address
            payload = {
                "module": "account",
                "action": "txlist",
                "address": contract_address,
                "sort": "asc",
                "apikey": self.api_key
            }
            tx_list = self.get_request(payload)

            # Check each transaction to find contract creation
            for tx in tx_list['result']:
                if tx['to'] == "":
                    return tx['hash']
                    
            logger.info("No contract creation transaction found for this address.")
            return None

        except Exception as e:
            logger.exception(f"Failed to get contract creation transaction hash: {e}")
            raise e