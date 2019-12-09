from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mitko123@localhost/weather_app'
app.config['SECRET_KEY'] = 'verySecretKey'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    name = db.Column(db.String(24), nullable=False)


def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=80b60c443a744c40ac9f82d9e3d4e0dc'
    r = requests.get(url).json()
    return r


@app.route('/')
def index():
    cities = City.query.all()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)
        temper = r['main']['temp']
        descript = r['weather'][0]['description']
        icn = r['weather'][0]['icon']
        weather = {'city': city.name,
                   'temperature': temper,
                   'description': descript,
                   'icon': icn,
                   }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    error_message = ''
    new_city = request.form.get('city')

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)

            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                error_message = 'City does not exists!'
        else:
            error_message = 'City already exists in the database!'

    if error_message:
        flash(error_message, 'error')
    else:
        flash('City added successfully!')

    return redirect(url_for('index'))


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f'Successfully deleted {city.name}')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=80)
