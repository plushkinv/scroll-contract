from statistics import mean
import time
from web3 import Web3
import requests
import random
from datetime import datetime
import config
import fun
from fun import *


deploy_bytcode = '0x60806040526000805461ffff1916905534801561001b57600080fd5b5060fb8061002a6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c80630c55699c146037578063b49004e914605b575b600080fd5b60005460449061ffff1681565b60405161ffff909116815260200160405180910390f35b60616063565b005b60008054600191908190607a90849061ffff166096565b92506101000a81548161ffff021916908361ffff160217905550565b61ffff81811683821601908082111560be57634e487b7160e01b600052601160045260246000fd5b509291505056fea2646970667358221220666c87ec501268817295a4ca1fc6e3859faf241f38dd688f145135970920009264736f6c63430008120033'

deploy_abi = []


current_datetime = datetime.now()
print(f"\n\n {current_datetime}")
print(f'============================================= Плюшкин Блог =============================================')
print(f'subscribe to : https://t.me/plushkin_blog \n============================================================================================================\n')

keys_list = []
with open("private_keys.txt", "r") as f:
    for row in f:
        private_key=row.strip()
        if private_key:
            keys_list.append(private_key)

random.shuffle(keys_list)
i=0
for private_key in keys_list:
    i+=1
    if config.proxy_use == 2:
        while True:
            try:
                requests.get(url=config.proxy_changeIPlink)
                fun.timeOut("teh")
                result = requests.get(url="https://yadreno.com/checkip/", proxies=config.proxies)
                print(f'Ваш новый IP-адрес: {result.text}')
                break
            except Exception as error:
                print(' !!! Не смог подключиться через Proxy, повторяем через 2 минуты... ! Чтобы остановить программу нажмите CTRL+C или закройте терминал')
                time.sleep(120)

    try:
        web3 = Web3(Web3.HTTPProvider(config.rpc_links['scroll'], request_kwargs=config.request_kwargs))
        account = web3.eth.account.from_key(private_key)
        wallet = account.address    
        log(f"I-{i}: Начинаю работу с {wallet}")
        balance = web3.eth.get_balance(wallet)
        balance_decimal = Web3.from_wei(balance, 'ether')        

        if balance_decimal < config.minimal_need_balance:
            log("Недостаточно эфира.  жду когда пополнишь. на следующем круге попробую снова")
            fun.save_wallet_to("no_money_wa", wallet)
            keys_list.append(private_key)            
            timeOut("teh")
            continue 

        # while True:
        #     gasPrice = web3.eth.gas_price
        #     gasPrice_Gwei = Web3.from_wei(gasPrice, 'Gwei')
        #     log(f"gasPrice_Gwei = {gasPrice_Gwei}")
        #     if config.max_gas_price > gasPrice_Gwei:
        #         break
        #     else:
        #         log("Жду снижения цены за газ")
        #         timeOut("teh")
        #         timeOut("teh")
        #         timeOut("teh")




        contract = web3.eth.contract(
            abi=deploy_abi,
            bytecode=deploy_bytcode
        )

        transaction = contract.constructor().build_transaction({
            'from': wallet,
            'value': 0,
            "gasPrice": web3.eth.gas_price ,
            'nonce': web3.eth.get_transaction_count(wallet),
        })
        gasLimit = web3.eth.estimate_gas(transaction)
        transaction['gas'] = int(gasLimit * config.gas_kef)


        

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.to_hex(web3.eth.send_raw_transaction(signed_txn.rawTransaction))
        tx_result = web3.eth.wait_for_transaction_receipt(txn_hash)
        print(tx_result)
        if tx_result['status'] == 1:
            contractAddress = tx_result['contractAddress']
            log_ok(f'deploy OK: https://scrollscan.com/tx/{txn_hash}')
            log_ok(f'contractAddress: {contractAddress}')
            save_private_key_to("private_keys_step2", private_key+";"+contractAddress)
            save_wallet_to("deploy_ok_pk", private_key)
            fun.delete_private_key_from_file("private_keys", private_key)
            fun.delete_wallet_from_file("no_money_wa", wallet)
            fun.delete_wallet_from_file("deploy_false_pk", private_key)
        else:
            log_error(f'deploy false: {txn_hash}')
            save_wallet_to("deploy_false_pk", private_key)
            fun.delete_wallet_from_file("no_money_wa", wallet)
            keys_list.append(private_key)   

        timeOut()


    except Exception as error:
        fun.log_error(f'bridge false: {error}')    
        save_wallet_to("bridge_false_pk", private_key)
        keys_list.append(private_key)
        timeOut("teh")
        continue


        
  
    
log("Ну типа все, кошельки закончились!")        

