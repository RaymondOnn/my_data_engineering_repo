from src.db import db

class DeptEmpLink(db.Model):
    __tablename__ = "dept_emp"
    
    # Columns
    id = db.Column(db.Integer, primary_key = True)
    emp_id = db.Column('emp_no', db.Integer, db.ForeignKey("employees.emp_no"))
    dep_id = db.Column('dept_no', db.String(4), db.ForeignKey("departments.dept_no"))
    
