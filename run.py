import base64
import random
import socket
import websockets
import json
import time
import asyncio

import requests  # Tambahkan ini di bagian import
import time
from datetime import datetime
import argparse


def read_serial_from_file(filename):
    serial_list = []
    with open(filename, 'r') as file:
        for line in file:
            serial_list.append(line.strip())
    return serial_list

serial_file = "serial.txt"
serial_list = read_serial_from_file(serial_file)

async def process_subprotocol(subprotocol, uri, headers, cek_boost):
    try:
        async with websockets.connect(uri, extra_headers=headers, subprotocols=[subprotocol]) as ws:
            try:
                message = await ws.recv()
                data = json.loads(message)
                if data.get("action") == "user":
                    # Proses data pengguna
                    print(f"Connected", end="", flush=True)
                    print()
                    time.sleep(2)
                    user_data = data.get("data", {})
                    username = user_data.get("username", "Username not found")
                    nama = f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip()
                    energy = user_data.get("energy", 0)
                    free_turbo = user_data.get("freeTurbo", 0)
                    free_energy_regeneration = user_data.get("freeEnergyRegeneration", 0)
                    balance = user_data.get("balance", 0)
                    print(f"{username}", flush=True)
                    formatted_balance = f"{balance}".replace(",", ".")
                    print(f"Balance     : {formatted_balance}")
                    print(f"Energy      : {energy}")
                    print(f"Free Turbo  : {free_turbo}")
                    print(f"Free Energy : {free_energy_regeneration}")

                    if cek_boost == 'y':
                        if energy < 100 and free_energy_regeneration > 0:
                            response = requests.put(
                                'https://api.prick.lol/v1/boost/energy-regeneration',
                                headers={
                                    'Authorization': f'Bearer {subprotocol}',  # asumsi subprotocol adalah token
                                    'Content-Length': '0',
                                    'User-Agent': headers['User-Agent'],
                                    'Origin': headers['Origin']
                                }
                            )
                            if response.status_code == 200:
                                print(f"Energy Boost  : Active", flush=True)
                            else:
                                print(f"Energy Boost  : Failed", flush=True)

                            # Aktifkan turbo jika energi berhasil diperbarui
                            if response.json().get("result", {}).get("energy", 0) > 0:
                                turbo_response = requests.put(
                                    'https://api.prick.lol/v1/boost/turbo',
                                    headers={
                                        'Authorization': f'Bearer {subprotocol}',
                                        'Content-Length': '0',
                                        'User-Agent': headers['User-Agent'],
                                        'Origin': headers['Origin']
                                    }
                                )
                                if turbo_response.status_code == 200:
                                    print(f"Turbo Boost  : Active", flush=True)
                                else:
                                    print(f"Turbo Boost  : Failed", flush=True)

                    # Mengirim pesan tap
                    waktu_sekarang = int(time.time() * 1000)
                    taps = [waktu_sekarang + i * 140 for i in range(200)]
                    tap_message = {
                        "action": "tap",
                        "data": taps
                    }
                    await ws.send(json.dumps(tap_message))

                    try:
                        response_message = await asyncio.wait_for(ws.recv(), timeout=20)  # Meningkatkan timeout menjadi 20 detik
                        response_data = json.loads(response_message)
                        if 'userClicks' in response_data and 'energy' in response_data and 'balance' in response_data:
                            # formatted_balance = f"{response_data['balance']:,}".replace(",", ".")
                            print(f"Clicked : {response_data['userClicks']} | {response_data['energy']} Energy | {response_data['balance']} Balance", flush=True)
                        else:
                            print(f"{response_data}", flush=True)
                    except asyncio.TimeoutError:
                        print(f"Timeout / Not Active", flush=True)
                    except json.JSONDecodeError:
                        print(f" Error respons JSON", flush=True)
                    except Exception as e:
                        print(f"Error : {e}", flush=True)

            except Exception as e:
                print(f"Error: {e}")
            finally:
                await ws.close()
                print(f"Done")
    except Exception as e:
        print(f"Error: {e}")
    print()

def parse_arguments():
    parser = argparse.ArgumentParser(description='Prick BOT')
    parser.add_argument('--boost', type=str, choices=['y', 'n'], help='use Booster (y/n)')
    args = parser.parse_args()
    if args.boost is None:
        boost_input = input("Use Booster ? (y/n): ").strip().lower()
        args.boost = boost_input if boost_input in ['y', 'n'] else 'n'

    return args

def start_subprotocol_thread(subprotocol, uri, headers):
    asyncio.new_event_loop().run_until_complete(process_subprotocol(subprotocol, uri, headers))

start_time = datetime.now()

def print_welcome_message(serial=None):
    print(r"""
              
            Created By Snail S4NS Group
    find new airdrop & bot here: t.me/sanscryptox
              
          """)
    if serial is not None:
        print(f"Copy, tag bot @SnailHelperBot and paste this key in discussion group t.me/sanscryptox")
        print(f"Your key : {serial}")

def get_serial(current_date, getpcname, name, status):
    formatted_current_date = current_date.strftime("%d-%m-%Y")
    # Encode each value using base64
    getpcname += "knjt"
    name += "knjt"
    encoded_getpcname = base64.b64encode(getpcname.encode()).decode().replace("=", "")
    encoded_current_date = base64.b64encode(formatted_current_date.encode()).decode().replace("=", "")
    encoded_name = base64.b64encode(name.encode()).decode().replace("=", "")
    encoded_status = base64.b64encode(str(status).encode()).decode().replace("=", "")

    # Calculate the length of each encoded value
    getpcname_len = len(encoded_getpcname)
    current_date_len = len(encoded_current_date)
    name_len = len(encoded_name)
    status_len = len(encoded_status)

    # Concatenate the encoded values with their lengths
    serial = "S4NS-"
    serial += str(getpcname_len).zfill(2) + encoded_getpcname
    serial += str(current_date_len).zfill(2) + encoded_current_date
    serial += str(name_len).zfill(2) + encoded_name
    serial += str(status_len).zfill(2) + encoded_status
    return serial

def decode_pc(serial, getpcname, name, current_date):
    try:
        getpcname_len = int(serial[5:7])
        encoded_getpcname = serial[7:7 + getpcname_len]
        current_date_len = int(serial[7 + getpcname_len:9 + getpcname_len])
        encoded_current_date = serial[9 + getpcname_len:9 + getpcname_len + current_date_len]
        name_len = int(serial[9 + getpcname_len + current_date_len:11 + getpcname_len + current_date_len])
        encoded_name = serial[11 + getpcname_len + current_date_len:11 + getpcname_len + current_date_len + name_len]
        status_len = int(serial[11 + getpcname_len + current_date_len + name_len:13 + getpcname_len + current_date_len + name_len])
        encoded_status = serial[13 + getpcname_len + current_date_len + name_len:13 + getpcname_len + current_date_len + name_len + status_len]

        # Decode each value using base64
        decoded_getpcname = base64.b64decode(encoded_getpcname + "==").decode()
        decoded_current_date = base64.b64decode(encoded_current_date + "==").decode()
        decoded_name = base64.b64decode(encoded_name + "==").decode()
        decoded_status = base64.b64decode(encoded_status + "==").decode()
        
        dates = compare_dates(decoded_current_date)

        if decoded_status != '1':
            print("Key Not Generated")
            return None
            
        elif decoded_getpcname.replace("knjt", "") != getpcname:
            print("Different devices registered")
            return None
        
        elif decoded_name.replace("knjt", "") != name:
            print("Different bot registered")
            return None
        
        elif dates > 7:
            print("Key Expired")
            return None
        else:
            print(f"ur key alive until : {decoded_current_date}")
            return dates
    except Exception as e:
        print(f'Key Error : {e}')

def compare_dates(date_str):
    tanggal_compare_dt = datetime.strptime(date_str, '%d-%m-%Y')
    tanggal_now = datetime.now()
    perbedaan_hari = (tanggal_compare_dt - tanggal_now).days
    return perbedaan_hari

def main(decodeds):
    getpcname = socket.gethostname()
    name = "Prickle"
    current_date = datetime.now() # Get the current date
    status = '0'

    uri = "wss://api.prick.lol/ws"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Origin": "https://app.prick.lol",
    }
    
    args = parse_arguments()
    cek_boost = args.boost

    while True:
        # Membaca subprotocols dari file
        with open('tgids.txt', 'r') as file:
            subprotocols = [line.strip() for line in file.readlines()]

        for subprotocol in subprotocols:
            asyncio.new_event_loop().run_until_complete(process_subprotocol(subprotocol, uri, headers, cek_boost))
        
        print("ALL ID DONE")
        print()
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{now} | waiting 60 min")
        time.sleep(3600)
        if decodeds == 0 :
            serial = get_serial(current_date, getpcname, name, status)
            print_welcome_message(serial)
            break

def started():
    getpcname = socket.gethostname()
    name = "Prickle"
    current_date = datetime.now() # Get the current date
    status = '0'

    if len(serial_list) == 0:
        serial = get_serial(current_date, getpcname, name, status)
        print_welcome_message(serial)
    else:
        serial = serial_list[0]
        decodeds = decode_pc(serial, getpcname, name, current_date)
        if decodeds is not None:
            print_welcome_message()
            time.sleep(10)
            main(decodeds)
        else:
            serial = get_serial(current_date, getpcname, name, status)
            print_welcome_message(serial)
            print("Please submit the key to bot for get new key")

if __name__ == "__main__":
    started()
