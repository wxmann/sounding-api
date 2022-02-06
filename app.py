from fastapi import FastAPI, Response, status

from sounding import get_sounding

app = FastAPI()


@app.get('/health')
def health():
    return {'status': 'OK'}


@app.get('/sounding')
def sounding(date: str, hour: int, station: str, response: Response):
    dt = f'{date} {hour}'
    try:
        return get_sounding(dt, station)
    except ValueError as e:
        error_str = str(e).lower()
        if 'could not convert string' in error_str:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                'error': f'could not parse date {date}'
            }
        elif 'no data available' in error_str:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                'error': f'no data for {station} at {date} {hour}:00'
            }
        raise e
