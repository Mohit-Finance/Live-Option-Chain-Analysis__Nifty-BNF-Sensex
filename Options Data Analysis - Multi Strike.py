import time
import json
from datetime import datetime, date, timedelta
from datetime import time as tm
from types import SimpleNamespace
import pyotp
import sys
import upstox_client
import threading
import requests
import pandas as pd
import numpy as np
import xlwings as xw
from collections import defaultdict
import pickle
import msvcrt

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor

from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg

from pyqtgraph import TextItem, mkPen, QtCore
from pyqtgraph.exporters import ImageExporter

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os

######################################################################################
tdate = datetime.now().date()
code = None
access = None

os.makedirs(f'Credentials/Data/{tdate}', exist_ok=True)

def time_fun():
    ttime = datetime.now().time().replace(microsecond=0)
    ttime = ttime.strftime("%H:%M:%S")
    return ttime

def show_totp(secret):
    totp = pyotp.TOTP(secret)
    otp = totp.now()
    return otp

if not os.path.exists('Credentials/login_details.json'):
    print("User Details not found. First Create a User Base & Retry. Exiting program.")
    sys.exit()

with open('Credentials/login_details.json', 'r') as file_read:
    users_data = json.load(file_read)

allowed_namess = users_data.keys()
allowed_names = [name.lower() for name in allowed_namess]

name_dict = {}

for i in range(len(allowed_names)):
    name_dict[f'{allowed_names[i]}'] = f'{tdate}_access_code_{allowed_names[i]}.json'

name_list = name_dict.values()

file_list = os.listdir(f'Credentials/Data/{tdate}')

for name in name_list:
    if name in file_list:
        with open(f'Credentials/Data/{tdate}/{name}', 'r') as file_read:
            access = json.load(file_read)
            acc_name = name[23:][:-5]

if not access:

    while True:
        acc_name = input(f'\nEnter Name of Account Holder to Login From {list(allowed_namess)} : ').lower()
        if acc_name in allowed_names:
            break
        else:
            print(f"\nInvalid User. Please Enter Registered User Name {list(allowed_namess)}'.")

    try:
        with open(f'Credentials/Data/{tdate}/{tdate}_access_code_{acc_name}.json', 'r') as file_read:
            access = json.load(file_read)

    except:

        with open('Credentials/login_details.json', 'r') as file_read:
            login_details = json.load(file_read)

        api_key = login_details[f'{acc_name.capitalize()}']['api_key']
        api_secret = login_details[f'{acc_name.capitalize()}']['api_secret']
        api_auth = login_details[f'{acc_name.capitalize()}']['api_auth']
        api_pin = login_details[f'{acc_name.capitalize()}']['pin']
        mobile_no = login_details[f'{acc_name.capitalize()}']['Mob No.']
        hold_name = login_details[f'{acc_name.capitalize()}']['full_name']

        print(f'\nTrying to Login from Account Holder: {hold_name}')

        uri = 'https://www.google.com/'
        url1 = f'https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={api_key}&redirect_uri={uri}\n'

        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = uc.Chrome(version_main=144, options=options)
        # driver = uc.Chrome(options=options)

        # driver = uc.Chrome() # Use this line instead to run Chrome in normal (visible) mode, (In that case, comment out the 5 lines above that set headless options)

        driver.get(url1)
        wait = WebDriverWait(driver, 20)
        phone_input = wait.until(EC.presence_of_element_located((By.ID, "mobileNum")))
        phone_input.send_keys(mobile_no)
        otp_button = wait.until(EC.element_to_be_clickable((By.ID, "getOtp")))
        otp_button.click()
        # print("✅ Phone number entered, now captcha should appear normally")

        totp_value = show_totp(api_auth)
        totp_input = wait.until(EC.presence_of_element_located((By.ID, "otpNum")))
        totp_input.send_keys(totp_value)
        proceed_button = wait.until(EC.element_to_be_clickable((By.ID, "continueBtn")))
        proceed_button.click()
        # print("✅ TOTP entered and Continue clicked!")

        pin_input = wait.until(EC.presence_of_element_located((By.ID, "pinCode")))
        pin_input.send_keys(api_pin)
        proceed_button = wait.until(EC.element_to_be_clickable((By.ID, "pinContinueBtn")))
        proceed_button.click()

        # print("✅ PIN entered and proceed button clicked!")
        time.sleep(3)
        code_url = driver.current_url

        driver.quit()

        start = code_url.find('code=')
        if start != -1:
            start =start + 5  # move past 'code='
            code = code_url[start:start+6]
        else:
            print("No code found in the URL")

        url = 'https://api.upstox.com/v2/login/authorization/token'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'code': code,
            'client_id': api_key,
            'client_secret': api_secret,
            'redirect_uri': uri,
            'grant_type': 'authorization_code',
        }

        response = requests.post(url, headers=headers, data=data)
        access = response.json()['access_token']
        print(f'\nLogin Successful, Status Code : {response.status_code}')
        print(f"User Name : {response.json()['user_name']}\nEmail ID : {response.json()['email']}")

        with open(f'Credentials/Data/{tdate}/{tdate}_access_code_{acc_name}.json', 'w') as file_write:
            json.dump(access, file_write)

print(f'\nLogin Successful from Account : {acc_name.capitalize()}')


#############################################################################
to_date= date.today()
from_date = to_date - timedelta(days=750)

to_date   = to_date.strftime("%Y-%m-%d")
from_date = from_date.strftime("%Y-%m-%d")

configuration = upstox_client.Configuration()
configuration.access_token = access
api = upstox_client.HistoryV3Api(upstox_client.ApiClient(configuration))
response_iv = api.get_historical_candle_data1(instrument_key="NSE_INDEX|India VIX", unit="days", interval="1", from_date=from_date, to_date=to_date)
response_iv = response_iv.to_dict()
df_iv = pd.DataFrame(response_iv['data']['candles'], columns=['time', 'open', 'high', 'low', 'close', 'vol1', 'vol2'])
iv_data_close = df_iv['close']


def instrument():
    inst_url = 'https://assets.upstox.com/market-quote/instruments/exchange/complete.csv.gz'
    instrument = pd.read_csv(inst_url)
    instrument.to_csv('Credentials/instrument.csv')

if os.path.exists('Credentials/instrument.csv'):
    modified_time = datetime.fromtimestamp(os.path.getmtime('Credentials/instrument.csv'))
    today_9am = datetime.combine(datetime.today(), tm(9, 0, 0))
    yn = '1' if modified_time < today_9am else '0'
else:
    yn = '1'

if yn=='1':
    instrument()
    print("Instrument Data Updated Successfully")

try:
    inst_data = pd.read_csv('Credentials/instrument.csv', index_col=0)
    inst_data['expiry'] = pd.to_datetime(inst_data['expiry'], format='%Y-%m-%d', errors='coerce')
except:
    instrument()
    print("Can't find 'Instrument.csv' file, Latest Instrument Data Downloaded Successfully")
    inst_data = pd.read_csv('Credentials/instrument.csv', index_col=0)
    inst_data['expiry'] = pd.to_datetime(inst_data['expiry'], format='%Y-%m-%d', errors='coerce')

t_time = datetime.now().time().replace(microsecond=0)
start_time = tm(9,15,5,0)
end_time = tm(15,30,0,0)

while t_time < start_time:
    t_time = datetime.now().time().replace(microsecond=0)
    print(f'\rCurrent Time : {t_time} | Market Will Start at {start_time}', end='', flush=True)
    time.sleep(1)

configuration = upstox_client.Configuration()
configuration.access_token = access
data_base = {}
streamer = None
lock = threading.Lock()

def on_open():
    # print(open1)
    print("✅ WebSocket Connection Established")

def on_message(message):
    global sub_list_ce, sub_list_pe, inst_strike_pair
    if 'feeds' not in message:
        return

    data = message['feeds']
    for key, value in data.items():
        try:
            if "marketFF" in value.get("fullFeed", {}):
                ff = value['fullFeed']['marketFF']
                with lock:
                    data_base[key] = {
                        'ltp': ff.get('ltpc', {}).get('ltp') or None,
                        'type': 'CE' if key in sub_list_ce else 'PE',
                        'strike': inst_strike_pair.loc[key, 'strike'] if key in inst_strike_pair.index else None,
                        'prev_close': ff.get('ltpc', {}).get('cp') or None,
                        'delta': ff.get('optionGreeks', {}).get('delta') or None,
                        'theta': ff.get('optionGreeks', {}).get('theta') or None,
                        'gamma': ff.get('optionGreeks', {}).get('gamma') or None,
                        'vega': ff.get('optionGreeks', {}).get('vega') or None,
                        'volume': (ff.get('marketOHLC', {}).get('ohlc', [{}])[0].get('vol')) or None,
                        'atp': ff.get('atp') or None,
                        'tbq': ff.get('tbq') or None,
                        'tsq': ff.get('tsq') or None,
                        'oi': ff.get('oi') or None,
                        'iv': ff.get('iv') or None}

            elif "indexFF" in value.get("fullFeed", {}):
                ff = value['fullFeed']['indexFF']
                with lock:
                    data_base[key] = {'ltp': ff.get('ltpc', {}).get('ltp') or None}

        except Exception as e:
            print(f'Missing Key in {key} : {e}')
            continue

def start_stream():
    global sub_list, configuration, streamer, index_key

    streamer = upstox_client.MarketDataStreamerV3(upstox_client.ApiClient(configuration), sub_list+index_key, "full")
    streamer.on("open", on_open)
    streamer.on("message", on_message)
    streamer.connect()

def main():
    thread = threading.Thread(target=start_stream)
    thread.start()

apiInstance = upstox_client.MarketQuoteV3Api(upstox_client.ApiClient(configuration))

nifty_expiry = None
bnf_expiry = None
sensex_expiry = None
index_key = ["NSE_INDEX|Nifty 50", "NSE_INDEX|Nifty Bank", "BSE_INDEX|SENSEX", "NSE_INDEX|India VIX"]
def synth_atm_index():

    global nifty_expiry, bnf_expiry, sensex_expiry

    nifty_ce_ltp = nifty_pe_ltp = None
    bnf_ce_ltp = bnf_pe_ltp = None
    sensex_ce_ltp = sensex_pe_ltp = None

    index_key = "NSE_INDEX|Nifty 50,NSE_INDEX|Nifty Bank,BSE_INDEX|SENSEX"
    index_spot = apiInstance.get_ltp(instrument_key=index_key).to_dict()

    nifty_spot = index_spot['data']['NSE_INDEX:Nifty 50']['last_price']
    bnf_spot = index_spot['data']['NSE_INDEX:Nifty Bank']['last_price']
    sensex_spot = index_spot['data']['BSE_INDEX:SENSEX']['last_price']

    nifty_contract = contract_keys(index_spot = nifty_spot, step_size = 50, exchange = 'NSE_FO', name = 'NIFTY')
    bnf_contract =  contract_keys(index_spot = bnf_spot, step_size = 100, exchange = 'NSE_FO', name = 'BANKNIFTY')
    sensex_contract =  contract_keys(index_spot = sensex_spot, step_size = 100, exchange = 'BSE_FO', name = 'SENSEX')

    all_contract_keys = f"{nifty_contract[0]},{nifty_contract[1]},{bnf_contract[0]},{bnf_contract[1]},{sensex_contract[0]},{sensex_contract[1]}"
    
    nifty_atm = nifty_contract[2]
    bnf_atm = bnf_contract[2]
    sensex_atm = sensex_contract[2]

    nifty_expiry = nifty_contract[3]
    bnf_expiry = bnf_contract[3]
    sensex_expiry = sensex_contract[3]

    contract_quote = apiInstance.get_ltp(instrument_key=all_contract_keys).to_dict()

    for key, value in contract_quote['data'].items():
        # ✅ NIFTY
        if key.endswith("CE") and "NSE_FO:NIFTY" in key:
            nifty_ce_ltp = value['last_price']
        elif key.endswith("PE") and "NSE_FO:NIFTY" in key:
            nifty_pe_ltp = value['last_price']

        # ✅ BANKNIFTY
        elif key.endswith("CE") and "NSE_FO:BANKNIFTY" in key:
            bnf_ce_ltp = value['last_price']
        elif key.endswith("PE") and "NSE_FO:BANKNIFTY" in key:
            bnf_pe_ltp = value['last_price']

        # ✅ SENSEX
        elif key.endswith("CE") and "BSE_FO:SENSEX" in key:
            sensex_ce_ltp = value['last_price']
        elif key.endswith("PE") and "BSE_FO:SENSEX" in key:
            sensex_pe_ltp = value['last_price']


    if None in [nifty_ce_ltp, nifty_pe_ltp, bnf_ce_ltp, bnf_pe_ltp, sensex_ce_ltp, sensex_pe_ltp]:
        raise ValueError("Some CE/PE values missing, check response or instrument_key mapping")

    nifty_synthetic_spot = nifty_ce_ltp - nifty_pe_ltp + nifty_atm
    nifty_synthetic_atm = round(nifty_synthetic_spot/50) * 50

    bnf_synthetic_spot = bnf_ce_ltp - bnf_pe_ltp + bnf_atm
    bnf_synthetic_atm = round(bnf_synthetic_spot/100) * 100

    sensex_synthetic_spot = sensex_ce_ltp - sensex_pe_ltp + sensex_atm
    sensex_synthetic_atm = round(sensex_synthetic_spot/100) * 100

    index_synthetic_atm = {'nifty':nifty_synthetic_atm, 'bnf':bnf_synthetic_atm, 'sensex':sensex_synthetic_atm}

    return index_synthetic_atm


def contract_keys(index_spot, step_size, exchange, name):

    index_atm = round(index_spot/step_size) * step_size
    index_dataframe = inst_data[(inst_data['exchange'] == exchange) & (inst_data['instrument_type'] == "OPTIDX") & (inst_data['name'] == name)]
    index_expiry = sorted(index_dataframe['expiry'].unique().tolist())

    index_atm_strikes_df = inst_data[(inst_data['exchange'] == exchange) & (inst_data['instrument_type'] == "OPTIDX") & (inst_data['name'] == name) & (inst_data['expiry'] == index_expiry[0]) & (inst_data['strike'] == index_atm)]
    index_atm_ce_instkey = index_atm_strikes_df[index_atm_strikes_df['option_type'] == 'CE']['instrument_key'].iloc[0]
    index_atm_pe_instkey = index_atm_strikes_df[index_atm_strikes_df['option_type'] == 'PE']['instrument_key'].iloc[0]

    return [index_atm_ce_instkey, index_atm_pe_instkey, index_atm, index_expiry]

synth_atm = synth_atm_index()
####### Upto Here we have brought Synthetic ATM Strike for each index Nifty, BankNifty, Sensex #######

old_synth_atm = synth_atm


def valid_strikes(synth_atm):
    global inst_data

    nifty_upper_strikes = []
    nifty_lower_strikes = []
    bnf_upper_strikes = []
    bnf_lower_strikes = []
    sensex_upper_strikes = []
    sensex_lower_strikes = []

    total_strikes = 25

    for i in range (1, total_strikes+1):
        nifty_upper_strikes.append(synth_atm['nifty'] + (i)*50)
        bnf_upper_strikes.append(synth_atm['bnf'] + (i)*100)
        sensex_upper_strikes.append(synth_atm['sensex'] + (i)*100)

        nifty_lower_strikes.append(synth_atm['nifty'] - (i)*50)
        bnf_lower_strikes.append(synth_atm['bnf'] - (i)*100)
        sensex_lower_strikes.append(synth_atm['sensex'] - (i)*100)

    nifty_option_strikes = nifty_lower_strikes + [synth_atm['nifty']] + nifty_upper_strikes
    bnf_option_strikes = bnf_lower_strikes + [synth_atm['bnf']] + bnf_upper_strikes
    sensex_option_strikes = sensex_lower_strikes + [synth_atm['sensex']] + sensex_upper_strikes
    ####### Got all the Strikes required to prepare Option Chain of Nifty, BNF and Sensex as per Synthetic Strikes of each Index #######

    nifty_option_inst_ce = inst_data[(inst_data['exchange'] == 'NSE_FO') & (inst_data['instrument_type'] == 'OPTIDX') & (inst_data['name'] == 'NIFTY') & (inst_data['expiry'] == nifty_expiry[0]) & (inst_data['option_type'] == 'CE') & (inst_data['strike'].isin(nifty_option_strikes))]['instrument_key'].tolist()
    nifty_option_inst_pe = inst_data[(inst_data['exchange'] == 'NSE_FO') & (inst_data['instrument_type'] == 'OPTIDX') & (inst_data['name'] == 'NIFTY') & (inst_data['expiry'] == nifty_expiry[0]) & (inst_data['option_type'] == 'PE') & (inst_data['strike'].isin(nifty_option_strikes))]['instrument_key'].tolist()
    bnf_option_inst_ce = inst_data[(inst_data['exchange'] == 'NSE_FO') & (inst_data['instrument_type'] == 'OPTIDX') & (inst_data['name'] == 'BANKNIFTY') & (inst_data['expiry'] == bnf_expiry[0]) & (inst_data['option_type'] == 'CE') &(inst_data['strike'].isin(bnf_option_strikes))]['instrument_key'].tolist()
    bnf_option_inst_pe = inst_data[(inst_data['exchange'] == 'NSE_FO') & (inst_data['instrument_type'] == 'OPTIDX') & (inst_data['name'] == 'BANKNIFTY') & (inst_data['expiry'] == bnf_expiry[0]) & (inst_data['option_type'] == 'PE') &(inst_data['strike'].isin(bnf_option_strikes))]['instrument_key'].tolist()
    sensex_option_inst_ce = inst_data[(inst_data['exchange'] == 'BSE_FO') & (inst_data['instrument_type'] == 'OPTIDX') & (inst_data['name'] == 'SENSEX') & (inst_data['expiry'] == sensex_expiry[0]) & (inst_data['option_type'] == 'CE') & (inst_data['strike'].isin(sensex_option_strikes))]['instrument_key'].tolist()
    sensex_option_inst_pe = inst_data[(inst_data['exchange'] == 'BSE_FO') & (inst_data['instrument_type'] == 'OPTIDX') & (inst_data['name'] == 'SENSEX') & (inst_data['expiry'] == sensex_expiry[0]) & (inst_data['option_type'] == 'PE') & (inst_data['strike'].isin(sensex_option_strikes))]['instrument_key'].tolist()
    
    index_ce_pe_list = [nifty_option_inst_ce, nifty_option_inst_pe, bnf_option_inst_ce, bnf_option_inst_pe, sensex_option_inst_ce, sensex_option_inst_pe]

    sub_list_ce = nifty_option_inst_ce + bnf_option_inst_ce + sensex_option_inst_ce
    sub_list_pe = nifty_option_inst_pe + bnf_option_inst_pe + sensex_option_inst_pe
    sub_list = sub_list_ce + sub_list_pe

    inst_strike_pair = inst_data[inst_data['instrument_key'].isin(sub_list)][['instrument_key', 'strike']].set_index('instrument_key')

    return sub_list_ce, sub_list_pe, sub_list, inst_strike_pair, index_ce_pe_list

sub_list_ce, sub_list_pe, sub_list, inst_strike_pair, index_ce_pe_list = valid_strikes(old_synth_atm)

if __name__ == "__main__":
    main()

while not data_base:
    print("⏳ Waiting for WebSocket data...")
    time.sleep(0.5)

print("✅ Local Database Updated!")


def default_list_dict():                        # Last layer → keys like 'ltp', 'oi', 'volume'
    return defaultdict(list)

def default_strike_dict():                      # Middle layer → strike → list(dict of lists)
    return defaultdict(default_list_dict)


structure = {}
structure_strike = {}
strikes_df_dict = {'nifty':None, 'bnf':None, 'sensex':None}
def data_prep(df_option, index):
    global structure, structure_strike, strikes_df_dict
    today = pd.Timestamp.today().normalize()
    df = df_option.copy()
    atm_row = df.loc[df['diff'].idxmin()]

    expiry = atm_row['expiry']

    spot = atm_row[f'{index}_spot']
    India_Vix = atm_row['India_Vix']
    IVP = atm_row['IVP']

    atm_strike = atm_row['strike']
    step = df['strike'].diff().mode()[0]

    atm_ce_ltp = atm_row['ltp_CE']
    atm_pe_ltp = atm_row['ltp_PE']
    atm_straddle_ltp = atm_ce_ltp + atm_pe_ltp

    atm_ce_vol = atm_row['volume_CE']
    atm_pe_vol = atm_row['volume_PE']
    atm_straddle_vol = atm_ce_vol + atm_pe_vol

    ce_df = df[(df['strike'] >= atm_strike-step) & (df['strike'] <= atm_strike+5*step)]
    pe_df = df[(df['strike'] <= atm_strike+step) & (df['strike'] >= atm_strike-5*step)]

    ce_buy_depth = ce_df['tbq_CE'].sum()
    ce_sell_depth = ce_df['tsq_CE'].sum()
    pe_buy_depth = pe_df['tbq_PE'].sum()
    pe_sell_depth = pe_df['tsq_PE'].sum()
    ce_buy_pressure = ce_buy_depth / (ce_buy_depth+ce_sell_depth) * 100
    pe_buy_pressure = pe_buy_depth / (pe_buy_depth+pe_sell_depth) * 100

    # ce_buy_depth = atm_row['tbq_CE']
    # ce_sell_depth = atm_row['tsq_CE']
    # pe_buy_depth = atm_row['tbq_PE']
    # pe_sell_depth = atm_row['tsq_PE']
    # ce_buy_pressure = ce_buy_depth / (ce_buy_depth+ce_sell_depth) * 100
    # pe_buy_pressure = pe_buy_depth / (pe_buy_depth+pe_sell_depth) * 100

    ce_ltp_sum = ce_df['ltp_CE'].sum()
    pe_ltp_sum = pe_df['ltp_PE'].sum()

    ce_delta_sum = ce_df['delta_CE'].sum()
    pe_delta_sum = abs(pe_df['delta_PE'].sum())

    ce_oi_sum = ce_df['oi_CE'].sum()
    pe_oi_sum = pe_df['oi_PE'].sum()

    ce_iv_avg = (ce_df['iv_CE']*ce_df['volume_CE']).sum()/ce_df['volume_CE'].sum()
    pe_iv_avg = (pe_df['iv_PE']*pe_df['volume_PE']).sum()/pe_df['volume_PE'].sum()

    timestamp = datetime.now()

    if index=='nifty' and not structure and not structure_strike:
        try:
            with open(f'Credentials/Data/{tdate}/{tdate}_raw_data.pkl', 'rb') as fr:
                structure = pickle.load(fr)
            with open(f'Credentials/Data/{tdate}/{tdate}_raw_data_strike.pkl', 'rb') as fr:
                structure_strike = pickle.load(fr)
        except:
            structure = defaultdict(default_list_dict)          # Shape 1: index → keys
            structure_strike = defaultdict(default_strike_dict) # Shape 2: index → strike → keys

    structure[index]['timestamp'].append(timestamp)
    structure[index]['expiry'].append(expiry)
    structure[index]['index'].append(index)
    structure[index]['today'].append(today)
    structure[index]['strike'].append(int(atm_strike))
    structure[index]['ce_ltp_sum'].append(round(float(ce_ltp_sum),2))
    structure[index]['pe_ltp_sum'].append(round(float(pe_ltp_sum),2))
    structure[index]['ce_delta_sum'].append(round(float(ce_delta_sum),2))
    structure[index]['pe_delta_sum'].append(round(float(pe_delta_sum),2))
    structure[index]['ce_oi_sum'].append(round(float(ce_oi_sum),2))
    structure[index]['pe_oi_sum'].append(round(float(pe_oi_sum),2))
    structure[index]['ce_iv_avg'].append(round(float(ce_iv_avg),2))
    structure[index]['pe_iv_avg'].append(round(float(pe_iv_avg),2))
    structure[index]['ce_buy_pressure'].append(round(float(ce_buy_pressure),2))
    structure[index]['pe_buy_pressure'].append(round(float(pe_buy_pressure),2))
    structure[index]['India_Vix'].append(round(float(India_Vix),2))
    structure[index]['spot'].append(round(float(spot),2))
    structure[index]['IVP'].append(IVP)

    if strikes_df_dict[f'{index}'] is None:
        try:
            with open(f'Credentials/Data/{tdate}/strikes_df_list_{index}_{tdate}.json', 'r') as fileread:
                strikes_df_dict[f'{index}'] = json.load(fileread)
        except:
            mid = len(df) // 2
            strikes_df_dict[f'{index}'] = df['strike'].iloc[mid-12 : mid+13].tolist()
            # strikes_df_dict[f'{index}'] = df['strike'].iloc[3:18].tolist()
            with open(f'Credentials/Data/{tdate}/strikes_df_list_{index}_{tdate}.json', 'w') as filewrite:
                json.dump(strikes_df_dict[f'{index}'], filewrite)

    for strike in strikes_df_dict[f'{index}']:
        structure_strike[index][strike]['timestamp'].append(timestamp)
        structure_strike[index][strike]['ltp_CE'].append(df.loc[df['strike'] == strike, 'ltp_CE'].iloc[0])
        structure_strike[index][strike]['ltp_PE'].append(df.loc[df['strike'] == strike, 'ltp_PE'].iloc[0])
        structure_strike[index][strike]['volume_CE'].append(df.loc[df['strike'] == strike, 'volume_CE'].iloc[0])
        structure_strike[index][strike]['volume_PE'].append(df.loc[df['strike'] == strike, 'volume_PE'].iloc[0])

initial_oi_data = {f'nifty_oi_ce_initial':None, f'nifty_oi_pe_initial':None, 'bnf_oi_ce_initial':None, f'bnf_oi_pe_initial':None, 'sensex_oi_ce_initial':None, f'sensex_oi_pe_initial':None,}
def option_chain(ce, pe, df, expiry, index):
    global initial_oi_data, iv_data_close
    df_index = df[df.index.isin(ce + pe)]
    df_ce = df_index[df_index['type'] == 'CE']
    df_pe = df_index[df_index['type'] == 'PE']
    df_option = pd.merge(df_ce, df_pe, on='strike', suffixes=('_CE', '_PE')).sort_values(by='strike', ascending=True)
    df_option['expiry'] = expiry
    df_option['iv_CE'] = df_option['iv_CE']*100
    df_option['iv_PE'] = df_option['iv_PE']*100

    df_option[f'{index}_spot'] = df.loc[{'nifty': 'NSE_INDEX|Nifty 50', 'bnf': 'NSE_INDEX|Nifty Bank', 'sensex': 'BSE_INDEX|SENSEX'}[index], 'ltp']
    india_vix = df.loc['NSE_INDEX|India VIX', 'ltp']

    df_option['diff'] = abs(df_option['ltp_CE'] - df_option['ltp_PE'])
    df_option['Δ_CE'] = round(((df_option['ltp_CE'] - df_option['prev_close_CE']) / df_option['prev_close_CE']),2)
    df_option['Δ_PE'] = round(((df_option['ltp_PE'] - df_option['prev_close_PE']) / df_option['prev_close_PE']),2)

    df_option['buy_per_CE'] = (df_option['tbq_CE'])/(df_option['tbq_CE'] + df_option['tsq_CE'])*100
    df_option['sell_per_CE'] = (df_option['tsq_CE'])/(df_option['tbq_CE'] + df_option['tsq_CE'])*100
    
    df_option['buy_per_PE'] = (df_option['tbq_PE'])/(df_option['tbq_PE'] + df_option['tsq_PE'])*100
    df_option['sell_per_PE'] = (df_option['tsq_PE'])/(df_option['tbq_PE'] + df_option['tsq_PE'])*100

    df_option['CE_depth'] = (df_option['buy_per_CE'].round(2).astype(str) + '%' + ' / ' + df_option['sell_per_CE'].round(2).astype(str) + '%')
    df_option['PE_depth'] = (df_option['buy_per_PE'].round(2).astype(str) + '%' + ' / ' + df_option['sell_per_PE'].round(2).astype(str) + '%')
    df_option['India_Vix'] = india_vix

    ivp_6m = round(((iv_data_close.head(126) <= india_vix).mean() * 100))
    ivp_1y = round(((iv_data_close.head(252) <= india_vix).mean() * 100))
    ivp_2y = round(((iv_data_close <= india_vix).mean() * 100))

    df_option['IVP'] = f'{ivp_6m} {ivp_1y} {ivp_2y}'


    if initial_oi_data[f'{index}_oi_ce_initial'] is None:
        try:
            with open(f'Credentials/Data/{tdate}/init_oi_{index}_{tdate}.pkl', 'rb') as fileread:
                initial_oi_data = pickle.load(fileread)
                df_option['oi_CE_initial'] = initial_oi_data[f'{index}_oi_ce_initial']
                df_option['oi_PE_initial'] = initial_oi_data[f'{index}_oi_pe_initial']
        except:
            initial_oi_data[f'{index}_oi_ce_initial'] = df_option['oi_CE']
            initial_oi_data[f'{index}_oi_pe_initial'] = df_option['oi_PE']
            with open(f'Credentials/Data/{tdate}/init_oi_{index}_{tdate}.pkl', 'wb') as filewrite:
                pickle.dump(initial_oi_data, filewrite)
                df_option['oi_CE_initial'] = initial_oi_data[f'{index}_oi_ce_initial']
                df_option['oi_PE_initial'] = initial_oi_data[f'{index}_oi_pe_initial']
    
    df_option['oi_CE_initial'] = initial_oi_data[f'{index}_oi_ce_initial']
    df_option['oi_PE_initial'] = initial_oi_data[f'{index}_oi_pe_initial'] 
    # print(df_option, index)

    df_option['Δ_OI_CE'] = (((df_option['oi_CE'] - df_option['oi_CE_initial']) / df_option['oi_CE_initial'])).round(2)
    df_option['Δ_OI_PE'] = (((df_option['oi_PE'] - df_option['oi_PE_initial']) / df_option['oi_PE_initial'])).round(2)

    # df_option['B/S CE'] = round((df_option['tbq_CE'] / df_option['tsq_CE']),2)
    # df_option['B/S PE'] = round((df_option['tbq_PE'] / df_option['tsq_PE']),2)
    df_option = df_option[['expiry', 'prev_close_CE', 'delta_CE', 'theta_CE', 'gamma_CE', 'vega_CE', 'atp_CE', 'tbq_CE', 'tsq_CE', 'CE_depth', 'oi_CE', 'iv_CE', 'volume_CE', 'Δ_OI_CE','Δ_CE', 'ltp_CE', 'strike', 'ltp_PE', 'Δ_PE', 'Δ_OI_PE', 'volume_PE', 'iv_PE', 'oi_PE', 'PE_depth', 'tsq_PE', 'tbq_PE', 'atp_PE', 'vega_PE', 'gamma_PE', 'theta_PE', 'delta_PE', 'prev_close_PE', 'diff', f'{index}_spot', 'India_Vix', 'IVP']]
    
    option_data = df_option.copy()
    option_data["timestamp"] = pd.Timestamp.now()
    write_header = not os.path.exists(f'Credentials/Data/{tdate}/{index}_option_chain_{tdate}.csv')
    option_data.to_csv(f'Credentials/Data/{tdate}/{index}_option_chain_{tdate}.csv', mode='a', header=write_header, index=False)

    data_prep(df_option, index)

    return df_option

def final_data_prep(df_dict):
    sec = datetime.now().second

    df = pd.DataFrame(df_dict)

    nifty_df = df['nifty']
    bnf_df = df['bnf']
    sensex_df = df['sensex']

    nifty_df = pd.DataFrame.from_dict(df['nifty'].to_dict(), orient='columns')
    bnf_df   = pd.DataFrame.from_dict(df['bnf'].to_dict(), orient='columns')
    sensex_df= pd.DataFrame.from_dict(df['sensex'].to_dict(), orient='columns')

    index = [nifty_df, bnf_df, sensex_df]

    #Calculating OI & LTP Change for all 3 index
    for i in range(0,3):

        index[i]['ce_oi_change'] = index[i]['ce_oi_sum']-index[i]['ce_oi_sum'].iloc[0]
        index[i]['pe_oi_change'] = index[i]['pe_oi_sum']-index[i]['pe_oi_sum'].iloc[0]
        index[i]['ce_ltp_change'] = index[i]['ce_ltp_sum']-index[i]['ce_ltp_sum'].iloc[0]
        index[i]['pe_ltp_change'] = index[i]['pe_ltp_sum']-index[i]['pe_ltp_sum'].iloc[0]

    final_plot_data = {'nifty':nifty_df, 'bnf':bnf_df, 'sensex':sensex_df}

    if sec in [1,2,3]:
        with open(f'Credentials/Data/{tdate}/{tdate}_final_plot_data.pkl', 'wb') as fw:
            pickle.dump(final_plot_data, fw)

    return final_plot_data


def final_data_prep_strike(df_dict_strike):
    nifty_strike, bnf_strike, sensex_strike = {}, {}, {}
    sec = datetime.now().second
    strike_df = {}

    df_nifty = df_dict_strike['nifty']
    df_bnf = df_dict_strike['bnf']
    df_sensex = df_dict_strike['sensex']

    index_list = [df_nifty, df_bnf, df_sensex]
    main_list = [nifty_strike, bnf_strike, sensex_strike]

    for i in range(0,3):
        for strike, features in index_list[i].items():
            df = pd.DataFrame(features)
            df['ltp_CE_x_vol'] = df['ltp_CE'] * df['volume_CE']
            df['ltp_CE_vwap'] = df['ltp_CE_x_vol'].cumsum() / df['volume_CE'].cumsum()

            df['ltp_PE_x_vol'] = df['ltp_PE'] * df['volume_PE']
            df['ltp_PE_vwap'] = df['ltp_PE_x_vol'].cumsum() / df['volume_PE'].cumsum()

            df['straddle_ltp'] = df['ltp_CE'] + df['ltp_PE']
            df['straddle_vol'] = df['volume_CE'] + df['volume_PE']
            df['ltp_x_vol'] = df['straddle_ltp'] * df['straddle_vol']
            df['straddle_vwap'] = df['ltp_x_vol'].cumsum() / df['straddle_vol'].cumsum()

            df['vol_CE_diff'] = df['volume_CE'].diff()
            df['ltp_CE_diff'] = df['ltp_CE'].diff()
            df['ltp_CE_sign'] = np.sign(df['ltp_CE_diff'])
            df['pre_obv_CE'] = df['vol_CE_diff'] * df['ltp_CE_sign']
            df['obv_CE'] = df['pre_obv_CE'].cumsum()

            df['vol_PE_diff'] = df['volume_PE'].diff()
            df['ltp_PE_diff'] = df['ltp_PE'].diff()
            df['ltp_PE_sign'] = np.sign(df['ltp_PE_diff'])
            df['pre_obv_PE'] = df['vol_PE_diff'] * df['ltp_PE_sign']
            df['obv_PE'] = df['pre_obv_PE'].cumsum()

            df = df[['timestamp', 'ltp_CE', 'ltp_CE_vwap', 'ltp_PE', 'ltp_PE_vwap', 'straddle_ltp', 'straddle_vwap', 'obv_CE', 'obv_PE']]

            main_list[i][f'{strike}'] = df

    strike_df = {'nifty':nifty_strike, 'bnf':bnf_strike, 'sensex':sensex_strike}

    if sec in [1,2,3]:
        with open(f'Credentials/Data/{tdate}/{tdate}_final_plot_data_strike.pkl', 'wb') as fw:
            pickle.dump(strike_df, fw)

    return strike_df



app = QApplication(sys.argv)

# Create main window
main = QMainWindow()
main.setWindowTitle("Option Data Analysis")
win = pg.GraphicsLayoutWidget()
main.setCentralWidget(win) 

main_st = QMainWindow()
main_st.setWindowTitle("Option Data Analysis")
win_st = pg.GraphicsLayoutWidget()
main_st.setCentralWidget(win_st)

def plot_graph(df):
    nifty_df = df['nifty']
    bnf_df = df['bnf']
    sensex_df = df['sensex']

    sec = datetime.now().second

    if sec in [1,2,3]:

        nifty_df.to_csv('nifty.csv')
        bnf_df.to_csv('bnf.csv')
        sensex_df.to_csv('sensex.csv')

wb = xw.Book('Analysis.xlsx')
sht_summary = wb.sheets['summary']
sht_nifty = wb.sheets['nifty']
sht_bnf = wb.sheets['bnf']
sht_sensex = wb.sheets['sensex']

def format_oi(num):
    sign = "-" if num < 0 else ""   # capture the sign
    num = abs(num)                  # work with positive value for scaling
    
    if num >= 1_000_000:
        return f"{sign}{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{sign}{num/1_000:.2f}K"
    else:
        return f"{sign}{num}"


def one_time_index(row, column):
    ########################################################################################################
    # Controls the Visibility of all the 4 Axis and Text on it
    # Controls Visibility of Text
    plot00 = win.addPlot(row=row, col=column)
    plot00.getAxis('left').setStyle(showValues=True)
    plot00.getAxis('right').setStyle(showValues=False)
    plot00.getAxis('top').setStyle(showValues=False)
    plot00.getAxis('bottom').setStyle(showValues=True)
    # Controls Visibility of Axis
    plot00.showAxis('right', show=True)
    plot00.showAxis('top', show=False)
    plot00.showAxis('left', show=True)
    plot00.showAxis('bottom', show=True)

    plot00.addLegend() # Add a legend to the plot
    plot00_1 = plot00.plot([], pen=mkPen('g', width=3), name='CE OTMs Change') # Add green line for CE OTMs (empty data)
    plot00_2 = plot00.plot([], pen=mkPen('y', width=3), name='PE OTMs Change') # Add yellow line for PE OTMs (empty data)
    #------------------------------------------------------------------
    vplot00 = pg.ViewBox()
    plot00.scene().addItem(vplot00)
    plot00.getAxis('right').linkToView(vplot00)
    vplot00.setXLink(plot00)
    vplot00_1 = pg.PlotDataItem(pen=mkPen('g', width=3, style=QtCore.Qt.DotLine), name='CE OI Change')
    vplot00_2 = pg.PlotDataItem(pen=mkPen('y', width=3, style=QtCore.Qt.DotLine), name='PE OI Change')
    vplot00.addItem(vplot00_1)
    vplot00.addItem(vplot00_2)

    plot00.legend.addItem(vplot00_1, vplot00_1.name())
    plot00.legend.addItem(vplot00_2, vplot00_2.name())

    def update_vplot00_geometry():
        vplot00.setGeometry(plot00.getViewBox().sceneBoundingRect())
    plot00.getViewBox().sigResized.connect(update_vplot00_geometry)
    #------------------------------------------------------------------
    vvplot00 = pg.ViewBox()
    axis00B = pg.AxisItem('right')
    axis00B.setVisible(False)
    axis00B.setStyle(showValues=False)
    plot00.layout.addItem(axis00B, 2, 3)  # adds 3rd axis on right-most
    axis00B.linkToView(vvplot00)
    vvplot00.setXLink(plot00)
    plot00.scene().addItem(vvplot00)

    # Data curves for 3rd axis
    vvplot00_1 = pg.PlotDataItem(pen=mkPen('c', width=3), name='Blank')
    vvplot00_2 = pg.PlotDataItem(pen=mkPen('m', width=3), name='Blank')
    vvplot00.addItem(vvplot00_1)
    vvplot00.addItem(vvplot00_2)
    plot00.legend.addItem(vvplot00_1, vvplot00_1.name())
    plot00.legend.addItem(vvplot00_2, vvplot00_2.name())

    def update_vvplot00_geometry():
        vvplot00.setGeometry(plot00.getViewBox().sceneBoundingRect())
    plot00.getViewBox().sigResized.connect(update_vvplot00_geometry)

    #####################################################################################
    # Controls the Visibility of all the 4 Axis and Text on it
    # Controls Visibility of Text
    plot10 = win.addPlot(row=row+1, col=column)
    plot10.getAxis('left').setStyle(showValues=True)
    plot10.getAxis('right').setStyle(showValues=False)
    plot10.getAxis('top').setStyle(showValues=False)
    plot10.getAxis('bottom').setStyle(showValues=True)
    # Controls Visibility of Axis
    plot10.showAxis('right', show=True)
    plot10.showAxis('top', show=False)
    plot10.showAxis('left', show=True)
    plot10.showAxis('bottom', show=True)

    plot10.addLegend() # Add a legend to the plot
    plot10_1 = plot10.plot([], pen=mkPen('w', width=3), name='Straddle') # Add green line for CE OTMs (empty data)
    plot10_2 = plot10.plot([], pen=mkPen('r', width=3), name='Straddle VWAP') # Add yellow line for PE OTMs (empty data)
    #--------------------------------------------------------------------------------------------------
    vplot10 = pg.ViewBox()
    plot10.scene().addItem(vplot10)
    plot10.getAxis('right').linkToView(vplot10)
    vplot10.setXLink(plot10)

    vplot10_1 = pg.PlotDataItem(pen=mkPen('g', width=3, style=QtCore.Qt.DotLine), name='CE OBV')
    vplot10_2 = pg.PlotDataItem(pen=mkPen('y', width=3, style=QtCore.Qt.DotLine), name='PE OBV')
    vplot10.addItem(vplot10_1)
    vplot10.addItem(vplot10_2)

    plot10.legend.addItem(vplot10_1, vplot10_1.name())
    plot10.legend.addItem(vplot10_2, vplot10_2.name())

    def update_vplot10_geometry():
        vplot10.setGeometry(plot10.getViewBox().sceneBoundingRect())
    plot10.getViewBox().sigResized.connect(update_vplot10_geometry)
    #---------------------------------------------------------------------------------------------------
    vvplot10 = pg.ViewBox()
    axis10B = pg.AxisItem('right')
    axis10B.setVisible(False)
    axis10B.setStyle(showValues=False)
    plot10.layout.addItem(axis10B, 2, 3)
    axis10B.linkToView(vvplot10)
    vvplot10.setXLink(plot10)
    plot10.scene().addItem(vvplot10)

    vvplot10_1 = pg.PlotDataItem(pen=mkPen('c', width=3), name='Blank')
    vvplot10_2 = pg.PlotDataItem(pen=mkPen('m', width=3), name='Blank')
    vvplot10.addItem(vvplot10_1)
    vvplot10.addItem(vvplot10_2)
    plot10.legend.addItem(vvplot10_1, vvplot10_1.name())
    plot10.legend.addItem(vvplot10_2, vvplot10_2.name())

    def update_vvplot10_geometry():
        vvplot10.setGeometry(plot10.getViewBox().sceneBoundingRect())
    plot10.getViewBox().sigResized.connect(update_vvplot10_geometry)
    #########################################################################
    # Controls the Visibility of all the 4 Axis and Text on it
    # Controls Visibility of Text
    plot20 = win.addPlot(row=row+2, col=column)
    plot20.getAxis('left').setStyle(showValues=True)
    plot20.getAxis('right').setStyle(showValues=False)
    plot20.getAxis('top').setStyle(showValues=False)
    plot20.getAxis('bottom').setStyle(showValues=True)
    # Controls Visibility of Axis
    plot20.showAxis('right', show=True)
    plot20.showAxis('top', show=False)
    plot20.showAxis('left', show=True)
    plot20.showAxis('bottom', show=True)

    plot20.addLegend() # Add a legend to the plot
    plot20_1 = plot20.plot([], pen=mkPen('g', width=3), name='CE IVs') # Add green line for CE OTMs (empty data)
    plot20_2 = plot20.plot([], pen=mkPen('y', width=3), name='PE IVs') # Add yellow line for PE OTMs (empty data)
    #-------------------------------------------------------------------------------------------------
    vplot20 = pg.ViewBox()
    plot20.scene().addItem(vplot20)
    plot20.getAxis('right').linkToView(vplot20)
    vplot20.setXLink(plot20)

    vplot20_1 = pg.PlotDataItem(pen=mkPen('g', width=3, style=QtCore.Qt.DotLine), name='CE Delta')
    vplot20_2 = pg.PlotDataItem(pen=mkPen('y', width=3, style=QtCore.Qt.DotLine), name='PE Delta')
    vplot20.addItem(vplot20_1)
    vplot20.addItem(vplot20_2)

    plot20.legend.addItem(vplot20_1, vplot20_1.name())
    plot20.legend.addItem(vplot20_2, vplot20_2.name())

    def update_vplot20_geometry():
        vplot20.setGeometry(plot20.getViewBox().sceneBoundingRect())
    plot20.getViewBox().sigResized.connect(update_vplot20_geometry)
    #--------------------------------------------------------------------------------------------------
    vvplot20 = pg.ViewBox()
    axis20B = pg.AxisItem('right')
    axis20B.setVisible(False)
    axis20B.setStyle(showValues=False)
    plot20.layout.addItem(axis20B, 2, 3)
    axis20B.linkToView(vvplot20)
    vvplot20.setXLink(plot20)
    plot20.scene().addItem(vvplot20)

    vvplot20_1 = pg.PlotDataItem(pen=mkPen('c', width=3), name='CE BUY Pressure')
    vvplot20_2 = pg.PlotDataItem(pen=mkPen('m', width=3), name='PE BUY Pressure')
    vvplot20.addItem(vvplot20_1)
    vvplot20.addItem(vvplot20_2)
    plot20.legend.addItem(vvplot20_1, vvplot20_1.name())
    plot20.legend.addItem(vvplot20_2, vvplot20_2.name())

    def update_vvplot20_geometry():
        vvplot20.setGeometry(plot20.getViewBox().sceneBoundingRect())
    plot20.getViewBox().sigResized.connect(update_vvplot20_geometry)
    #--------------------------------------------------------------------------------------------------
    font = QFont("Arial", 10)    # 14 = bigger text
    font.setBold(True)           # optional

    text00 = pg.TextItem('', color='w', anchor=(0.5, 0.5))
    text00.setFont(font)
    plot00.addItem(text00)

    text10 = pg.TextItem('', color='w', anchor=(0.5, 0.5))
    text10.setFont(font)
    plot10.addItem(text10)

    text20 = pg.TextItem('', color='w', anchor=(0.5, 0.6))
    text20.setFont(font)
    plot20.addItem(text20)

    xx = locals()
    return xx

def one_time_index_straddle():
    ########################################################################################################
    # Controls the Visibility of all the 4 Axis and Text on it
    # Controls Visibility of Text
    var = {}

    font = QFont("Arial", 10)    # 14 = bigger text
    font.setBold(True)           # optional

    for i in range(0,3):
        for j in range(0,3):
            var[f'plot{i}{j}'] = win_st.addPlot(row=i, col=j)

            var[f'plot{i}{j}'].getAxis('left').setStyle(showValues=True)
            var[f'plot{i}{j}'].getAxis('right').setStyle(showValues=False)
            var[f'plot{i}{j}'].getAxis('top').setStyle(showValues=False)
            var[f'plot{i}{j}'].getAxis('bottom').setStyle(showValues=True)

            # Controls Visibility of Axis
            var[f'plot{i}{j}'].showAxis('right', show=True)
            var[f'plot{i}{j}'].showAxis('top', show=False)
            var[f'plot{i}{j}'].showAxis('left', show=True)
            var[f'plot{i}{j}'].showAxis('bottom', show=True)

            var[f'plot{i}{j}'].addLegend() # Add a legend to the plot
            var[f'plot{i}{j}_1'] = var[f'plot{i}{j}'].plot([], pen=mkPen('r', width=3), name='VWAP') # Add green line for CE OTMs (empty data)
            var[f'plot{i}{j}_2'] = var[f'plot{i}{j}'].plot([], pen=mkPen('w', width=3), name='Straddle' if i == 1 else 'PE OTM' if i == 0 else 'CE OTM')


            var[f'text{i}{j}'] = pg.TextItem('', color='w', anchor=(0.5, 0.5))
            var[f'text{i}{j}'].setFont(font)
            var[f'plot{i}{j}'].addItem(var[f'text{i}{j}'])

    return var

def one_time():

    xx_nifty = one_time_index(0, 0)
    xx_bnf = one_time_index(0, 1)
    xx_sensex = one_time_index(0, 2)

    xx_straddle = one_time_index_straddle()

    return [xx_nifty, xx_bnf, xx_sensex, xx_straddle]

def auto_scale_and_text(plot, vb_right, vb_third, x, y1, y2, y3, y4, y5, y6, text_item, text_string, disp_range):
    """
    Handles:
    - Set X range
    - Auto Y range for all axes (main, right, and optional third)
    - Keep text on top
    """

    # STEP-1: Set X range
    plot.setXRange(x[disp_range], x[-1], padding=0.02)

    # STEP-2: Visible region mask
    x_min, x_max = plot.viewRange()[0]
    mask = (x >= x_min) & (x <= x_max)

    # STEP-3: Main axis autoscale
    all_main = np.concatenate([y1.values[mask], y2.values[mask]])
    ymin = np.nanmin(all_main); ymax = np.nanmax(all_main)
    ymax += (ymax - ymin) * 0.15
    plot.getViewBox().setYRange(ymin, ymax)

    # STEP-4: Right axis autoscale
    all_right = np.concatenate([y3.values[mask], y4.values[mask]])
    
    if np.all(np.isnan(all_right)):
        pass     # skip autoscale when no valid data
    else:
        ymin_r = np.nanmin(all_right)
        ymax_r = np.nanmax(all_right)
        ymax_r += (ymax_r - ymin_r) * 0.15
        vb_right.setYRange(ymin_r, ymax_r)

    # STEP-5: Third axis autoscale (only if provided)
    if vb_third is not None and y5 is not None and y6 is not None:
        all_third = np.concatenate([y5.values[mask], y6.values[mask]])
        ymin_b = np.nanmin(all_third); ymax_b = np.nanmax(all_third)
        ymax_b += (ymax_b - ymin_b) * 0.15
        vb_third.setYRange(ymin_b, ymax_b)

    # STEP-6: Update text and keep it on top
    text_item.setText(text_string)
    xr, yr = plot.viewRange()
    text_item.setPos((xr[0] + xr[1]) / 2, yr[1] - (yr[1] - yr[0]) * 0.08)

def update_each_index(xx, df, x_data_qty, dfs):

    ns = SimpleNamespace(**xx)

    x00 = df.index
    y00_1 = df['ce_ltp_change']
    y00_2 = df['pe_ltp_change']
    y00_3 = df['ce_oi_change']
    y00_4 = df['pe_oi_change']

    # y00_5 = df['ce_delta_sum']
    # y00_6 = df['pe_delta_sum']

    today = df['today'].iloc[-1].date()
    expiry = df['expiry'].iloc[-1].date()
    dte = (expiry - today).days
    inst_index = df['index'].iloc[-1].upper()

    time = df['timestamp'].iloc[-1].time().replace(microsecond=0)
    vix = df['India_Vix'].iloc[-1]
    IVP = df['IVP'].iloc[-1]
    ch_ce_oi = df['ce_oi_change'].iloc[-1]
    format_ch_ce_oi = format_oi(df['ce_oi_change'].iloc[-1])
    ch_pe_oi = df['pe_oi_change'].iloc[-1]
    format_ch_pe_oi = format_oi(df['pe_oi_change'].iloc[-1])
    pc = round(ch_pe_oi/ch_ce_oi,2) if ch_ce_oi != 0 else 0
    ce_oi = df['ce_oi_sum'].iloc[-1]
    format_ce_oi = format_oi(df['ce_oi_sum'].iloc[-1])
    pe_oi = df['pe_oi_sum'].iloc[-1]
    format_pe_oi = format_oi(df['pe_oi_sum'].iloc[-1])
    pcr = round(pe_oi/ce_oi,2) if ce_oi != 0 else 0
    text00t = f'{time} | Vix: {vix} | IVP: {IVP} | T: {today} | {inst_index} | E: {expiry} | DTE: {dte}\n  CE: {format_ce_oi}, PE: {format_pe_oi}, PCR: {pcr} | ΔCE: {format_ch_ce_oi}, ΔPE: {format_ch_pe_oi}, P/C: {pc}'

    ns.plot00_1.setData(x00, y00_1)
    ns.plot00_2.setData(x00, y00_2)

    ns.vplot00_1.setData(x00,y00_3)
    ns.vplot00_2.setData(x00,y00_4)

    # ns.vvplot00_1.setData(x00, y00_5)
    # ns.vvplot00_2.setData(x00, y00_6)
    abc = int(x_data_qty)
    disp_range = -abc

    auto_scale_and_text(ns.plot00, ns.vplot00, ns.vvplot00, x00, y00_1, y00_2, y00_3, y00_4, None, None, ns.text00, text00t, disp_range) # (enable later if y00_5,y00_6 added in place on None)

    ############################################################################################################
    atm_strike = float(df['strike'].iloc[-1])

    all_strike = [int(float(x)) for x in dfs.keys()]
    position_strike = all_strike.index(int(atm_strike))+1

    x10 = dfs[f'{atm_strike}'].index
    y10_1 = dfs[f'{atm_strike}']['straddle_ltp']
    y10_2 = dfs[f'{atm_strike}']['straddle_vwap']

    y10_3 = dfs[f'{atm_strike}']['obv_CE']
    y10_4 = dfs[f'{atm_strike}']['obv_PE']

    # y10_5 = df['ce_obv']
    # y10_6 = df['pe_obv']

    ce_ltp = dfs[f'{atm_strike}']['ltp_CE'].iloc[-1]
    pe_ltp = dfs[f'{atm_strike}']['ltp_PE'].iloc[-1]
    ce_pe = (ce_ltp + pe_ltp)
    ce_ltp_init = dfs[f'{atm_strike}']['ltp_CE'].iloc[0]
    pe_ltp_init = dfs[f'{atm_strike}']['ltp_PE'].iloc[0]
    ce_pe_init = (ce_ltp_init + pe_ltp_init)
    change_per = (ce_pe - ce_pe_init)/ce_pe_init*100
    ce_obv = dfs[f'{atm_strike}']['obv_CE'].iloc[-1]
    pe_obv = dfs[f'{atm_strike}']['obv_PE'].iloc[-1]
    text10t = f'{ce_ltp:.2f} + {pe_ltp:.2f} = {ce_pe:.2f} ({ce_pe_init:.2f}) | {(ce_pe-ce_pe_init):.2f} ({change_per:.2f} %)\nCE OBV: {ce_obv/1000:.2f} | PE OBV: {pe_obv/1000:.2f} | {int(atm_strike)} Position: {position_strike}/{len(all_strike)}'

    ns.plot10_1.setData(x10, y10_1)
    ns.plot10_2.setData(x10, y10_2)

    ns.vplot10_1.setData(x10,y10_3)
    ns.vplot10_2.setData(x10,y10_4)

    # ns.vvplot10_1.setData(x10,y10_5)
    # ns.vvplot10_2.setData(x10,y10_6)

    auto_scale_and_text(ns.plot10, ns.vplot10, ns.vvplot10, x10, y10_1, y10_2, y10_3, y10_4, None, None, ns.text10, text10t, disp_range)

    #--------------------------------------------------------------------------------------------------------------------------
    x20 = df.index
    y20_1 = df['ce_iv_avg']
    y20_2 = df['pe_iv_avg']

    y20_3 = df['ce_delta_sum']
    y20_4 = df['pe_delta_sum']

    y20_5 = df['ce_buy_pressure']
    y20_6 = df['pe_buy_pressure']

    spot = df['spot'].iloc[-1]
    synth_atm = df['strike'].iloc[-1]
    ce_iv = df['ce_iv_avg'].iloc[-1]
    pe_iv = df['pe_iv_avg'].iloc[-1]
    ce_prs = df['ce_buy_pressure'].iloc[-1]
    pe_prs = df['pe_buy_pressure'].iloc[-1]
    text20t = f'Spot: {spot} | Synth ATM: {synth_atm} | CE IV : {ce_iv:.2f}, PE IV : {pe_iv:.2f}\nCE Pr: {ce_prs:.2f}, PE Pr: {pe_prs:.2f}'

    ns.plot20_1.setData(x20, y20_1)
    ns.plot20_2.setData(x20, y20_2)

    ns.vplot20_1.setData(x20,y20_3)
    ns.vplot20_2.setData(x20,y20_4)

    ns.vvplot20_1.setData(x20, y20_5)
    ns.vvplot20_2.setData(x20, y20_6)

    auto_scale_and_text(ns.plot20, ns.vplot20, ns.vvplot20, x20, y20_1, y20_2, y20_3, y20_4, y20_5, y20_6, ns.text20, text20t, disp_range)

def update_straddle(index, var, df_strike, atm):

    if index not in ['nifty', 'bnf', 'sensex']:
        for i in range(0,3):
            for j in range(0,3):
                var[f'plot{i}{j}_1'].setData()
                var[f'plot{i}{j}_2'].setData()
    else:

        straddle_list = list(df_strike.keys())

        try:
            atm_manual = sht_summary.range('C11').value
            atm_manual = int(atm_manual)
            if atm_manual > 0 and str(float(atm_manual)) in straddle_list:
                atm = atm_manual
        except (TypeError, ValueError):
            pass

        strikes_float = sorted(float(k) for k in df_strike.keys())
        atm_float = float(atm)
        atm_index = strikes_float.index(atm_float)
        atm_strike = str(strikes_float[atm_index])
        pe_otm_strike = [str(x) for x in strikes_float[atm_index-3 : atm_index]]
        ce_otm_strike = [str(x) for x in strikes_float[atm_index+1 : atm_index+4]]

        x = df_strike[atm_strike].index

        for j in range(0,3):
            i = 1

            y_vwap = df_strike[atm_strike]['ltp_PE_vwap'] if j==0 else df_strike[atm_strike]['straddle_vwap'] if j==1 else  df_strike[atm_strike]['ltp_CE_vwap']
            y_ltp  = df_strike[atm_strike]['ltp_PE'] if j==0 else df_strike[atm_strike]['straddle_ltp'] if j==1 else  df_strike[atm_strike]['ltp_CE']

            var[f'plot{i}{j}_1'].setData(x, y_vwap)
            var[f'plot{i}{j}_2'].setData(x, y_ltp)

            var[f'plot{i}{j}'].setXRange(x[0], x[-1], padding=0.03)

            ymin = min(y_vwap.min(), y_ltp.min())
            ymax = max(y_vwap.max(), y_ltp.max())
            pad = (ymax - ymin) * 0.1
            var[f'plot{i}{j}'].setYRange(ymin - pad, ymax + pad)

            init = df_strike[atm_strike]['ltp_PE'].iloc[0] if j==0 else df_strike[atm_strike]['straddle_ltp'].iloc[0] if j==1 else  df_strike[atm_strike]['ltp_CE'].iloc[0]
            latest = df_strike[atm_strike]['ltp_PE'].iloc[-1] if j==0 else df_strike[atm_strike]['straddle_ltp'].iloc[-1] if j==1 else  df_strike[atm_strike]['ltp_CE'].iloc[-1]

            text_string = f'{index.upper()} | {atm_strike} | LTP: {latest:.2f} | Initial: {init:.2f} | Decay: {(latest - init):.2f} | Change: {(latest - init)/init*100:.2f} %'
            var[f'text{i}{j}'].setText(text_string)
            xr, yr = var[f'plot{i}{j}'].viewRange()
            var[f'text{i}{j}'].setPos(
                (xr[0] + xr[1]) / 2,
                yr[1] - (yr[1] - yr[0]) * 0.08)
            

        if len(pe_otm_strike) == 3:
            for j, strike in enumerate(pe_otm_strike):
                i=0

                pe_otm_vwap = df_strike[strike]['ltp_PE_vwap']
                pe_otm_ltp  = df_strike[strike]['ltp_PE']

                var[f'plot{i}{j}_1'].setData(x, pe_otm_vwap)
                var[f'plot{i}{j}_2'].setData(x, pe_otm_ltp)

                var[f'plot{i}{j}'].setXRange(x[0], x[-1], padding=0.03)

                ymin = min(pe_otm_vwap.min(), pe_otm_ltp.min())
                ymax = max(pe_otm_vwap.max(), pe_otm_ltp.max())
                pad = (ymax - ymin) * 0.1
                var[f'plot{i}{j}'].setYRange(ymin - pad, ymax + pad)

                pe_init = df_strike[strike]['ltp_PE'].iloc[0]
                pe_latest = df_strike[strike]['ltp_PE'].iloc[-1]

                text_string = f'{index.upper()} | {strike} | PE OTM: {pe_latest:.2f} | Initial: {pe_init:.2f} | Decay: {(pe_latest - pe_init):.2f} | Change: {(pe_latest - pe_init)/pe_init*100:.2f} %'
                var[f'text{i}{j}'].setText(text_string)
                xr, yr = var[f'plot{i}{j}'].viewRange()
                var[f'text{i}{j}'].setPos(
                    (xr[0] + xr[1]) / 2,
                    yr[1] - (yr[1] - yr[0]) * 0.08)
        else:
            i=0
            for j in range(0,3):
                var[f'plot{i}{j}_1'].setData()
                var[f'plot{i}{j}_2'].setData()


        if len(ce_otm_strike) == 3:
            for j, strike in enumerate(ce_otm_strike):
                i=2

                ce_otm_vwap = df_strike[strike]['ltp_CE_vwap']
                ce_otm_ltp  = df_strike[strike]['ltp_CE']

                var[f'plot{i}{j}_1'].setData(x, ce_otm_vwap)
                var[f'plot{i}{j}_2'].setData(x, ce_otm_ltp)

                var[f'plot{i}{j}'].setXRange(x[0], x[-1], padding=0.03)

                ymin = min(ce_otm_vwap.min(), ce_otm_ltp.min())
                ymax = max(ce_otm_vwap.max(), ce_otm_ltp.max())
                pad = (ymax - ymin) * 0.1
                var[f'plot{i}{j}'].setYRange(ymin - pad, ymax + pad)

                ce_init = df_strike[strike]['ltp_CE'].iloc[0]
                ce_latest = df_strike[strike]['ltp_CE'].iloc[-1]

                text_string = f'{index.upper()} | {strike} | CE OTM: {ce_latest:.2f} | Initial: {ce_init:.2f} | Decay: {(ce_latest - ce_init):.2f} | Change: {(ce_latest - ce_init)/ce_init*100:.2f} %'
                var[f'text{i}{j}'].setText(text_string)
                xr, yr = var[f'plot{i}{j}'].viewRange()
                var[f'text{i}{j}'].setPos(
                    (xr[0] + xr[1]) / 2,
                    yr[1] - (yr[1] - yr[0]) * 0.08)
        else:
            i=2
            for j in range(0,3):
                var[f'plot{i}{j}_1'].setData()
                var[f'plot{i}{j}_2'].setData()



def smooth_straddle_strike(var, data_strike, index_atm):

    nifty_df_strike = data_strike['nifty']
    bnf_df_strike = data_strike['bnf']
    sensex_df_strike = data_strike['sensex']

    index_list_strike = [nifty_df_strike, bnf_df_strike, sensex_df_strike]

    for i in range(0,3):
        for key, value in index_list_strike[i].items():
            value['ltp_CE'] = pd.Series(value['ltp_CE']).ewm(span=100, adjust=False).mean()
            value['ltp_PE'] = pd.Series(value['ltp_PE']).ewm(span=100, adjust=False).mean()
            value['straddle_ltp'] = pd.Series(value['straddle_ltp']).ewm(span=50, adjust=False).mean()
            value['straddle_vwap'] = pd.Series(value['straddle_vwap']).ewm(span=50, adjust=False).mean()
            value['obv_CE'] = pd.Series(value['obv_CE']).ewm(span=20, adjust=False).mean()
            value['obv_PE'] = pd.Series(value['obv_PE']).ewm(span=20, adjust=False).mean()
            value['ltp_CE_vwap'] = pd.Series(value['ltp_CE_vwap']).ewm(span=50, adjust=False).mean()
            value['ltp_PE_vwap'] = pd.Series(value['ltp_PE_vwap']).ewm(span=50, adjust=False).mean()

    focus = sht_summary.range('C10').value
    if focus == 'nifty':
        update_straddle('nifty', var, nifty_df_strike, index_atm['nifty'])
    elif focus == 'bnf':
        update_straddle('bnf', var, bnf_df_strike, index_atm['bnf'])
    elif focus == 'sensex':
        update_straddle('sensex', var, sensex_df_strike, index_atm['sensex'])
    else:
        update_straddle('blank', var, sensex_df_strike, index_atm['sensex'])

def update(xx, data, x_data_qty, data_strike):
    nifty_df = data['nifty']
    bnf_df = data['bnf']
    sensex_df = data['sensex']

    nifty_atm = nifty_df['strike'].iloc[-1]
    bnf_atm = bnf_df['strike'].iloc[-1]
    sensex_atm = sensex_df['strike'].iloc[-1]

    index_list = [nifty_df, bnf_df, sensex_df]
    index_atm = {'nifty':nifty_atm, 'bnf':bnf_atm, 'sensex':sensex_atm}

    for i in range(0,3):
        index_list[i]['ce_ltp_change'] = pd.Series(index_list[i]['ce_ltp_change']).ewm(span=200, adjust=False).mean()
        index_list[i]['pe_ltp_change'] = pd.Series(index_list[i]['pe_ltp_change']).ewm(span=200, adjust=False).mean()
        index_list[i]['ce_oi_change'] = pd.Series(index_list[i]['ce_oi_change'] ).ewm(span=200, adjust=False).mean()
        index_list[i]['pe_oi_change'] = pd.Series(index_list[i]['pe_oi_change']).ewm(span=200, adjust=False).mean()
        index_list[i]['ce_delta_sum'] = pd.Series(index_list[i]['ce_delta_sum']).ewm(span=100, adjust=False).mean()
        index_list[i]['pe_delta_sum'] = pd.Series(index_list[i]['pe_delta_sum']).ewm(span=100, adjust=False).mean()
        index_list[i]['ce_buy_pressure'] = pd.Series(index_list[i]['ce_buy_pressure']).ewm(span=50, adjust=False).mean()
        index_list[i]['pe_buy_pressure'] = pd.Series(index_list[i]['pe_buy_pressure']).ewm(span=50, adjust=False).mean()
        index_list[i]['ce_iv_avg'] = pd.Series(index_list[i]['ce_iv_avg']).ewm(span=100, adjust=False).mean()
        index_list[i]['pe_iv_avg'] = pd.Series(index_list[i]['pe_iv_avg']).ewm(span=100, adjust=False).mean()

    ###############################################

    nifty_df_strike = data_strike['nifty']
    bnf_df_strike = data_strike['bnf']
    sensex_df_strike = data_strike['sensex']

    index_list_strike = [nifty_df_strike, bnf_df_strike, sensex_df_strike]

    for i in range(0,3):
        for key, value in index_list_strike[i].items():
            atm = int(float((key)))
            if atm in [nifty_atm, bnf_atm, sensex_atm]:
                value['ltp_CE'] = pd.Series(value['ltp_CE']).ewm(span=100, adjust=False).mean()
                value['ltp_PE'] = pd.Series(value['ltp_PE']).ewm(span=100, adjust=False).mean()
                value['straddle_ltp'] = pd.Series(value['straddle_ltp']).ewm(span=50, adjust=False).mean()
                value['straddle_vwap'] = pd.Series(value['straddle_vwap']).ewm(span=50, adjust=False).mean()
                value['obv_CE'] = pd.Series(value['obv_CE']).ewm(span=20, adjust=False).mean()
                value['obv_PE'] = pd.Series(value['obv_PE']).ewm(span=20, adjust=False).mean()

    update_each_index(xx[0], nifty_df, x_data_qty, nifty_df_strike)
    update_each_index(xx[1], bnf_df, x_data_qty, bnf_df_strike)
    update_each_index(xx[2], sensex_df, x_data_qty, sensex_df_strike)

    smooth_straddle_strike(xx[3], data_strike, index_atm)

def update_option_list():
    global sub_list
    global old_synth_atm
    global sub_list_ce, sub_list_pe, inst_strike_pair, index_ce_pe_list
    interval = datetime.now()
    minute = interval.minute
    sec = interval.second

    if (minute % 5 == 0) and (sec == 1):
        print('I entered here - 5min zone')
        new_synth_atm = synth_atm_index()
        if new_synth_atm != old_synth_atm:

            old_sub = sub_list
            sub_list_ce, sub_list_pe, sub_list, inst_strike_pair, index_ce_pe_list = valid_strikes(new_synth_atm)
            new_sub = sub_list

            unsubscribe_list = list(set(old_sub) - set(new_sub))
            subscribe_list = list(set(new_sub) - set(old_sub))


            if unsubscribe_list:
                streamer.unsubscribe(unsubscribe_list)
                print("Unsubscribed:", unsubscribe_list)
            
            if subscribe_list:
                streamer.subscribe(subscribe_list, "full")
                print("Subscribed:", subscribe_list)

            old_synth_atm = new_synth_atm.copy()
            print('I updated the subscription list')
        time.sleep(1)

def show_only(index_id):
    # index_id: 0 = NIFTY, 1 = BNF, 2 = SENSEX
    for i in range(3):
        if i == index_id:
            xx[i]['plot00'].show()
            xx[i]['plot10'].show()
            xx[i]['plot20'].show()
        else:
            xx[i]['plot00'].hide()
            xx[i]['plot10'].hide()
            xx[i]['plot20'].hide()

def show_all():
    for i in range(3):
        xx[i]['plot00'].show()
        xx[i]['plot10'].show()
        xx[i]['plot20'].show()

def focus_index():
    focus = sht_summary.range('C9').value
    if focus == 'nifty':
        show_only(0)
    elif focus == 'bnf':
        show_only(1)
    elif focus == 'sensex':
        show_only(2)
    else:
        show_all()

one=True
xx=None
speed=1000
def call():
    start = time.time()
    t_time = datetime.now().time().replace(microsecond=0)
    global one, xx, sub_list, index_key, index_ce_pe_list, nifty_expiry, bnf_expiry, sensex_expiry, speed
    interval = datetime.now()
    minute = interval.minute
    sec = interval.second

    with lock:
        df = pd.DataFrame(data_base).T

    # ✅ Attempt to convert all columns to numeric types (int/float) where possible. If conversion fails (e.g., for text or categorical columns like 'type'), the exception is caught and that column is left unchanged as an object type.
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            # leave non-numeric columns as they are
            pass

    df = df[df.index.isin(sub_list+index_key)]

    df_nifty_option = option_chain(ce=index_ce_pe_list[0], pe=index_ce_pe_list[1], df=df, expiry=nifty_expiry[0], index='nifty')
    df_bnf_option = option_chain(ce=index_ce_pe_list[2], pe=index_ce_pe_list[3], df=df, expiry=bnf_expiry[0], index = 'bnf')
    df_sensex_option = option_chain(ce=index_ce_pe_list[4], pe=index_ce_pe_list[5], df=df, expiry=sensex_expiry[0], index = 'sensex')

    if sec in [1,2,3]:
        with open(f'Credentials/Data/{tdate}/{tdate}_raw_data.pkl', 'wb') as fw:
            pickle.dump(structure, fw)
        with open(f'Credentials/Data/{tdate}/{tdate}_raw_data_strike.pkl', 'wb') as fw:
            pickle.dump(structure_strike, fw)

    final_plot_data = final_data_prep(structure)
    final_plot_data_strike = final_data_prep_strike(structure_strike)
    # plot_graph(final_plot_data)

    if one:
        xx = one_time()
        one=False

    focus_index()

    sht_summary.range('C3').value = len(final_plot_data['nifty'].index)
    x_data_qty = sht_summary.range('C2').value
    if x_data_qty > sht_summary.range('C3').value:
        x_data_qty = 0

    update(xx, final_plot_data, x_data_qty, final_plot_data_strike)

    update_option_list()

    update_OC = sht_summary.range('C5').value
    
    if (update_OC==1):
        sht_nifty.range('A1').value = df_nifty_option
        sht_bnf.range('A1').value = df_bnf_option
        sht_sensex.range('A1').value = df_sensex_option
        speed = int(sht_summary.range('C7').value*1000)

    end = time.time()
    sht_summary.range('C6').value = end-start

    fs1 = sht_summary.range('C8').value
    fs2 = sht_summary.range('C12').value

    if (fs1 is not None) or (fs2 is not None):
        if fs1==1:
            main.showFullScreen()
            sht_summary.range('C8').value = None
        elif fs1==0:
            main.showMaximized()
            sht_summary.range('C8').value = None
        elif fs2==1:
            main_st.showFullScreen()
            sht_summary.range('C12').value = None
        elif fs2==0:
            main_st.showMaximized()
            sht_summary.range('C12').value = None

    exit_condition = str(sht_summary.range('C4').value).lower().strip()

    if exit_condition == 'e' or t_time > end_time:
        print("Exiting...")

        exporter = ImageExporter(win.scene())
        exporter.parameters()['width'] = 1800  # Optional: Set resolution
        exporter.export(f"Credentials/Data/{tdate}/{tdate}_plot_snapshot.jpg")
        print(f"\n\nPlot saved as plot_snapshot.jpg")
        if t_time > end_time:
            print(f'\rMarket Closed at : {end_time}, Current Time : {t_time} | Program Autoclosed', end='', flush=True)
        if exit_condition=='e':
            print(f'\nProgram Closed Manually at : {t_time} from Excel')

        streamer.disconnect()      # stop websocket
        sht_summary.range('C4').value = None
        sht_summary.range('C2').value = 0
        sht_summary.range('C5').value = 1
        sht_summary.range('C7').value = 1
        wb.save()
        wb.close()
        app.quit()

        if t_time > end_time:
            os.system("shutdown /s /t 300")
            print("\nShutdown scheduled in 300 seconds...")
            print("(Press ANY key to CANCEL)\n")

            for remaining in range(300, 0, -1):
                # Display countdown on same line
                print(f"\rShutdown in: {remaining:2d} seconds (Press ANY key to cancel)", end="", flush=True)

                # Wait 1 second
                for _ in range(10):
                    time.sleep(0.1)
                    if msvcrt.kbhit():
                        os.system("shutdown /a")
                        print("\n\nShutdown CANCELED by user.")
                        return
            print("\n\nShutdown will proceed...")
            return
        return

    QTimer.singleShot(speed, call)   # next run only if NOT exiting

main.showMaximized()
main_st.showMaximized()
# main_st.hide()
# main_st.close()
QTimer.singleShot(0, call)
sys.exit(app.exec_())
