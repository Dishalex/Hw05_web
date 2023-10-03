import asyncio
import logging
import websockets
import aiohttp
import names
from websockets import WebSocketServerProtocol, WebSocketProtocolError
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]


    async def send_to_client(self, message: str, ws: WebSocketServerProtocol):
        await ws.send(message)


    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.strip().lower() == 'exchange':
                r = await get_exchange()
                await self.send_to_client(r, ws)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever




async def request(url):
    async with aiohttp.ClientSession() as session:
                
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                await session.close()
                return html[:100]
            logging.error(f'Error status {response.status} for {url}')

        except aiohttp.ClientConnectionError as err:
            logging.error(f'Connection error {url}: {err}')
        return None


async def get_exchange():
    res = await request('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')
    exchange, *_ = list(filter(lambda x: x['ccy'] == 'USD', res))
    
    return f"USD: buy: {exchange['buy']}, sale: {exchange['sale']}"

if __name__ == '__main__':
    asyncio.run(main())