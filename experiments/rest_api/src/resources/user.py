from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256

from src.models import UserModel
from src.db import db
from src.schema import UserSchema, UserRegisterSchema
from src.blocklist import BLOCKLIST

# /register: 
# /login
# /logout
# /refresh
# /user/<user_id>: for testing

blp = Blueprint("users", __name__, description= "Operation on Users")

@blp.route('/user/<int:user_id')
class User(MethodView):
    '''for development purposes'''
    
    @blp.response(200, UserSchema)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        msg = f'User(id={user.id}, username={user.username}) deleted.'
        db.session.delete(user)
        db.session.commit()
        return {'message': msg}, 200
    
@blp.route('/register')
class UserRegistry(MethodView):
    '''create new user'''
    # inputs: email, user, pass
    
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):
        # username and email must be unique
        if UserModel.query.filter( 
            (UserModel.username == user_data['username']) 
            | (UserModel.id == user_data['id']) 
        ).first():
            abort(409, message='A user with that username/email already exists.')
            
        user = UserModel(
            username=user_data['username'],
            password=pbkdf2_sha256.hash(user_data['password']),
            email=user_data['email']
        )
        
        db.session.add(user)
        db.session.commit()
        return {'message': 'User successfully created'}

blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserSchema)    
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data['username']
            )
        
        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            # create access token and refresh token
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token, 
                'refresh_token': refresh_token
            }, 200
        abort(401, message="Invalid credentials.")    
            
            
@blp.route('/logout')            
class UserLogout(MethodView):
    '''Create logout entry'''
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']
        BLOCKLIST.add(jwt_id)
        return {'message': 'Successfully logged out'}, 200


@blp.route('/refresh')            
class TokenRefresh(MethodView):
    
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=True)
        return {
                'access_token': new_token, 
            }, 200