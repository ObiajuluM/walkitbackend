from web3.contract import Contract
from web3 import Web3
from eth_account.datastructures import SignedTransaction


CREATOR_ADDRESS = "0xdF0725C2f40380A04FBF10695d0de531a00443e8"
CREATOR_KEY = "852d82afe4e7724ea8c9f19a6eac20d317b08bd1e802cd8d6c633f7aba1e50dc"


NETWORKS_LIST_ = [
    # "SOMNIA":
    {
        "url": "https://dream-rpc.somnia.network/",
        "contract": "0x90510f40aD84eA5B01a3aC7C54C1415a24EA19D6",
    },
    # "MONAD":
    {
        "url": "https://testnet-rpc.monad.xyz/",
        "contract": "0xE496edfc5384Ba76d457a75a53B9819Ee9a62e3C",
    },
    # "XRPL_EVM":
    {
        "url": "https://rpc.testnet.xrplevm.org/",
        "contract": "0xE496edfc5384Ba76d457a75a53B9819Ee9a62e3C",
    },
    # "IOTA_EVM":
    {
        "url": "https://json-rpc.evm.testnet.iotaledger.net/",
        "contract": "0xE496edfc5384Ba76d457a75a53B9819Ee9a62e3C",
    },
]


def on_chain(
    network_url: str,
    contract_address: str,
    user_id: str,
    step_count: int,
):
    """function that writes step data on chain"""
    # connect to network
    web3 = Web3(Web3.HTTPProvider(network_url))

    # load the contract info
    ABI = open("backend/contracts/steps.abi").read()
    BYTECODE = open("backend/contracts/steps.bin").read()

    # get contract from info
    walk_log_contract: Contract = web3.eth.contract(
        address=contract_address,
        abi=ABI,
        bytecode=BYTECODE,
    )

    # build walk logging transaction
    txn = walk_log_contract.functions.logWalk(user_id, step_count).build_transaction(
        {
            "from": CREATOR_ADDRESS,
            "nonce": web3.eth.get_transaction_count(CREATOR_ADDRESS),
            "chainId": web3.eth.chain_id,
            "gasPrice": web3.eth.gas_price,
        }
    )

    stxn: SignedTransaction = web3.eth.account.sign_transaction(
        txn, private_key=CREATOR_KEY
    )
    send_stxn = web3.eth.send_raw_transaction(stxn.raw_transaction)
    # convert transaction hexbyte to readable string
    transaction_hash = [s.hex() for s in [send_stxn]]
    print(transaction_hash[0])
    return "0x" + transaction_hash[0]
