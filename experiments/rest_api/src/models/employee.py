from src.db import db

class EmployeeModel(db.Model):
    __tablename__ = "employees"

    # columns
    id = db.Column('emp_no', db.Integer, primary_key=True)
    first_name = db.Column('first_name', db.String(50),  nullable=False)
    last_name = db.Column('last_name', db.String(50), nullable=False)
    gender = db.Column('gender', db.String(1), nullable=False)
    birth_date = db.Column('birth_date', db.DateTime(), nullable=False)
    hire_date = db.Column('hire_date', db.DateTime(), nullable=False)
    
    # relationships
    departments = db.relationship("DepartmentModel", back_populates="employees", secondary="dept_emp")
    
    def __repr__(self) -> str:
        return f"""Employee(
            id={self.id}, 
            first_name={self.first_name}, 
            last_name={self.last_name}, 
            gender={self.gender}, 
            birth_date={self.birth_date}, 
            hire_date={self.hire_date}
        )"""