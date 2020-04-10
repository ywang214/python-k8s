import os
import pandas as pd
from flask import Flask, request, render_template, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from sqlalchemy.dialects.postgresql import UUID, BIGINT
from flask_marshmallow import Marshmallow


app = Flask(__name__, template_folder='template')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)
api = Api(app)
ma = Marshmallow(app)
hashtag_map = {"#one": "1", "#two": "2", "#three": "3", "#four": "4", "#five": "5",
               "#six": "6", "#seven": "7", "#eight": "8", "#nine": "9", "#ten": "10"}


class Model(db.Model):
    created_on = db.Column(BIGINT)
    partition_number = db.Column(db.Integer)
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    hashtags = db.Column(db.String())

    def __init__(self, created_on, partition_number, uuid, hashtags):
        self.created_on = created_on
        self.partition_number = partition_number
        self.id = uuid
        self.hashtags = hashtags

    def __repr__(self):
        return '<id %s>' % self.id


class ModelSchema(ma.Schema):
    class Meta:
        fields = ("created_on", "partition_number", "id", "hashtags")


model_schema = ModelSchema()
models_schema = ModelSchema(many=True)


@app.route("/")
def upload():
    return render_template("index.html")


@app.route('/handle_upload', methods=['POST'])
def handle_form():
    file = request.files['file']
    data = pd.read_csv(file, sep=",", header=None, error_bad_lines=False, names=range(100))
    for index, row in data.iterrows():
        hashtag = ""
        hashtag_set = set()
        for i in range(len(row)):
            if i > 2:
                if is_valid_hashtag(row[i]) & (row[i] not in hashtag_set):
                    hashtag += row[i] + ","
                    hashtag_set.add(row[i])

        record = Model(row[0], row[1], row[2], hashtag[:-1])
        try:
            db.session.add(record)
            db.session.commit()
        except:
            db.session.rollback()

    return '', 201


@app.route("/text.txt")
def download():
    data = Model.query.all()
    records = models_schema.dump(data)
    # len(records)

    def generate():
        for row in records:
            yield str(row["created_on"]) + ',' + str(row["partition_number"]) + ',' + (row["id"]) + ',' + (convert_hashtags(row["hashtags"])) + '\n'

    return Response(generate(),
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                             "attachment;filename=text.txt"})


def convert_hashtags(data):
    result = ""
    for hashtag in data.split(','):
        if hashtag in hashtag_map:
            result += hashtag_map[hashtag] + ","
    return result[:-1]


def is_valid_hashtag(hashtag):
    return hashtag in hashtag_map.keys()


class DataController(Resource):
    def get(self):
        data = Model.query.all()
        records = models_schema.dump(data)
        return models_schema.dump(data)

    def delete(self):
        Model.query.delete()
        try:
            db.session.commit()
        except:
            db.session.rollback()

        return '', 204


api.add_resource(DataController, '/data')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
