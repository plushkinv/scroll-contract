import json
import os
from datetime import datetime
import random
from statistics import mean
import time
import requests
from web3 import Web3
import config



log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log"




def log(text, status=""):
    now = datetime.now()
    log_text = now.strftime('%d %H:%M:%S')+": "
    with open(log_file, "a", encoding='utf-8') as f:
        if status == "error":
            color_code = "\033[91m"  # red
            log_text = log_text + "ERROR: "
        elif status == "ok":
            color_code = "\033[92m"  # green
            log_text = log_text + "OK: "
        else:
            color_code = "\033[0m"  # white
        log_text = log_text + f"{text}"
        log_text_color = f"{color_code}{log_text}\033[0m"
        f.write(log_text + "\n")
        print(log_text_color)

def log_error(text):
    log(text, "error")
    return "error"

def log_error_critical(text):
    log(text, "error")
    f=open(f"{log_dir}/critical.log", "a", encoding='utf-8')
    f.write(text + "\n")    
    return "error"

def log_ok(text):
    log(text, "ok")
    return "ok"

def save_wallet_to(filename, wallet):
    file_path = f"{log_dir}/{filename}.log"
    # Проверяем, есть ли строка в файле
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
           if wallet in file.read():
                return    
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(wallet + "\n")

def delete_wallet_from_file(filename, wallet):
    file_path = f"{log_dir}/{filename}.log"
    if not os.path.exists(file_path):
        return
    # Открываем файл на чтение
    lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for row in f:
            line=row.strip()
            if line:
                if line != wallet:
                    lines.append(line + "\n")

    # Открываем файл на запись и записываем измененный список строк
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def save_private_key_to(filename, wallet):
    file_path = f"{filename}.txt"
    # Проверяем, есть ли строка в файле
    if os.path.exists(file_path):    
        with open(file_path, 'r', encoding='utf-8') as file:
            if wallet in file.read():
                return
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(wallet + "\n")
        
def delete_private_key_from_file(filename, wallet):
    file_path = f"{filename}.txt"
    if not os.path.exists(file_path):
        return    
    # Открываем файл на чтение
    lines = []
    with open(file_path, "r", encoding='utf-8') as f:
        for row in f:
            line=row.strip()
            if line:
                if line != wallet:
                    lines.append(line + "\n")

    # Открываем файл на запись и записываем измененный список строк
    with open(file_path, "w", encoding='utf-8') as f:
        f.writelines(lines)  



def timeOut(type="main"):
    if type=="main":
        time_sleep=random.randint(config.timeoutMin, config.timeoutMax)
    if type=="teh":
        time_sleep=random.randint(config.timeoutTehMin, config.timeoutTehMax)
        
    if int(time_sleep/60) > 0:
        log(f"пауза {int(time_sleep/60)} минут")
    time.sleep(time_sleep)




def get_new_prices(token = False):


    if token:
        try:
            url =f'https://min-api.cryptocompare.com/data/price?fsym={token}&tsyms=USDT'
            result = requests.get(url=url, proxies=config.proxies)
            if result.status == 200:
                resp_json = result.json(content_type=None)
                new_price = float(resp_json['USDT'])
                config.prices[token] = new_price
                log(f"Обновил цену для {token}= {new_price}")
        except Exception as error:
            log_error(f'Не смог узнать цену для {token}: {error}')

    else:
            
        if config.prices["last_update"] > int(time.time()-3600):
            return False
        config.prices["last_update"] = int(time.time())

        for token, price in config.prices.items():    
            if token == "last_update":
                continue

            try:
                url =f'https://min-api.cryptocompare.com/data/price?fsym={token}&tsyms=USDT'
                if config.proxy_use:
                    result = requests.get(url=url, proxies=config.proxies)
                else:
                    result = requests.get(url=url)                    
                if result.status_code == 200:
                    resp_json = result.json()
                    new_price = float(resp_json['USDT'])
                    config.prices[token] = new_price
                    log(f"Обновил цену для {token}= {new_price}")
            except Exception as error:
                log_error(f'Не смог узнать цену для {token}: {error}')

            time.sleep(1)

    return True