from config import TIME_TO_UPDATE, URL
from admin import error_timetable
from datetime import datetime
import asyncio
import aiohttp
import csv
import io

month = [str(i) for i in range(1,32)]
days = {'Пн':'Понедельник', 'Вт':'Вторник','Ср':'Среда','Чт':'Четверг','Пт':'Пятница'}

classes = {}
take_class = ['Дни', 'Уроки']
take_teacher = ['Альянаки', 'Антонова', 'Баталова', 'Бежина', 'Брюхов', 'Бушин', 'Вавилин',
                'Гасанов', 'Гачегова', 'Демидова', 'Жувак', 'Зотина', 'Ковалевская', 'Коровина',
                'Кощеева', 'Ларина', 'Леготкина', 'Мартынова', 'Митюшева', 'Нилов', 'Осташова', 'Ошева',
                'Полушкина', 'Разепина', 'Ракина', 'Рыкова', 'Снигирев', 'Соболева', 'Сонинский',
                'Степанова', 'Сутоцкая', 'Федотова', 'Филенко А', 'Филенко Д', 'Хайрулина', 'Хромцова',
                'Чепурин', 'Чигодайкина', 'Шестакова', 'Штейн']
teachers = dict.fromkeys(take_teacher, '')

async def update_table(url: URL):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                response.raise_for_status()
                content = await response.text(encoding='utf-8')

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        await error_timetable(str(datetime.now().time())[:8], e)
        return

    reader = csv.reader(io.StringIO(content))

    global classes, teachers
    classes = {}
    teachers = dict.fromkeys(take_teacher, '')

    global take_class
    take_class = ['Дни', 'Уроки']

    for row in reader:
        if not row:
            continue

        if row[0] == 'Дни':
            for i in range(2, len(row)):
                class_name = row[i]
                classes[class_name] = f'{class_name}'
                take_class.append(class_name)
        else:
            if row[0] in month:
                row[0] = ''
            elif row[0] in days:
                for j in take_teacher:
                    teachers[j] = f'{teachers[j]}\n<b>📆{days[row[0]]}</b>\n'

            for i in range(2, len(row)):
                class_key = take_class[i]
                classes[class_key] = f'{classes[class_key]}\n{row[0]}\n{row[1]}. {row[i]}'

                for j in take_teacher:
                    if j in row[i]:
                        teachers[j] = f'{teachers[j]}\n<b>{row[1]}.</b> {row[i].split(j)[0]} {class_key}\n'
                        break

async def periodic_update():
    while True:
        await asyncio.sleep(TIME_TO_UPDATE)
        await update_table(URL)