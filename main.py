import platform
import asyncio
import aiohttp

from datetime import date


URL_BASE = 'https://api.privatbank.ua/p24api/exchange_rates?date='#01.12.2014
TIKERS = ['EUR', 'USD']


def date_range_list(number_of_days=1):
    if number_of_days > 10:
        number_of_days = 10
    if number_of_days < 1:
        number_of_days = 1    

    today = date.today().toordinal()
    date_range = [date.strftime(date.fromordinal(d), '%d.%m.%Y') for d in range(today, today - number_of_days, -1)]
    return date_range
    

def urls_list_for_date_range(date_range_list,  url_base=URL_BASE):
    res = [url_base + i for i in date_range_list]
    return res


async def request(url):
    async with aiohttp.ClientSession() as session:

        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                await session.close()
            logging.error(f'Error status {response.status} for {url}')

        except aiohttp.ClientConnectionError as err:
            logging.error(f'Connection error {url}: {err}')
        return None


def print_out(data, tiker = TIKERS):
    res = []
    for i in data:
        ccy_rates = filter(lambda x: x['currency'] in tiker, i['exchangeRate'])
        data_per_day = {i['date']: {}}
        
        for curr in ccy_rates:
            cur = {curr['currency']: {'sale': curr['saleRate'], 'purchase': curr['purchaseRate']}}
        
            data_per_day[i['date']].update(cur)
        
        res.append(data_per_day)
    return res


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    number_of_days = int(input('>>>Input number of days: '))
    
    urls = urls_list_for_date_range(date_range_list(number_of_days), URL_BASE)

    res = [asyncio.run(request(url)) for url in urls]

    r = print_out(res, TIKERS)
    
    print(*r, sep='\n')