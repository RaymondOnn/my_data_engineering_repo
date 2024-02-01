from marshmallow import Schema, fields

class DepartmentSchema(Schema):
    id = fields.String(required=True)
    name = fields.String(dump_only=True)
    
class DepartmentCreateSchema(Schema):
    name = fields.String(required=True)    
    
class DepartmentUpdateSchema(DepartmentCreateSchema):
    id = fields.String(required=True)

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)

class UserRegisterSchema(UserSchema):
    email = fields.String(required=True)    