from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from src.schema import DepartmentSchema, DepartmentCreateSchema, DepartmentUpdateSchema

from src.db import db
from src.models import DepartmentModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# /department: get all departments
# /department/<dep_id>/employee: get employees of selected department 

blp = Blueprint("departments", __name__, description= "abc")

@blp.route("/department/<string:dept_id>")
class Department(MethodView):
    '''Get info regarding by dep_id'''
    @jwt_required()
    @blp.response(200, DepartmentSchema)
    def get(self, dept_id):
        # get() supprts query by primary key
        return DepartmentModel.query.get_or_404(dept_id)
    
    '''Update dept info by dept_id'''
    @jwt_required()
    @blp.arguments(DepartmentUpdateSchema) # check input
    @blp.response(201, DepartmentSchema) # check output
    def put(self, dept_data, dept_id):
        dept = DepartmentModel.query.get_or_404(dept_id)
        if dept:
            # take on the new data
            dept.id = dept_data['id']
            dept.name = dept_data['name']
        else:
            # else use the old data
            dept = DepartmentModel(**dept_data)
    
        db.session.add(dept)
        db.session.commit()
        return dept
    
    '''Delete dept info by dept_id'''
    @jwt_required()
    def delete(self, dept_id):
        dept = DepartmentModel.query.get_or_404(dept_id.lower())
        msg = f'Department(id={dept.id}, name={dept.name}) deleted'
        db.session.delete(dept)
        db.session.commit()
        return {'message': msg}
    
    
@blp.route("/department")
class DepartmentList(MethodView):
    '''Get all departments'''
    @jwt_required()
    @blp.response(200, DepartmentSchema(many=True))
    def get(self):
        return DepartmentModel.query.all()
    
    '''Create new department record'''
    # User supplies department name, system generates dept_id
    @jwt_required()
    @blp.arguments(DepartmentCreateSchema)
    @blp.response(201, DepartmentSchema)
    def post(self, dept_data): 
        def create_primary_key():
            last_key = db.session.scalar(db.func.max(DepartmentModel.id))
            print(last_key)
            num = int(last_key[1:])    # dept_id fixed to 4 chars: dXXX
            return 'd' + str(num + 1).rjust(3, '0')   
    
        new_dept = DepartmentModel()
        new_dept.id = create_primary_key()
        new_dept.name = dept_data['name']
        try: 
            db.session.add(new_dept)
            db.session.commit()
        except IntegrityError:
            abort(
                400, 
                message='A department with that name already exists.'
            )
        except SQLAlchemyError: # catchall error
            abort(
                500, 
                message='An error occurred creating the department.'
            )
        return new_dept
    
@blp.route("/department/manager/<string:dept_id>")
class DepartmentManager(MethodView):
    '''Get manager_ids by dep_id'''
    @jwt_required()
    def get(self):
        raise NotImplementedError
    
#     def post(self):
#         pass
    
#     def delete(self):
#         pass
    
    