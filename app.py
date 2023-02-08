from flask import Flask, render_template
from flask_misaka import Misaka
from back_end import ConfigurationHandler
import yaml

app = Flask(__name__)

from front_end import bp as frontEndApi
app.register_blueprint(frontEndApi, url_prefix='/api/v1', name='frontEndApp')

with open('config.yml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)
    ConfigurationHandler.SetBackEnd(data['BackEnd'])

Misaka(app, tables=True)
with open('README.md', 'r', encoding='utf-8') as file:
    readme = file.read()

@app.route('/')
def index():
    return render_template('index.html', mkd=readme)


if __name__ == '__main__':
    app.run()
