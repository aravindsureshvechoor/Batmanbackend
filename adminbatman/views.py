from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import User

# Create your views here.
class AdminLogin(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')

        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_staff:
            refresh = RefreshToken.for_user(user)

            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.first_name,
                    }
            }
            return Response(tokens, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class BlockUser(APIView):
    def post(self,request,pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=404)

        user.is_blocked = True
        user.save()


        return Response({'message': 'User blocked successfully'})

class UnblockUser(APIView):
    def post(self,request,pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=404)

        user.is_blocked = False
        user.save()

        return Response({'message': 'User Unblocked successfully'})

class Deleteunregisteredusers(APIView):
    def delete(self, request):
        unregistered_users = User.objects.filter(otp__isnull=False)
        deleted_count = unregistered_users.delete()[0]
        return Response({"message": f"{deleted_count} unregistered users deleted."})
