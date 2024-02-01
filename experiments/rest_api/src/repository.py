from src.models import UserModel, DepartmentModel
from src.db import db

# class Repository:
#     def __init__(self) -> None:
#         pass
    
class DepartmentRepository(Repository):
    def __init__(self, session):
        self.session = session
        
    def get(self, **filters):
        pass
    
    def get_all(self, **filters):
        return DepartmentModel.query.all()
    
    def create(self, dept_name):
        def create_primary_key():
            last_key = db.session.scalar(db.func.max(DepartmentModel.id))
            num = int(last_key[1:])    # dept_id fixed to 4 chars: dXXX
            return 'd' + str(num + 1).rjust(3, '0')   
    
        new_dept = DepartmentModel(create_primary_key(), )
        new_dept.id = create_primary_key()
        new_dept.name = dept_data['name']
        self.session.add(new_dept)
        self.session.commit()
        return DepartmentModel
    
    def update(self, **kwargs):
        pass
    
    def delete(self, id_):
        pass