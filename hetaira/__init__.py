from flask import Flask

app = Flask('hetaira')
app.config.from_object('config')

from hetaira import views
