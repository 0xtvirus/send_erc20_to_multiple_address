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

### read abi
def get_abi_bytecode(file_location):
    with open (file_location) as cont_file:
        abi = json.load(cont_file)
    return abi['abi'], abi['bytecode']


def token_approve(owner:address, token:contract, spender:address, amount:int):
    construct_txn = token.functions.approve(spender, amount).buildTransaction({
        'from': owner,
        'nonce': w3.eth.getTransactionCount(owner),
        'gas': gas,
        "gasPrice": gasPrice,
        })
    tx_hash = w3.eth.send_transaction(construct_txn)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return token.functions.allowance(owner, spender).call()

def get_allowance(token:contract, owner:address, spender:address):
    return token.functions.allowance(owner, spender).call()


def make_swap(owner:address,token_in:contract, token_out:contract, router:contract, amountIn:int):
   
    #### grant allowance to router for token_in ######
    allowance = get_allowance(token_in, owner, router.address)
    if allowance < amountIn:
        token_approve(owner, token_in, router.address, amountIn)
    
    params = {
    "tokenIn": token_in.address,
    "tokenOut": token_out.address,
    "fee": 3000,
    "recipient": owner,
    "deadline": w3.eth.getBlock("latest").timestamp+10,
    "amountIn": amountIn,
    "amountOutMinimum": 0,
    "sqrtPriceLimitX96": 0
    }

    construct_txn = router.functions.exactInputSingle(params).buildTransaction({
    'from': owner,
    'nonce': w3.eth.getTransactionCount(owner),
    'gas': gas,
    "gasPrice": gasPrice,
    })
    tx_hash = w3.eth.send_transaction(construct_txn)
    return token_in.functions.balanceOf(owner).call(), token_out.functions.balanceOf(owner).call()

def get_weth(owner:address, token:contract, amountIn:int):
    construct_txn = token.functions.deposit().buildTransaction({
    'from': owner,
    'nonce': w3.eth.getTransactionCount(owner),
    'gas': gas, 
    "gasPrice": gasPrice,
    'value': amountIn
    })
    tx_hash = w3.eth.send_transaction(construct_txn)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return token.functions.balanceOf(owner).call()

def refund_weth(owner:address, token:contract, amountIn:int):
    construct_txn = token.functions.withdraw(amountIn).buildTransaction({
    'from': owner,
    'nonce': w3.eth.getTransactionCount(owner),
    'gas': gas,
    "gasPrice": gasPrice,
    })
    tx_hash = w3.eth.send_transaction(construct_txn)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return token.functions.balanceOf(owner).call()

def send_multi_address(sender:address, recievers:address, sending_contract:contract, token:contract, amount):
    tokenAddress = token.functions.address  
    construct_txn = sending_contract.functions.sendTokens(tokenAddress, int(amount), recievers).buildTransaction({
    'from': sender,
    'nonce': w3.eth.getTransactionCount(sender),
    'gas': gas, 
    "gasPrice": gasPrice,
    })
    tx_hash = w3.eth.send_transaction(construct_txn)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    return token.functions.balanceOf(sending_contract.address).call()
    
    






if __name__ == "__main__": 
    ### get ganache accounts
    accounts = w3.eth.accounts

    #### token addresses
    DAI_a = w3.toChecksumAddress("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    WETH9_a = w3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    USDC_a = w3.toChecksumAddress("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

    ### uniswap v3 router address
    router= w3.toChecksumAddress("0xE592427A0AEce92De3Edee1F18E0157C05861564")


    ### Router contract
    abi, bytecode = get_abi_bytecode("../build/contracts/ISwapRouter.json")
    swap_router = w3.eth.contract(address=router, abi=abi)
    # print(list(swap_router.functions))

    ### get WETH9 contract
    abi, bytecode = get_abi_bytecode("../build/contracts/IWETH.json")
    weth = w3.eth.contract(address=WETH9_a, abi=abi)
    # print(list(weth.functions), weth.address)


    ### get DAI contract
    abi, bytecode = get_abi_bytecode("../build/contracts/IERC20Minimal.json")
    DAI = w3.eth.contract(address=DAI_a, abi=abi)
    # print(list(DAI.functions), DAI.address)

    ### get USDC contract
    abi, bytecode = get_abi_bytecode("../build/contracts/IERC20Minimal.json")
    USDC = w3.eth.contract(address=USDC_a, abi=abi)
    # print(list(USDC.functions), USDC.address)

    ######################################################################
    ######################################################################
    ### deploy contract
    ### get multiple_senc contract ABI and bytecode
    abi, bytecode = get_abi_bytecode("../build/contracts/sendTokenMultipleReciever_2.json")
    sending_contract = w3.eth.contract(bytecode=bytecode, abi=abi)
    with open("tx_reciept_2.json") as f:
        data = json.load(f)

    contract_address = data["contractAddress"]
    sending_contract = w3.eth.contract(address=contract_address, abi=abi)
    ######################################################################
    ######################################################################




    amountIn = Web3.toWei(10, 'ether')
    weth_amount = get_weth(accounts[0] ,weth, amountIn)
    print('%s WETH is recieved\n\n'%(weth_amount/1e18))

    print("WETH to DAI swap")
    in1, out1 = make_swap(accounts[0], weth, DAI, swap_router, amountIn)
    print("DAI balance is %s"%(out1/1e18))
    print('WETH Balance after WETH/DAI swap= %s\n\n'%(in1/1e18))


    recievers = ["0xD2BF819D02DAbAE63Ed7d6B7A7Bc07913183a8b2", 
                "0x7bCccb99567241bF5966c77f27139a4ECf5fF58f",
                "0x5c4e51e532f8448d8D3A08C9B9136Cd45d0534Df",
                "0x122E7740adb801CdD315e94ebEA0Db2eFf4de18c",
                "0xe532bb711D5c6a91668Dfa2Ff47E0DDb53D54068",
                "0xCD204d3722fbEE4dcF7D1EB3D7235Fe36B60e352",
                "0xEfbb61dD08f2B5C94a2e3cB27631Ed9ad89Acb0a",
                "0x1415D35b6095417225bbd65a6FB662a8e457d3b1"]

  
    
    ############# send DAI to contract ##########################
    amount = int(10e18)
    total_amount = amount*len(recievers)
    sender = accounts[0]
    construct_txn = DAI.functions.transfer(data["contractAddress"], int(total_amount)).buildTransaction({
    'from': sender,
    'nonce': w3.eth.getTransactionCount(sender),
    'gas': gas, 
    "gasPrice": gasPrice,
    })
    tx_hash = w3.eth.send_transaction(construct_txn)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    balance_contract = DAI.functions.balanceOf(data["contractAddress"]).call()
    print("balance of token at contract= %s\n\n"%(balance_contract/1e18))
    
  
  
    balance_contract = send_multi_address(accounts[0], recievers, sending_contract, DAI, amount)
    print("balance of token at contract= %s"%(balance_contract/1e18))

    for reciver in recievers:
        print(DAI.functions.balanceOf(reciver).call()/1e18)




    amount_in_2 = int(DAI.functions.balanceOf(accounts[0]).call())
    in2, out2 =make_swap(accounts[0], DAI, weth, swap_router, amount_in_2)
    print("\nReverse **************")
    print("DAI balance is %s"%(in2/1e18))
    print('WETH Balance after DAI/WETH swap= %s'%(out2/1e18))

    ## weth refund
    print(refund_weth(accounts[0], weth, out2), w3.eth.getBalance(accounts[0])/1e18)














