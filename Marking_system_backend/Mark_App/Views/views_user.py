import json
from rest_framework.response import Response
from rest_framework.views import APIView

from Mark_App.models.User_Model import User

class Upload_A_User(APIView):
    def post(self, request):
        pass


class Get_All_Users(APIView):
    def get(self, request):
        try:
            user_obj = User.objects.all()
            print(user_obj.first().User_email)
            return Response({"rtCode": 0, "rtMsg": "success", 'Email':user_obj.first().User_email})
        except Exception as e:
            return Response(json.dumps({"rtCode": 1, "rtMsg": str(e), "rtData": ""}))