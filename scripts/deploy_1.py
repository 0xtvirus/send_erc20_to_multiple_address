from web3 import Web3, HTTPProvider
import json
from dotenv import load_dotenv



#Connect to figmen HTTP End Point
url="HTTP://127.0.0.1:7545" 
w3 = Web3(HTTPProvider(url))
if w3.isConnected():
    print("connected")

### not necessary
address = str()
contract = str() # actually not string, it is in own class


gas = 30000000
gasPrice = w3.toWei(25, 'gwei') #w3.eth.gas_price + w3.toWei(10, 'gwei') # this works for ganache ui and ganache cli

### get ganache accounts
accounts = w3.eth.accounts

### read abi
def get_abi_bytecode(file_location):
    with open (file_location) as cont_file:
        abi = json.load(cont_file)
    return abi['abi'], abi['bytecode']

######################################################################
######################################################################
### deploy contract
### get multiple_senc contract ABI and bytecode
abi, bytecode = get_abi_bytecode("../build/contracts/sendTokenMultipleReciever_1.json")
sending_contract = w3.eth.contract(bytecode=bytecode, abi=abi)
# print(list(contract.functions))
######################################################################
construct_txn = sending_contract.constructor().buildTransaction({
    'from': accounts[0],
    'nonce': w3.eth.getTransactionCount(accounts[0]),
    'gasPrice': gasPrice, 
    'gas': gas,
    })
######################################################################
tx_hash = w3.eth.send_transaction(construct_txn)
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)



# # Encode the transaction receipt as a JSON object
tx_receipt_json = Web3.toJSON(tx_receipt)

# # Write the JSON string to a file
with open("tx_reciept_1.json", "w") as f:
    f.write(tx_receipt_json)

# # Read the JSON file to test
with open("tx_reciept_1.json") as f:
    data = json.load(f)
print(data.keys())
######################################################################
######################################################################