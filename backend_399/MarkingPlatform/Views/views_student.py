import json

from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from MarkingPlatform.models.StudentModel import Student


class Upload_A_Student(APIView):
    '''

        format:{
            "Student_first_name": "",   # required
            "Student_last_name": "",    # required
            "Student_UPI": "",          # required
            "Student_email": ""         # required
            }
    '''
    def post(self, request):
        try:
            student_obj = Student.objects.create(
                Student_first_name=request.data['Student_first_name'],
                Student_last_name=request.data['Student_last_name'],
                Student_UPI=request.data['Student_UPI'],
                Student_email=request.data['Student_email']
            )
            student_obj.save()
            return Response(json.dumps({"rtCode": 0, "rtMsg": "success", "rtData": student_obj.Student_id}))
        except Exception as e:
            return Response(json.dumps({"rtCode": 1, "rtMsg": str(e), "rtData": ""}))


class Get_All_Students(APIView):
    def get(self, request):
        try:
            student_obj = Student.objects.all()
            return Response(json.dumps({"rtCode": 0, "rtMsg": "success", "rtData": student_obj}))
        except Exception as e:
            return Response(json.dumps({"rtCode": 1, "rtMsg": str(e), "rtData": ""}))


