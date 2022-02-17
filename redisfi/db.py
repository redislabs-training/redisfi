from redis import Redis

_key_bars = lambda ticker: f'bars:{ticker}'

def set_bar(redis: Redis, ticker: str, timestamp: int, open: float,
             high: float, low: float, close: float, volume: int):
   
    redis.zadd(_key_bars(ticker),{f'{open}|{high}|{low}|{close}|{volume}':timestamp})
