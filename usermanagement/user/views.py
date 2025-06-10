from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, ContactSerializer
from rest_framework import status
from datetime import datetime, timedelta
from .models import User, Contact
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
import os
import jwt


load_dotenv()

class RegisterAPIView(APIView):

    def post(self,request):
        try:
            data = request.data
            first_name  = data.get("first_name")
            last_name = data.get("last_name")
            email       = data.get("email")
            password    = data.get("password")
            phone_no = data.get("phone_no")
            aadhar_no = data.get("aadhar_no")
            date_of_birth = data.get("date_of_birth")

            # If any field is missing then return a 
            if not all([first_name, last_name, email, password, phone_no,date_of_birth,aadhar_no]):
                return Response({"success":False,"message": "All fields including role are required."},
                                status=status.HTTP_400_BAD_REQUEST)


            if User.objects.filter(email=email).exists():
                return Response({"success":False,"message": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)
        
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "username": email,
                "password": password
            }

            contact_data = {
                "first_name": first_name,
                "last_name": last_name,
                "phone_no": phone_no,
                "aadhar_no": aadhar_no,
                "date_of_birth": date_of_birth
            }
            
            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                contact_data['user'] = user.id
                contact_serializer = ContactSerializer(data=contact_data)
                del user_data["password"]
                if contact_serializer.is_valid():
                    contact_serializer.save(user=user)
                    return Response({"success":True,"message": "User created successfully.","User":user_data}, status=status.HTTP_201_CREATED)
                return Response(contact_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success":False,"message": "Something went wrong.", "Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPIView(APIView):
    def post(self, request):
        try:
            # Get data from the request body
            data = request.data
            email    = data.get("email")
            password = data.get("password")

            if not all([email, password]):
                return Response({"success":False,"message": "Email and password are required."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Now find user using email. 
            user = User.objects.get(email=email)
            # print("User is :",user)

            # if email user not found using email then return response of invalid credential or User not exits.
            if not User.DoesNotExist:
                return Response({"success":False,"message": "Invalid credentials or User doesn't exists."}, status=status.HTTP_400_BAD_REQUEST)

            # if User exists then check for password entered correct or not.
            if not user.check_password(password):
                return Response({"success":False,"message": "Invalid credentials(email,password)."}, status=status.HTTP_400_BAD_REQUEST)


            # Now if everything is correct login the user. 
            serializer = UserSerializer(user)
            payload = serializer.data.copy() # copy the data into payload for token generation.

            #do the process of making an access token.
            expiration = datetime.now() + timedelta(minutes=15)
            payload['exp'] = expiration.isoformat()

            token = jwt.encode(
                payload,
                os.getenv('JWT_SECRET_KEY'),
                algorithm=os.getenv('JWT_ALGORITHM')
            )

            return Response({
                "success": True,
                "accessToken": token,
                "user": payload
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"success":False,"message": "Something went wrong.", "Error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# This view is to get the data of Particular user using {id}.
class UserDetailedAPIView(APIView):
    def get(self,reqeust, id):
        try:
            user = get_object_or_404(User, id=id)
            
            serializer = UserSerializer(user)
            return Response({"success":True,"message": "User Data Retrive Successfully", "Users":serializer.data},
                            status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"success":False,"message": "Something went wrong.", "Error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# This view is to get all user, delete a particular user, and update a particular user.

class UserDetailsAPIView(APIView):
    def get(self, request):
        try:
            user = User.objects.all()
            
            serializer = UserSerializer(user, many=True)
            return Response({"success":True,"message": "User Data Retrive Successfully", "Users":serializer.data},
                            status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"success":False,"message": "Something went wrong.", "Error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def delete(self, request, id):
        try:
            # Retrive user from the Id using helper function.
            user = get_object_or_404(User, id=id)


            # Perform deletion
            user.delete() # If Contact has on_delete=models.CASCADE, it will also be deleted

            return Response(
                {"success": True, "message": "Data deleted successfully."},
                status=status.HTTP_204_NO_CONTENT 
            )
        except Exception as e:
            return Response(
                {"success": False, "message": "Something went Wrong.","Error":str(e)},
                status=status.HTTP_204_NO_CONTENT
            )
        
    def put(self,request,id):
        try:
            user = get_object_or_404(User,id = id)
            contact = get_object_or_404(Contact, id = id)
            print(user)
            user_data = {
                "first_name":user.first_name,
                "last_name":user.last_name,
                "email":user.email,
                "password":user.password
            }
            

            contact_data = {
                "first_name":contact.first_name,
                "last_name":contact.last_name,
                "phone_no":contact.phone_no,
                "aadhar_no":contact.aadhar_no,
                "date_of_birth":contact.date_of_birth
            }

            user_serializer = UserSerializer(user_data,data = request.data, partial = True)
            
            print("yaha tk print kr rhe ho na")
            
            contact_serializer = ContactSerializer(contact_data,data = request.data, partial = True)

            if user_serializer.is_valid():
                user_serializer.save()

            if contact_serializer.is_valid():
                contact_serializer.save()

            return Response(
                    {"success": True, "message": "Data Updated Successfully.", "UdatedUser": user_data},
                    status=status.HTTP_204_NO_CONTENT 
                )
            
        except Exception as e:
            return Response({"success":False,"message": "Something went wrong.", "Error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)