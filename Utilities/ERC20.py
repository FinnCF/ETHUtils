
import BaseWeb3Client
from typing import List, Dict, Any

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

import BaseWeb3Client
from typing import List, Dict, Any

# STANDARD_ERC20_ABI remains the same.

class ERC20(BaseWeb3Client):
    """
    This class is used for interacting and producing ERC20 tokens.
    """
    def __init__(self, provider_url: str):
        super().__init__(provider_url)

    def get_decoded_logs(self, from_block: int, to_block: int, contractAddress: str, event_name: str) -> List[Dict[str, Any]]:
        """Fetch and decode logs of a contract within a block range."""
        try:
            contract = self.initiate_erc20_contract(contractAddress)
            event_filter = contract.events.__dict__[event_name].create_filter(fromBlock=from_block, toBlock=to_block)
            events = event_filter.get_all_entries()

            if not events:
                raise ValueError("No events emitted in this block range")

            return [
                {
                    'address':  contractAddress,
                    'from': event.args['from'],
                    'to': event.args['to'],
                    'quantity': event.args['value'],
                    'blockNumber': event.blockNumber,
                    'transactionHash': event.transactionHash.hex()
                } for event in events]
        except Exception as e:
            print(f"An error occurred while getting decoded logs: {str(e)}")
            return []

    def initiate_erc20_contract(self, contract_address: str):
        """Initiates an ERC20 token contract."""
        try:
            return self.w3.eth.contract(address=contract_address, abi=STANDARD_ERC20_ABI)
        except Exception as e:
            print(f"An error occurred while initiating the ERC20 contract: {str(e)}")
            return None

    def get_balance(self, contract_address: str, owner_address: str) -> int:
        """Get the balance of a specific address."""
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.balanceOf(owner_address).call()
        except Exception as e:
            print(f"An error occurred while getting the balance: {str(e)}")
            return 0

    def get_total_supply(self, contract_address: str) -> int:
        """Get the total supply for the token."""
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.totalSupply().call()
        except Exception as e:
            print(f"An error occurred while getting the total supply: {str(e)}")
            return 0

    def get_symbol(self, contract_address: str) -> str:
        """Get the symbol of the token."""
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.symbol().call()
        except Exception as e:
            print(f"An error occurred while getting the symbol: {str(e)}")
            return ''

    def get_decimals(self, contract_address: str) -> int:
        """Get the decimals of the token."""
        try:
            contract = self.initiate_erc20_contract(contract_address)
            return contract.functions.decimals().call()
        except Exception as e:
            print(f"An error occurred while getting the decimals: {str(e)}")
            return 0