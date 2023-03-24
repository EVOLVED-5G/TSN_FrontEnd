from flask import Flask, render_template
from flask_misaka import Misaka
from back_end import ConfigurationHandler
from capif import maybePublishApi
import json

app = Flask(__name__)

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
    ConfigurationHandler.SetBackEnd(config['BackEnd'])
    app.config["CAPIF_ENABLED"] = config['CAPIF']['Enabled']
    app.config["CAPIF_SECURITY_ENABLED"] = config['CAPIF']['SecurityEnabled']

Misaka(app, tables=True)
with open('README.md', 'r', encoding='utf-8') as file:
    readme = file.read()

if app.config["CAPIF_ENABLED"]:
    maybePublicKey = maybePublishApi(config)

    if app.config["CAPIF_SECURITY_ENABLED"]:
        if maybePublicKey is None:
            print("Security enabled, but unable to retrieve public key. Aborting.")
            exit()
        else:
            from flask_jwt_extended import JWTManager
            JWTManager(app)

            app.config["JWT_ALGORITHM"] = 'RS256'
            app.config["JWT_PUBLIC_KEY"] = maybePublicKey


from front_end import bp as frontEndApi
app.register_blueprint(frontEndApi, url_prefix='/tsn/api/v1', name='frontEndApi')

@app.route('/')
def index():
    return render_template('index.html', mkd=readme)

if __name__ == '__main__':
    app.run()
