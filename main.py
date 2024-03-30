from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import uvicorn
import requests
from pydantic import BaseModel
from requests.structures import CaseInsensitiveDict
import jwt

app = FastAPI()

available_currency = {
    'EUR': 'Euro',
    'USD': 'US Dollar',
    'JPY': 'Japanese Yen',
    'BGN': 'Bulgarian Lev',
    'CZK': 'Czech Republic Koruna',
    'DKK': 'Danish Krone',
    'GBP': 'British Pound Sterling',
    'HUF': 'Hungarian Forint',
    'PLN': 'Polish Zloty',
    'RON': 'Romanian Leu',
    'SEK': 'Swedish Krona',
    'CHF': 'Swiss Franc',
    'ISK': 'Icelandic Króna',
    'NOK': 'Norwegian Krone',
    'HRK': 'Croatian Kuna',
    'RUB': 'Russian Ruble',
    'TRY': 'Turkish Lira',
    'AUD': 'Australian Dollar',
    'BRL': 'Brazilian Real',
    'CAD': 'Canadian Dollar',
    'CNY': 'Chinese Yuan',
    'HKD': 'Hong Kong Dollar',
    'IDR': 'Indonesian Rupiah',
    'ILS': 'Israeli New Sheqel',
    'INR': 'Indian Rupee',
    'KRW': 'South Korean Won',
    'MXN': 'Mexican Peso',
    'MYR': 'Malaysian Ringgit',
    'NZD': 'New Zealand Dollar',
    'PHP': 'Philippine Peso',
    'SGD': 'Singapore Dollar',
    'THB': 'Thai Baht',
    'ZAR': 'South African Rand',
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY = 'somesecretkey'
ALGORITHM = 'HS256'

USERS_DATA = [
    {'username': 'user1', 'password': 'user1pass'}
]


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None


def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user(username: str):
    for user in USERS_DATA:
        if user.get('username') == username:
            return user
    return None


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


@app.get('/available_currency/')
async def get_available_currency():
    return available_currency


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
