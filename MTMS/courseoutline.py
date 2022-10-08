from MTMS import db_session
from MTMS.Models.courses import Course, Term
import os
import xlrd
from flask import current_app


file = xlrd.open_workbook(os.path.join(current_app.root_path, 'courseoutline.xlsx'))
term = file.sheet_by_index(0)
rows = term.nrows

course=[]
for i in range(1, rows):
    course.append(term.row_values(i))
print(course)


path = os.path.join(os.path.dirname(current_app.instance_path), "MTMS", "EmailTemplate")



newC = Course(
    courseNum="COMP 1000",
    courseName="Cloud and Big Data Computing",
)

db_session.add(newC)

db_session.commit()