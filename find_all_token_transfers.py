from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Any, Dict, List
import logging
import pandas as pd
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import eth_abi
import web3
import os
from eth_abi.exceptions import InsufficientDataBytes
import concurrent.futures
import multiprocessing

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

class EventFetcher(BaseWeb3Client):
    """Fetches and decodes 'Transfer' events for a specified token contract."""

    def get_decoded_logs(self, from_block: int, to_block: int, contractAddress: Any, event_name: str) -> List[Dict[str, Any]]:
        """Fetch and decode logs of a contract within a block range."""

        contract = self.get_contract(contractAddress, STANDARD_ERC20_ABI)
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



if __name__ == '__main__':
    # Read the CSV file with token addresses into a pandas DataFrame
    csv_file = './tokens_14_07_2023_18_36.csv'
    token_df = pd.read_csv(csv_file)

    provider_url = 'https://mainnet.infura.io/v3/ba4743fed5204b35a6da5317fce4e103'
    w3 = BaseWeb3Client(provider_url)
    eventFetcher = EventFetcher(provider_url)
    to_block = w3.get_latest_block()
    
    # Set the initial and minimum block chunk sizes
    initial_block_chunk_size = 150000
    min_block_chunk_size = 5000
    block_chunk_sizes = {}

    def process_token(row):
        token_address = row.address
        from_block = row.block_number
        block_chunk_size = block_chunk_sizes.get(token_address, initial_block_chunk_size)

        while from_block < to_block:
            try:
                events = eventFetcher.get_decoded_logs(from_block, min(from_block + block_chunk_size, to_block), token_address, 'Transfer')

                if events:
                    events_df = pd.DataFrame(events)

                    if os.path.exists(f'transfers.csv'):
                        events_df.to_csv(f'transfers.csv', mode='a', header=False, index=False)
                    else:
                        events_df.to_csv(f'transfers.csv', index=False)

                from_block += block_chunk_size + 1

            except eth_abi.exceptions.InsufficientDataBytes as e:
                if 'Only got 0 bytes' in str(e):
                    print(f"No logs for token {token_address} in blocks {from_block} to {from_block + block_chunk_size}")
                    from_block += block_chunk_size + 1
                else:
                    print(f"Unable to decode logs for token {token_address} in blocks {from_block} to {from_block + block_chunk_size}. Error: {e}")
                    block_chunk_size = max(block_chunk_size // 2, min_block_chunk_size)
                    block_chunk_sizes[token_address] = block_chunk_size
            except web3.exceptions.LogTopicError as e:
                print(f"LogTopicError for token {token_address} in blocks {from_block} to {from_block + block_chunk_size}. Error: {e}")
                block_chunk_size = max(block_chunk_size // 2, min_block_chunk_size)
                block_chunk_sizes[token_address] = block_chunk_size
            except ValueError as e:
                if 'No events emitted in this block range' in str(e):
                    from_block += block_chunk_size + 1 
                elif 'query returned more than 10000 results' in str(e):
                    block_chunk_size = max(block_chunk_size // 2, min_block_chunk_size)
                    block_chunk_sizes[token_address] = block_chunk_size
                else:
                    print(f"ValueError for token {token_address} in blocks {from_block} to {from_block + block_chunk_size}. Error: {str(e)}")
                    block_chunk_size = max(block_chunk_size // 2, min_block_chunk_size)
                    block_chunk_sizes[token_address] = block_chunk_size

        # Return the token address to keep track of processed tokens
        return token_address

    # Create a list of token rows
    token_rows = token_df.itertuples(index=False)

    with concurrent.futures.ThreadPoolExecutor() as thread_executor, concurrent.futures.ProcessPoolExecutor() as process_executor:
        # Process the token events in parallel using ThreadPoolExecutor and ProcessPoolExecutor
        thread_executor.map(process_token, token_rows)
        process_executor.map(process_token, token_rows)

    print("Finished processing tokens:")
