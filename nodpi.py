# Based on this article https://habr.com/ru/articles/870110/

intro = r"""
$$\     $$\                $$$$$$$$\        $$\
\$$\   $$  |               \__$$  __|       $$ |
 \$$\ $$  /$$$$$$\  $$\   $$\ $$ |$$\   $$\ $$$$$$$\   $$$$$$\
  \$$$$  /$$  __$$\ $$ |  $$ |$$ |$$ |  $$ |$$  __$$\ $$  __$$\
   \$$  / $$ /  $$ |$$ |  $$ |$$ |$$ |  $$ |$$ |  $$ |$$$$$$$$ |
    $$ |  $$ |  $$ |$$ |  $$ |$$ |$$ |  $$ |$$ |  $$ |$$   ____|
    $$ |  \$$$$$$  |\$$$$$$  |$$ |\$$$$$$  |$$$$$$$  |\$$$$$$$\
    \__|   \______/  \______/ \__| \______/ \_______/  \_______|



$$\                                       $$\
$$ |                                      $$ |
$$$$$$$\   $$$$$$\   $$$$$$\   $$$$$$$\ $$$$$$\    $$$$$$\   $$$$$$\
$$  __$$\ $$  __$$\ $$  __$$\ $$  _____|\_$$  _|  $$  __$$\ $$  __$$\
$$ |  $$ |$$ /  $$ |$$ /  $$ |\$$$$$$\    $$ |    $$$$$$$$ |$$ |  \__|
$$ |  $$ |$$ |  $$ |$$ |  $$ | \____$$\   $$ |$$\ $$   ____|$$ |
$$$$$$$  |\$$$$$$  |\$$$$$$  |$$$$$$$  |  \$$$$  |\$$$$$$$\ $$ |
\_______/  \______/  \______/ \_______/    \____/  \_______|\__|

"""


from random import randint
from asyncio import (
    StreamReader,
    StreamWriter,
    start_server,
    create_task,
    run,
    open_connection,
    sleep,
)
import sys
import itertools

BLOCKED = [
    line.strip().encode() for line in open("blacklist.txt", "r", encoding="utf-8")
]
TASKS = []


async def pipe(reader: StreamReader, writer: StreamWriter):
    while not reader.at_eof() and not writer.is_closing():
        try:
            writer.write(await reader.read(1500))
            await writer.drain()
        except:
            break
    writer.close()


async def fragemtn_data(
    local_reader: StreamReader,
    remote_writer: StreamWriter,
):
    head = await local_reader.read(5)
    data = await local_reader.read(1500)
    parts = []
    if all([data.find(site) == -1 for site in BLOCKED]):
        remote_writer.write(head + data)
        await remote_writer.drain()
        return

    while data:
        part_len = randint(1, len(data))
        parts.append(
            bytes.fromhex("1603")
            + bytes([randint(0, 255)])
            + int(part_len).to_bytes(2)
            + data[0:part_len]
        )
        data = data[part_len:]
    remote_writer.write(b"".join(parts))
    await remote_writer.drain()


async def new_conn(
    local_reader: StreamReader,
    local_writer: StreamWriter,
):
    http_data = await local_reader.read(1500)
    try:
        req_type, target = http_data.split(b"\r\n")[0].split(b" ")[0:2]
        host, port = [byte.decode() for byte in target.split(b":")]
    except:
        local_writer.close()
        return
    if req_type != b"CONNECT":
        local_writer.close()
        return
    local_writer.write(b"HTTP/1.1 200 OK\n\n")
    await local_writer.drain()
    try:
        remote_reader, remote_writer = await open_connection(host, port)
    except:
        local_writer.close()
        return

    if port == "443":
        await fragemtn_data(local_reader, remote_writer)

    TASKS.append(create_task(pipe(local_reader, remote_writer)))
    TASKS.append(create_task(pipe(remote_reader, local_writer)))
    while len(TASKS) > 100:
        TASKS.pop(0)


async def spinner():
    spinner_chars = itertools.cycle(["|", "/", "-", "\\"])
    while True:
        sys.stdout.write(next(spinner_chars))
        sys.stdout.flush()
        sys.stdout.write("\b")
        await sleep(0.1)


async def main(host: str, port: int):
    server = await start_server(new_conn, host, port)
    spinner_task = create_task(spinner())
    await server.serve_forever()
    spinner_task.cancel()


print(intro)
run(main("127.0.0.1", 8881))
