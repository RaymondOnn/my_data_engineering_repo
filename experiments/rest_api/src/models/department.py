from src.db import db



    
class DepartmentModel(db.Model):
    __tablename__ = "departments"
    
    # columns
    id = db.Column('dept_no', db.String, primary_key=True)
    name = db.Column('dept_name', db.String(50), unique=True, nullable=False)
    
    # relationships
    employees = db.relationship("EmployeeModel", back_populates="departments", secondary="dept_emp")
    managers = db.relationship("EmployeeModel", back_populates='departments', secondary='dept_manager')
    
    
    def __repr__(self) -> str:
        return f"""Department(
            id={self.id}, 
            name={self.name} 
        )"""
        