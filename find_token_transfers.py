"""
This script processes token events for a list of tokens in parallel using concurrent execution.
It reads token information from a CSV file, creates Token objects for each token, and processes
the transfer events for each token using the TokenEventsProcessor class.

The TokenEventsProcessor utilizes the Web3 library to interact with the Ethereum blockchain and
retrieve transfer events for a specific token. It saves the transfer events to a CSV file.

Concurrent execution is achieved using the ConcurrentExecutor class, which utilizes ThreadPoolExecutor
and ProcessPoolExecutor to execute the token event processing function concurrently for each token.

Author: Finn Casey Fierro
"""

import pandas as pd
from Utilities.Processors.TokenEventsProcessor import TokenEventsProcessor
from Utilities.Structures.Token import Token
from Utilities.Clients.BaseWeb3Client import BaseWeb3Client
from Utilities.Interactors.ERC20 import ERC20Interactor
from Utilities.Clients.Etherscan import EtherscanClient


if __name__ == '__main__':

    provider_url = 'https://mainnet.infura.io/v3/ba4743fed5204b35a6da5317fce4e103'
    etherscan_api_token = '2ZXU2USHPCRS638RE91II9C52IMD8NDY13'
    erc20Interactor = ERC20Interactor(provider_url)
    etherscanClient = EtherscanClient(etherscan_api_token)

    # token Address In Question
    contract_address = erc20Interactor.to_address('0xf3115b544C287380d34a19280DCFd029eeaDA9c8')
    contract_creation_hash = etherscanClient.get_contract_creation_transaction_hash(contract_address)
    timestamp = erc20Interactor.get_timestamp(contract_creation_hash)
    block_number = erc20Interactor.get_block_number(contract_creation_hash)


    # Create a new Token object for each row in the DataFrame.
    token = Token(
        address= contract_address,
        symbol = erc20Interactor.get_symbol(contract_address),
        name= erc20Interactor.get_name(contract_address),
        decimals = erc20Interactor.get_decimals(contract_address),
        total_supply = erc20Interactor.get_total_supply(contract_address),
        block_timestamp= timestamp,
        block_number= block_number,
        block_hash= contract_creation_hash
    )

    print(token.address, token.symbol, token.name, token.decimals, token.total_supply, token.block_timestamp, token.block_number, token.block_hash)

    # Processing the transfer events for each token.
    token_processor = TokenEventsProcessor(provider_url, token)
    token_processor.find_all_transfers()

    
    
