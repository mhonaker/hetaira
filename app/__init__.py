from flask import Flask

app = Flask('app')
app.config.from_object('config')

from app import views
