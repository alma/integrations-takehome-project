from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return (
        "See "
        '<a href="https://github.com/alma/integrations-takehome-project#endpoints-disponibles">here</a> '
        "for endpoints documentation"
    )
