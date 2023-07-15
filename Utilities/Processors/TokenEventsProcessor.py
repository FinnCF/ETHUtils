from typing import List
from Utilities.Structures import Token
import eth_abi.exceptions
import web3.exceptions
import os
import pandas as pd
from Utilities.Interactors.ERC20 import ERC20Interactor
import logging
logging.basicConfig(level=logging.INFO)
from tqdm import tqdm 

class TokenEventsProcessor(ERC20Interactor):
    def __init__(self, provider_url, token: Token):
        self.token = token
        super().__init__(provider_url)
        self.logger = logging.getLogger(__name__)
        self.file_exists = os.path.exists('transfers.csv')

    def _reduce_block_chunk_size(self, token_address, block_chunk_size, min_block_chunk_size):
        block_chunk_size = max(round(block_chunk_size / 2), min_block_chunk_size)
        return block_chunk_size
    
    def _increase_block_chunk_size(self, block_chunk_size):
        return block_chunk_size * 2

    def find_all_transfers(self):
        """ Finds all transfers for a Token
        """
        # Token address we are using to find the transfers
        token_address = self.token.address

        # Set the initial and minimum block chunk sizes
        initial_block_chunk_size = 5000
        min_block_chunk_size = 1

        # Starts when the token is made
        from_block = self.token.block_number

        # Stops at the current block. 
        to_block = self.get_latest_block()

        # Finding the initial block chunk size
        block_chunk_size = initial_block_chunk_size

        # Initialising Loading Bar
        pbar = tqdm(total=to_block - from_block, desc='Processing blocks')

        while from_block < to_block: # While not all the blocks have been scanned

            try: # Get events...
                events = self.get_decoded_logs(from_block, min(from_block + block_chunk_size, to_block), token_address, 'Transfer')

                if len(events) > 0: 
                    events_df = pd.DataFrame(events)
                    events_df.to_csv('transfers.csv', mode='a', header=not self.file_exists, index=False)
                    self.file_exists = True
                else:
                    block_chunk_size = self._increase_block_chunk_size(block_chunk_size)

                processed_blocks = min(from_block + block_chunk_size, to_block) - from_block
                pbar.update(processed_blocks)

                from_block += block_chunk_size + 1


            except (eth_abi.exceptions.InsufficientDataBytes, web3.exceptions.LogTopicError, ValueError) as e:
                self.logger.exception(f"Error processing blocks {from_block} to {from_block + block_chunk_size}")
                block_chunk_size = self._reduce_block_chunk_size(token_address, block_chunk_size, min_block_chunk_size)

        pbar.close()

        # Return the token address to keep track of processed tokens
        return token_address