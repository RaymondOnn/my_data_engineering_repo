from src.db import db

class DeptManagerLink(db.Model):
    __tablename__ = "dept_manager"
    
    # Columns
    emp_id = db.Column('emp_no', db.Integer, db.ForeignKey("employees.emp_no"))
    dep_id = db.Column('dept_no', db.String(4), db.ForeignKey("departments.dept_no"))
    from_date = db.Column('from_date',db.DateTime(), nullable=False)
    to_date = db.Column('from_date',db.DateTime(), nullable=False)
