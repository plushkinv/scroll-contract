import time
from web3 import Web3
import requests
import random
from datetime import datetime
import config
import fun
from fun import *
import subprocess


current_datetime = datetime.now()
print(f"\n\n {current_datetime}")
print(f'============================================= Плюшкин Блог =============================================')
print(f'subscribe to : https://t.me/plushkin_blog \n============================================================================================================\n')

keys_list = []
with open("private_keys_step2.txt", "r") as f:
    for row in f:
        private_key=row.strip()
        if private_key:
            keys_list.append(private_key)

random.shuffle(keys_list)
i=0
for private_key_line in keys_list:
    i+=1
    contractAddress = ""
    string_list = private_key_line.split(";")
    private_key = string_list[0]
    contractAddress = string_list[1]
    deploy_abi = '[{"inputs":[],"name":"increaseCounter","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"x","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"}]'

    # print(deploy_abi)
    abi = json.loads(deploy_abi)
    
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

        # ожидает подходящий газ
        wait_gas_price_eth()


        dapp_address = web3.to_checksum_address(contractAddress)
        dapp_contract = web3.eth.contract(address=dapp_address, abi=abi)  


        transaction = dapp_contract.functions.increaseCounter().build_transaction({
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
        # print(tx_result)
        if tx_result['status'] == 1:
            log_ok(f'checkIn OK: https://scrollscan.com/tx/{txn_hash}')
        else:
            log_error(f'checkIn false: {txn_hash}')

        timeOut()


    except Exception as error:
        fun.log_error(f'checkIn false: {error}')    
        timeOut("teh")
        continue


        
  
    
log("Ну типа все, кошельки закончились!")        

