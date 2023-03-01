from flask import Flask, render_template
from flask_misaka import Misaka
from back_end import ConfigurationHandler
from capif import maybePublishApi
import json

app = Flask(__name__)

from front_end import bp as frontEndApi
app.register_blueprint(frontEndApi, url_prefix='/tsn/api/v1', name='frontEndApi')

with open('config.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    ConfigurationHandler.SetBackEnd(data['BackEnd'])

Misaka(app, tables=True)
with open('README.md', 'r', encoding='utf-8') as file:
    readme = file.read()

@app.route('/')
def index():
    return render_template('index.html', mkd=readme)

maybePublishApi()

if __name__ == '__main__':
    app.run()
