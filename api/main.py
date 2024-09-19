import json

from fastapi import FastAPI
import uvicorn

from api.prompts import prompt_with_date, prompt_with_baserow_id

from sdk.messages.human import HumanMessage
from sdk.messages.system import SystemMessage
from sdk.llm.yandex.chat_model import YandexChatGPT

import requests
from typing import List
from datetime import datetime
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

app = FastAPI()


@app.get('/action-info')
def get_action_info_gpt(user_prompt: str):
    """Get action info from gpt response"""

    model = YandexChatGPT()

    messages = [
        SystemMessage(content=prompt_with_date),
        HumanMessage(content=user_prompt)
    ]
    result = model.invoke(messages).replace('`', '').replace("'", '"')

    try:
        result = json.loads(result)
        return result

    except json.JSONDecodeError:
        return {'error': 'Непредвиденная ошибка. Попробуйте написать запрос иначе'}


@app.get('/action-info-with-bid')
def get_action_info_gpt_with_bid(user_prompt: str):
    """Get action info from gpt response with baserow-id"""

    model = YandexChatGPT()

    messages = [
        SystemMessage(content=prompt_with_baserow_id),
        HumanMessage(content=user_prompt)
    ]
    result = model.invoke(messages).replace('`', '').replace("'", '"')

    try:
        result = json.loads(result)
        return result

    except json.JSONDecodeError:
        return {'error': 'Непредвиденная ошибка. Попробуйте написать запрос иначе'}

@app.post('/group-free-slots-by-psychologist')
async def group_free_slots_by_psychologists(slots: str):
    slots = slots.split(';')
    result = ''
    grouped_slots = {}
    session = requests.Session()
    session.headers.update({'Authorization': 'Token 70oZEBzcucQOIKcn3WlRJwXT37tXV92y'})

    for slot in slots:
        date, time = slot.split(' ')
        day, month = date.split('.')
        year = datetime.now().year
        date = f'{day}/{month}/{year}'

        try:
            for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=2, max=10)):
                with attempt:
                    records = session.get(
                        'https://baserow.hrani.live/api/database/rows/table/373/'
                        '?user_field_names=true'
                        '&filters={"filter_type":"AND",'
                        '"filters":['
                        '{"type":"contains","field":"Время",' + f'"value":"{time}"' + '},'
                        '{"type":"contains","field":"Дата",' + f'"value":"{date}"' + '},'
                        '{"type":"contains","field":"Статус","value":"Свободен"}],'
                        '"groups":[]}'
                    ).json()['results']

                    for record in records:
                        # if record['Психолог'][0]['value'] not in grouped_slots:
                        #     grouped_slots[record['Психолог'][0]['value']] = {}
                        #
                        # if f'{day}.{month}' not in grouped_slots[record['Психолог'][0]['value']]:
                        #     grouped_slots[record['Психолог'][0]['value']][f'{day}.{month}'] = []
                        #
                        # if time not in grouped_slots[record['Психолог'][0]['value']][f'{day}.{month}']:
                        #     grouped_slots[record['Психолог'][0]['value']][f'{day}.{month}'].append(time)
                        print(f'{day}.{month}')
                        if f'{day}.{month} {time}' not in grouped_slots:
                            grouped_slots[f'{day}.{month} {time}'] = [record['Психолог'][0]['value']]
                        else:
                            grouped_slots[f'{day}.{month} {time}'].append(record['Психолог'][0]['value'])

        except RetryError:
            grouped_slots = {
                'error': 'Извините, но ,к сожалению, мы не смогли получить список свободных слотов из-за непредвиденной'
                         'ошибки'
            }

    return {'result': grouped_slots}
uvicorn.run(app, host='0.0.0.0', port=3125)
# uvicorn.run(app)
