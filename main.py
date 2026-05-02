import platform, psutil
from time import sleep
from utils import scan_ips, get_local_ip, send_message_to_server
from colorama import Fore, Back, Style
import json

HOST = "0.0.0.0"  # all interfaces
PORT = 65535 # network discovery port

import asyncio

async def handle_client(reader, writer):
    # This runs whenever a client connects
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")
    if message == "ping":
        print("Sending: pong")
        writer.write(b"pong")
        await writer.drain()
    elif message == "info":
        print("Getting info")
        mem = psutil.virtual_memory()
        
        msg = {
            "os": f"{platform.system()}|{platform.release()}|{platform.version()}",
            "cpu": f"{platform.processor()}|{psutil.cpu_percent(1)}",
            "mem": f"{mem.total}|{mem.used}|{mem.percent}"
        }
        msg_s = json.dumps(msg)

        msg_b = bytes(msg_s, "utf-8")
        writer.write(msg_b)
        await writer.drain()
    else:
        writer.write(b"a")
        await writer.drain()

    print("Closing the connection")
    writer.close()
    await writer.wait_closed()

async def start_listener():
    # Start the server
    server = await asyncio.start_server(handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

async def main():
    # Start the listener in the background
    listener_task = asyncio.create_task(start_listener())

    # Now your "Network Discovery Tool" logic runs here
    print(f"{Fore.GREEN}Network Discovery Tool{Fore.RESET}")
    print("Scan for other devices? (Y/n)")
    yes = input()
    if yes.lower() == "n" or yes.lower() == "no":
        # Keep the script alive
        await listener_task
    else:
        user_ip = get_local_ip()
        network_prefix_l = user_ip.split(".")[:-1]
        network_prefix = ""
        for value in network_prefix_l:
            network_prefix += value
            network_prefix += "."
        
        ips = scan_ips(network_prefix[:-1], PORT)
        if len(ips) == 0:
            print("No Devices found using network discovery tool")
        print(f"{Fore.CYAN}ONLINE DEVICES:{Fore.RESET}")
        for ip in ips:
            print(ip)
        print("\nWhich IP to get info about?")
        selected_ip = input()
        if selected_ip not in ips:
            print("IP not in the list")
            return

        data = send_message_to_server(selected_ip, PORT, "info")
        if data["sent"] != 4:
            # info wasnt sent fully
            print(f"{Fore.RED}Couldnt send request to server{Fore.RESET}")
            return
        
        server_data = json.loads(data["r"])
        os_info = server_data["os"].split("|")
        cpu_info = server_data["cpu"].split("|")
        mem_info = server_data["mem"].split("|")
        print(f"OS: {os_info[0]}")
        print(f"OS Release: {os_info[1]}")
        print(f"OS Version: {os_info[2]}")
        print("--------")
        print(f"CPU: {cpu_info[0]}")
        print(f"CPU Usage: {cpu_info[1]}%")
        print("--------")
        print(f"Memory Total: {mem_info[0]}")
        print(f"Memory Used: {mem_info[1]}")
        print(f"Memory Free: {mem_info[2]}%")

asyncio.run(main())