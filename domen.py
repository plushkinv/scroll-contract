from statistics import mean
import time
from web3 import Web3
import requests
import random
from datetime import datetime
import config
import fun
from fun import *



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


        dapp_abi = json.load(open('abi/domen.json'))
        dapp_address = web3.to_checksum_address("0xe2e1d82b050bb5bfec776b2653a72f093a8373ab")
        dapp_contract = web3.eth.contract(address=dapp_address, abi=dapp_abi)  


        domen = fun.get_random_line_from_file("words.txt") + str(random.randint(100, 99900))

        transaction = dapp_contract.functions.Register(
            domen,
            "0x0000000000000000000000000000000000000000"
        ).build_transaction({
            'from': wallet,
            'value': Web3.to_wei(0.0025, 'ether') ,
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
            contractAddress = tx_result['contractAddress']
            log_ok(f'domen OK: https://scrollscan.com/tx/{txn_hash}')
            save_wallet_to("domen_ok_pk", private_key)
            fun.delete_private_key_from_file("private_keys", private_key)
            fun.delete_wallet_from_file("no_money_wa", wallet)
            fun.delete_wallet_from_file("domen_error_pk", private_key)
        else:
            log_error(f'domen false: {txn_hash}')
            save_wallet_to("domen_error_pk", private_key)
            fun.delete_wallet_from_file("no_money_wa", wallet)

        timeOut()


    except Exception as error:
        fun.log_error(f'domen false: {error}')    
        save_wallet_to("domen_false_pk", private_key)
        timeOut("teh")
        continue


        
  
    
log("Ну типа все, кошельки закончились!")        

