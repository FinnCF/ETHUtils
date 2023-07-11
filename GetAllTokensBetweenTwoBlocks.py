from web3 import Web3, exceptions
import pandas as pd
import concurrent.futures

"""
REFINED_ERC20_ABI contains the necessary details of a standard ERC20 token contract's interface - reduced for our application.
"""
REFINED_ERC20_ABI = [
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
]

"""
is_erc20_contract checks if a given Ethereum contract adheres to the ERC20 token standard.
It does this by attempting to call two methods that should exist on an ERC20 contract and catching any exceptions
that may occur in case the contract is not ERC20 compliant.
"""
def is_erc20_contract(address, provider):
    w3 = Web3(Web3.HTTPProvider(provider))
    contract = w3.eth.contract(address=address, abi=REFINED_ERC20_ABI)
    try:
        contract.functions.balanceOf(address).call()
        contract.functions.transfer(address, 0).call()
    except (exceptions.BadFunctionCallOutput, exceptions.ContractLogicError):
        return False
    return True

"""
ERC20Checker is a class that encapsulates the logic to scan a given block range for Ethereum transactions
that resulted in the creation of an ERC20 token contract.
"""
class ERC20Checker:
    def __init__(self, provider, start_block, end_block):
        self.w3 = Web3(Web3.HTTPProvider(provider))
        self.start_block = start_block
        self.end_block = end_block

    """
    process_block scans the transactions in a given block for ERC20 contract creations.
    """
    def process_block(self, block_number):
        erc20_contracts = []
        block = self.w3.eth.get_block(block_number, full_transactions=True)
        for transaction in block['transactions']:
            if transaction['to']:
                continue  # skips non-contract creation transactions
            receipt = self.w3.eth.get_transaction_receipt(transaction['hash'])
            contract_address = receipt['contractAddress']
            if contract_address and is_erc20_contract(contract_address, self.w3.provider.endpoint_uri):
                erc20_contracts.append({'creationBlock': block_number, 'tokenAddress': contract_address})
                print(f"ERC20 Contract found at address: {contract_address} at block: {block_number}")

        return erc20_contracts

    """
    find_erc20_contracts scans the Ethereum blockchain for blocks within a specified range.
    It utilizes multithreading to process blocks in parallel.
    """
    def find_erc20_contracts(self):
        erc20_contracts = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.process_block, range(self.start_block, self.end_block + 1))
            for result in results:
                erc20_contracts.extend(result)

        return erc20_contracts

"""
The main entry point of the script. It instantiates an ERC20Checker and begins the scanning process.
At the end, all found ERC20 contracts are saved in a CSV file using the pandas library.
"""
if __name__ == '__main__':
    infura_mainnet_url = 'https://mainnet.infura.io/v3/19cb6798778843d28505de7f94aa7c60'
    checker = ERC20Checker(provider=infura_mainnet_url, start_block=17669140, end_block=17669940)
    try:
        contracts = checker.find_erc20_contracts()
        df = pd.DataFrame(contracts)
        df.to_csv('erc20_contracts.csv', index=False)
    except Exception as error:
        print(f"\nAn error occurred in main: {error}")
