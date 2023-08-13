import csv
import io
import random
import asyncio

import exrex
from faker import Faker
from flask import Flask, render_template, request, make_response

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
async def generate():
    rows = int(request.form['rows'])
    columns = request.form.getlist('column')
    custom_columns = request.form.getlist('custom_column')
    csv_data = await generate_csv(rows, columns, custom_columns)  # await here
    return send_csv(csv_data)


async def generate_csv(rows, columns, custom_columns):
    output = io.StringIO()
    writer = csv.writer(output)

    async def generate_row():
        row = []
        for column in columns:
            value = generate_value(column)
            row.append(value)

        for regex in custom_columns:
            value = generate_custom_value(regex)
            row.append(value)
        return row

    tasks = [generate_row() for _ in range(rows)]
    rows = await asyncio.gather(*tasks)

    for row in rows:
        writer.writerow(row)

    return output.getvalue()


def generate_value(column):
    if column == 'names':
        fake = Faker('ru-RU')
        return fake.name()
    elif column == 'products':
        fake = Faker('ru-RU')
        categories = ['Электроника', 'Товары для дома', 'Красота и здоровье', 'Книги', 'Игрушки', 'Авто', 'Продукты']
        adjective = fake.safe_color_name()
        material = fake.job()
        product = fake.catch_phrase()
        return f"{adjective} {material} {product} - {random.choice(categories)}"
    elif column == 'phone_numbers':
        return generate_phone_number()
    else:
        return ''


def generate_custom_value(regex):
    return exrex.getone(regex)


def generate_phone_number():
    regex = r'\+7\d{10}'
    return exrex.getone(regex)


def send_csv(csv_data):
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    response.headers['Content-type'] = 'text/csv'
    return response


if __name__ == '__main__':
    app.run(debug=True)
