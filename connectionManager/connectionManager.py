import connectionManager.WSServer as WSServer

import sys
import functools
import asyncio
import signal
import queue 
HOST = "localhost"
PORT = 8990

async def shutdown(loop: asyncio.AbstractEventLoop):
    print("Nacking outstanding tasks")
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task(loop)]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} outstanding tasks")
    if (len(tasks)):  await asyncio.gather(*tasks)
    loop.stop()

async def command_loop(command_queue, *servers):
    loop = asyncio.get_running_loop()
    while True:
        try:
            command = await asyncio.wait_for(loop.run_in_executor(None, 
                functools.partial(command_queue.get, timeout=1)), None)
            print("Command", command)
        except queue.Empty:
            continue

        if (command["cmd"] == "sendall"):
            await asyncio.gather(*[serv.sendall(command['data']) for serv in servers])

def init(command_queue, host=HOST, websocket_port=PORT, rawsocekt_port=PORT + 1):
    loop = asyncio.get_event_loop()
    wsserver = WSServer.WSServer(host, websocket_port, loop)

    try:
        loop.run_until_complete(asyncio.wait([wsserver.run(), command_loop(command_queue, wsserver)]))
        loop.run_forever()
    except KeyboardInterrupt:
        try:
            loop.run_until_complete(shutdown(loop))# start loop for shutdown task
        except Exception as e: #some weird error
            print(e)

    finally:
        loop.close()
        print("connectionManager eventloop has been closed")

    print("Exiting connectionManager")