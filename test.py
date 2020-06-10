from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from rq import Queue
from worker import conn
from function import get_result

q = Queue(connection=conn, default_timeout=3600)



app = Flask(__name__)
api = Api(app)

class getResult(Resource):

    def post(self):
        json_object = request.get_json()
        result = q.enqueue(get_result, args= (json_object,), timeout = 500)
        return {'status': 'Success'},200

api.add_resource(getResult, '/result')
if __name__ == '__main__':
    app.run(debug=True)