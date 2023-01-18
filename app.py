from flask import Flask


app = Flask(__name__)


from front_end import bp as frontEndApi
app.register_blueprint(frontEndApi, url_prefix='/api/v1', name='frontEndApp')


if __name__ == '__main__':
    app.run()
