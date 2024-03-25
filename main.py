from fastapi import FastAPI, HTTPException
import uvicorn
import requests
from requests.structures import CaseInsensitiveDict

app = FastAPI()


def get_exchange_rate(base_currency: str, final_currency: str) -> float:
    url = "https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_IBCijLqCB9AmAPIMJrcydRgvVYnaKjNCnIV8RyqQ"

    headers = CaseInsensitiveDict()
    headers["apikey"] = "fca_live_IBCijLqCB9AmAPIMJrcydRgvVYnaKjNCnIV8RyqQ"

    resp = requests.get(url)
    
    data = resp.json()

    if 'data' not in data:
        raise HTTPException(status_code=400, detail="Invalid currency")
    if final_currency not in data['data']:
        raise HTTPException(status_code=400, detail="Invalid currency")
    return data['data'][final_currency]


@app.get('/convert/')
async def convert_currency(
        base_currency: str,
        final_currency: str,
        amount: float,
):
    try:
        exchange_rate = get_exchange_rate(base_currency, final_currency)
        converted_currency = round(amount * exchange_rate, 2)
        return {'Converted amount': converted_currency}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail='Sever error')


if __name__ == '__main__':
    uvicorn.run('main:app',
                host='127.0.0.1',
                port=8000,
                reload=True)
