
from Utilities.Clients.BaseWeb3Client import BaseWeb3Client
from typing import List, Dict, Any
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from web3.exceptions import TransactionNotFound

STANDARD_ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "payable": True,
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]

class ERC20Interactor(BaseWeb3Client):
    """
    This class is used for interacting and producing ERC20 tokens.
    """
    def __init__(self, provider_url: str):
        """Initializes the ERC20 class.

        Inherits from the BaseWeb3Client class and sets up the Ethereum provider.

        Args:
            provider_url (str): The URL of the Ethereum provider.
        """
        super().__init__(provider_url)

    def get_decoded_logs(self, from_block: int, to_block: int, contractAddress: str, event_name: str) -> List[Dict[str, Any]]:
        """Fetches and decodes logs of a contract within a block range.

        Args:
            from_block (int): The starting block in the range.
            to_block (int): The ending block in the range.
            contractAddress (str): The address of the contract.
            event_name (str): The name of the event to filter.

        Returns:
            A list of decoded event logs.
        """
        try:
            contract = self.initiate_erc20_contract(contractAddress)
            event_filter = contract.events.__dict__[event_name].create_filter(fromBlock=from_block, toBlock=to_block)
            events = event_filter.get_all_entries()

            if not events:
                return []

            return [{'address':  contractAddress, 'from': event.args['from'], 'to': event.args['to'], 'quantity': event.args['value'], 'blockNumber': event.blockNumber, 'transactionHash': event.transactionHash.hex()} for event in events]
        except Exception as e:
            print(f"An error occurred while getting decoded logs: {str(e)}")
            raise ValueError

    def initiate_erc20_contract(self, contract_address: str):
        """Initiates an ERC20 token contract.

        Args:
            contract_address (str): The address of the contract.

        Returns:
            An initiated ERC20 token contract.
        """
        try:
            return self.w3.eth.contract(address=contract_address, abi=STANDARD_ERC20_ABI)
        except Exception as e:
            print(f"An error occurred while initiating the ERC20 contract: {str(e)}")
            return None

    def get_balance(self, contract_address: str, address: str) -> int:
        """Fetches the balance of a specific address.

        Args:
            contract_address (str): The address of the contract.
            address (str): The address whose balance is being fetched.

        Returns:
            The balance of the specified address.
        """
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.balanceOf(address).call()
        except Exception as e:
            print(f"An error occurred while getting the balance: {str(e)}")
            return None

    def get_total_supply(self, contract_address: str) -> int:
        """Fetches the total supply for the token.

        Args:
            contract_address (str): The address of the contract.

        Returns:
            The total supply of the token.
        """
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.totalSupply().call()
        except Exception as e:
            print(f"An error occurred while getting the total supply: {str(e)}")
            return None
        
    def get_symbol(self, contract_address: str) -> str:
        """Fetches the symbol of the token.

        Args:
            contract_address (str): The address of the contract.

        Returns:
            The symbol of the token.
        """
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.symbol().call()
        except Exception as e:
            print(f"An error occurred while getting the symbol: {str(e)}")
            return None
        
    def get_name(self, contract_address: str) -> str:
        """Fetches the name of the token.

        Args:
            contract_address (str): The address of the contract.

        Returns:
            The name of the token.
        """
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.name().call()
        except Exception as e:
            print(f"An error occurred while getting the symbol: {str(e)}")
            return None
        
    def get_decimals(self, contract_address: str) -> int:
        """Fetches the decimals of the token.

        Args:
            contract_address (str): The address of the contract.

        Returns:
            The decimals of the token.
        """
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.decimals().call()
        except Exception as e:
            print(f"An error occurred while getting the decimals: {str(e)}")
            return None
        
    def get_timestamp(self, creation_hash: str) -> int:
        """Fetches the timestamp of the token's creation.

        Args:
            creation_hash (str): The hash of the creation transaction.

        Returns:
            int: The timestamp of the token's creation.
        """
        try:
            tx_receipt = self.get_transaction_receipt(creation_hash)
            block = self.get_block(tx_receipt['blockNumber'])
            return block['timestamp']
        except Exception as e:
            print(f"An error occurred while getting the timestamp of token creation: {str(e)}")
        return None
        
    def get_block_number(self, creation_hash: str) -> int:
        """Fetches the block number of the tokens creation.

        Args:
            creation_hash (str): The hash of the creation transaction.

        Returns:
            The block number of the token.
        """
        try:
            tx_receipt = self.get_transaction_receipt(creation_hash)
            return tx_receipt['blockNumber']
        except Exception as e:
            print(f"An error occurred while getting the block number of token creation: {str(e)}")
            return None
        
    def calculate_decimal_adj(self, tokenA_address: str, tokenB_address: str) -> int:
        """Calculates the decimal adjustment between two tokens.

        Args:
            tokenA_address (str): The address of token A.
            tokenB_address (str): The address of token B.

        Returns:
            The decimal adjustment between the two tokens.
        """
        try:
            return self.get_decimals(tokenA_address) - self.get_decimals(tokenB_address)
        except Exception as e:
            logger.error(f"Failed to calculate decimal adjustment: {e}")
            return None