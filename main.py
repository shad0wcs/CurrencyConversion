from typing import Optional, Annotated
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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

USERS_DATA = {
    'admin': {'username': 'admin', 'password': 'adminpass', 'role': 'admin'},
    'user': {'username': 'user', 'password': 'userpass', 'role': 'user'}
}


class User(BaseModel):
    username: str
    password: str
    role: Optional[str] = None


def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get('sub')
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'},
        )


def get_user(username: str):
    if username in USERS_DATA:
        user_data = USERS_DATA[username]
        return User(**user_data)
    return None


@app.post('/token/')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = get_user(form_data.username)
    if user_data is None or user_data.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {'access_token': create_jwt_token({'sub': user_data.username}), 'token_type': 'Bearer'}


@app.get('/admin/')
async def get_admin_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(current_user)
    if user_data.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized',
        )
    return {'message': 'welcome back, admin'}


@app.get('/user/')
async def get_user_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(current_user)
    if user_data.role != 'user':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized',
        )
    return {'message': 'welcome back, user'}


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
