import time

import aiohttp
import asyncio

sync_time = ''
async_time= ''

async def get(i: int, endpoint: str):
    # print(f'Начал: {i}')
    url = f'http://127.0.0.1:8000/{endpoint}/{i}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            pass
            # print(f'Закончил: {i}')


async def main():
    global sync_time, async_time

    # begin_sync = time.time()
    # await asyncio.gather(
    #     *[get(i, 'sync') for i in range(99)],
    # )
    # end_sync = time.time()
    # sync_time = f'{(end_sync - begin_sync):.2f}'



    begin_async = time.time()
    await asyncio.gather(
        *[get(i, 'async') for i in range(9999)],
    )
    end_async = time.time()
    async_time = f'{(end_async - begin_async):.2f}'

begin = time.time()
asyncio.run(main())
end = time.time()
print(f'sync time: {sync_time}, async time: {async_time}')