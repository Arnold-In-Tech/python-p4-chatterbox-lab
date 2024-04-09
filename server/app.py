from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    
    if request.method == 'GET':
        messages = []
        from sqlalchemy import asc
        for message in Message.query.order_by(asc('created_at')).all(): # ordered by created_at in ascending order.
            message_dict = message.to_dict()
            messages.append(message_dict)

        response = make_response(
            messages,
            200
        )

        return response


    elif request.method == 'POST':

        # new_message = Message(
        #     body=request.form.get("body"),
        #     username=request.form.get("username")
        # )

        # Retrieve the data (posted as json) with request.get_json() as instructed 
        data = request.get_json()
        
        new_message = Message(
            body=data["body"],
            username=data["username"]
        )

        db.session.add(new_message)
        db.session.commit()
        
        message_dict = new_message.to_dict()

        response = make_response(
            message_dict,
            201
        )

        return response

        
@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):

    message = Message.query.filter(Message.id == id).first()

    if message == None:
        response_body = {
            "message": "This record does not exist in our database. Please try again."
        }
        response = make_response(response_body, 404)

        return response


    else:
        if request.method == 'PATCH':
            
            # The updated message is patched as a json, therefore request.get_json() is used to retrieve it
            updated_message = request.get_json()
        
            for attr in updated_message:
                setattr(message, attr, updated_message.get(attr))

            db.session.add(message)
            db.session.commit()

            message_dict = message.to_dict()
            
            response = make_response(
                message_dict,
                200
            )

            return response

 
        elif request.method == 'DELETE':
            db.session.delete(message)
            db.session.commit()

            response_body = {
                "delete_successful": True,
                "message": "Review deleted."
            }

            response = make_response(
                response_body,
                204
            )

            return response


if __name__ == '__main__':
    app.run(port=5555)
