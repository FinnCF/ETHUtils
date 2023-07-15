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
from Utilities.Concurrency.ConcurrentExecutor import ConcurrentExecutor

provider_url = 'https://mainnet.infura.io/v3/ba4743fed5204b35a6da5317fce4e103'
baseWeb3Client = BaseWeb3Client(provider_url)

def process_token_events(index_row_tuple):
    index, row = index_row_tuple

    # Create a new Token object for each row in the DataFrame.
    token = Token(
        address=baseWeb3Client.to_address(row['address']),
        symbol=row['symbol'],
        name=row['name'],
        decimals=row['decimals'],
        total_supply=row['total_supply'],
        block_timestamp=row['block_timestamp'],
        block_number=row['block_number'],
        block_hash=row['block_hash']
    )

    # Processing the transfer events for each token.
    token_processor = TokenEventsProcessor(provider_url, token)
    token_processor.find_all_transfers()

if __name__ == '__main__':
    # List of tokens
    tokens = pd.read_csv('Data/tokens_14_07_2023_18_36.csv')

    # Convert the iterator returned by iterrows() to a list
    index_row_tuples = list(tokens.iterrows())

    # Processing concurrently all token rows
    ConcurrentExecutor().execute_concurrently(index_row_tuples, process_token_events)