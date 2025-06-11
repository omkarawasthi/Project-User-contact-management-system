from django.shortcuts import get_object_or_404
from ..serializers import UserSerializer, ContactSerializer
from ..models import User, Contact
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
import os, jwt
from dotenv import load_dotenv
from rest_framework import status
from rest_framework import serializers
from ..utils.db_logging import log_in_db
from django.core.cache import cache
import json
from django.db.models import Q

load_dotenv()


def register_user(data):
    first_name  = data["first_name"]
    last_name = data["last_name"]
    email       = data["email"]
    password    = data["password"]
    phone_no = data["phone_no"]
    aadhar_no = data["aadhar_no"]
    date_of_birth = data["date_of_birth"]
    username = data["username"]

    # If any field is missing then return all field requireds.
    if not all([first_name, last_name, email, password, phone_no,date_of_birth,aadhar_no,username]):
        log_in_db("User Form Error", "CREATE", "User", {"message": "All fields including role are required."})
        return {"success":False,"message": "All fields including role are required."},status.HTTP_400_BAD_REQUEST


    
    if User.objects.filter(email=email).exists():
        log_in_db("User Email Error", "CREATE", "User", {"message": "Email already registered."})
        return {"success":False,"message": "Email already registered."}, status.HTTP_400_BAD_REQUEST
    
    user = User.objects.filter(email=email)
    
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "username":data["username"],
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
    else:
        log_in_db("Validation Error", "CREATE", "User", {"Error": user_serializer.errors})
        return {"success": False, "errors": user_serializer.errors}, status.HTTP_400_BAD_REQUEST
    
    contact_data['user'] = user.id
    contact_serializer = ContactSerializer(data=contact_data)
    del user_data["password"]
    if contact_serializer.is_valid():
        contact_serializer.save(user=user)
        
        log_in_db("INFO", "CREATE", "User", {"message": "User created successfully.","User":user_data})

        return {"success":True,"message": "User created successfully.","User":user_data},status.HTTP_201_CREATED
    
    else:
        log_in_db("Validation Error", "CREATE", "User", {"Error": contact_serializer.errors})
        return {"success": False, "errors": contact_serializer.errors},status.HTTP_400_BAD_REQUEST


def login_user(data):
    email = data.get("email")
    password = data.get("password")

    user_data = {
        "email": email,
        "password": password
    }

    if not all([email, password]):
        log_in_db("ERROR", "LOGIN", "User", {"message": "Email and password are required."})
        return {"success":True,"message": "Email and password are required."}, status.HTTP_400_BAD_REQUEST

    try:
        email = UserSerializer().validate_email(email)
    except serializers.ValidationError as ve:
        log_in_db("ERROR", "LOGIN", "User", {"message": "Invalid email format."})
        return {"success": False, "message": str(ve.detail[0])}, status.HTTP_400_BAD_REQUEST
    

    try:
        user = User.objects.get(email=email)
        print(user.email)
    except User.DoesNotExist:
        log_in_db("ERROR", "LOGIN", "User",{"message":"User with this email does not exist."})
        return {"success": False, "message": "Invalid credentials or User doesn't exist."}, status.HTTP_400_BAD_REQUEST
    
    if not user.check_password(password):
        log_in_db("ERROR", "LOGIN", "User", {"message": "Invalid credentials (email/password)."})
        return {"success":False,"message": "Invalid credentials (email/password)."}, status.HTTP_400_BAD_REQUEST

    serializer = UserSerializer(user)
    payload = serializer.data.copy()
    payload['exp'] = (datetime.now() + timedelta(minutes=15)).isoformat()
    
    token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm=os.getenv('JWT_ALGORITHM'))
    log_in_db("INFO", "LOGIN", "User", {"message": "User Login Successfully"})
    print("Yha nhi aa pa rhe")
    return {"success":True,"accessToken": token, "user": payload}, status.HTTP_200_OK



def get_all_users():
    cached_users = cache.get("all_users")

    if cached_users:
        print("Retrieved users from cache")
        return {
            "success": True,
            "message": "Users retrieved from cache.",
            "users": json.loads(cached_users)
        }, status.HTTP_200_OK

    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    data = serializer.data
    cache.set("all_users", json.dumps(data), timeout=60*60)  # 1 hour cache
    return {
        "success": True,
        "message": "Users retrieved from database.",
        "users": data
    }, status.HTTP_200_OK

def get_user_by_id(user_id):
    cache_key = f"user_{user_id}"
    cached_user = cache.get(cache_key)

    if cached_user:
        print(f"Retrieved user from cache")
        return {
            "success": True,
            "message": f"User retrieved from cache.",
            "user": json.loads(cached_user)
        }, status.HTTP_200_OK

    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    data = serializer.data
    cache.set(cache_key, json.dumps(data), timeout=60*60)
    return {
        "success": True,
        "message": f"User retrieved from database.",
        "user": data
    }, status.HTTP_200_OK


def delete_user_by_id(user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()

    log_in_db("INFO", "DELETE", "User AND Contact", {"message": "User deleted successfully."})
    return {"success":True,"message": "User deleted successfully."}, status.HTTP_204_NO_CONTENT


def update_user_and_contact(id, data):
    contact = get_object_or_404(Contact, id = id)

    if not contact.DoesNotExist:
        log_in_db("ERROR", "UPDATE", "User AND Contact", {"messsage":"User does not Exists."})
        return {"Success":False, "messsage":"User does not Exists."},status.HTTP_400_BAD_REQUEST

    user = contact.user

    user_data = {
        'email':data['email'],
        'password':data['password']
    }
            
    contact_data = {
        'first_name':data['first_name'],
        'last_name':data['last_name'],
        'phone_no':data['phone_no'],
        'aadhar_no':data['aadhar_no'],
        'date_of_birth':data['date_of_birth']
    }

            # if email changes then
    if 'email' in user_data:
        user.email = user_data['email']
        user.username = user_data['email']
            
    if 'password' in user_data:
        user.password = make_password(user_data['password'])
            
    user.save()

            # Update Contact fields via serializer
    serializer = ContactSerializer(instance=contact, data=contact_data, partial=True)

    if serializer.is_valid():
        serializer.save()
        log_in_db("INFO", "UPDATE", "User AND Contact", {"message": "User and Contact updated successfully."})
        return {
                    "success":True,
                    "message": "User and Contact updated successfully.",
                    "user_email": user.email,
                }, status.HTTP_200_OK
    else:
        log_in_db("ERROR", "UPDATE", "User AND Contact", {"message": serializer.errors})
        return {"success": False, "message": serializer.errors},status.HTTP_204_NO_CONTENT
    



def search_users(filters):
    name = filters.get('name')
    dob = filters.get('date_of_birth')
    upcoming_birthdays = filters.get('upcoming_birthdays', 'false').lower() == 'true'
    print("Name :",name)

    queryset = Contact.objects.all()

    if name:
        queryset = queryset.filter(
            Q(first_name__icontains=name) | Q(last_name__icontains=name)
        )

    if dob:
        # print("query set",queryset)
        queryset = queryset.filter(date_of_birth=dob)

    if upcoming_birthdays:
        today = datetime.today().date()
        in_seven_days = today + timedelta(days=7)
        queryset = queryset.filter(
            date_of_birth__month__gte=today.month,
            date_of_birth__day__gte=today.day,
            date_of_birth__month__lte=in_seven_days.month,
            date_of_birth__day__lte=in_seven_days.day,
        )

    serializer = ContactSerializer(queryset, many=True)
    # print("Serializer data :",serializer.data)
    return {"success": True, "message": "Filtered users retrieved.", "users": serializer.data}