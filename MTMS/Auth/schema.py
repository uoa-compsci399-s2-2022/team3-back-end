from marshmallow import Schema, fields


class userInput(Schema):
    userID = fields.Str()
    password = fields.Str()
    email = fields.Str(required=False)
    name = fields.Str(required=False)