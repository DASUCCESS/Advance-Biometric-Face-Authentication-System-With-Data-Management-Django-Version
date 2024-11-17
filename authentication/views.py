from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import face_recognition
import base64
from io import BytesIO
from PIL import Image
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
import jwt  
from django.conf import settings  


class RegisterUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            face_image_data = request.data.get('image')
            username = request.data.get('username')

            if not face_image_data or not username:
                return Response({"error": "Username and image data are required."}, status=status.HTTP_400_BAD_REQUEST)

            # Checking if the image data contains the prefix (we expect base64 without the 'data:image/jpeg;base64,' part)
            if face_image_data.startswith("data:image"):
                face_image_data = face_image_data.split(",")[1]

            try:
                image_data = base64.b64decode(face_image_data)
            except Exception as e:
                return Response({"error": "Invalid base64 image data."}, status=status.HTTP_400_BAD_REQUEST)

            image = Image.open(BytesIO(image_data))
            image = face_recognition.load_image_file(BytesIO(image_data))
            face_encodings = face_recognition.face_encodings(image)

            if len(face_encodings) == 0:
                return Response({"error": "No face found in the image."}, status=status.HTTP_400_BAD_REQUEST)

            user_data = {
                'username': username,
                'face_data': face_encodings[0].tolist()  # Convert numpy array to list for JSON serialization
            }
            serializer = UserSerializer(data=user_data)

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            face_image_data = request.data.get('image')

            if not face_image_data or not username:
                return Response({"error": "Username and image data are required."}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(username=username).first()
            if not user:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # THIS IS WHERE DECODING of the base64 image data 
            if face_image_data.startswith("data:image"):
                face_image_data = face_image_data.split(",")[1]

            image_data = base64.b64decode(face_image_data)
            image = face_recognition.load_image_file(BytesIO(image_data))
            face_encodings = face_recognition.face_encodings(image)
            if len(face_encodings) == 0:
                return Response({"error": "No face found in the image."}, status=status.HTTP_400_BAD_REQUEST)

            # This will compare the uploaded image with the user's face data and generate JWT token
            if face_recognition.compare_faces([user.face_data], face_encodings[0]):
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Face recognition failed."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # This i used to decode the JWT token manually to confirm the user_id
        token = request.headers.get('Authorization').split(' ')[1]  
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        # print(f"Decoded Token: {decoded_token}")  

        user_id = decoded_token.get("user_id")
        if not user_id:
            return Response({"error": "User ID not found in token."}, status=status.HTTP_401_UNAUTHORIZED)

        # This will fetch the user using the user_id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"username": user.username, "user_id": user.id})



    
# List all user data (GET)
class UserDataListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserData.objects.filter(user=user)
        serializer = UserDataSerializer(data, many=True)
        return Response(serializer.data)

class AllUserDataView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        
        data = UserData.objects.all()
        serializer = UserDataSerializer(data, many=True)
        return Response(serializer.data)
    
# This is creating the user data
class UserDataCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# This will Update user data
class UserDataUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            user_data = UserData.objects.get(id=pk, user=request.user)
        except UserData.DoesNotExist:
            return Response({"error": "Data not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDataSerializer(user_data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#  This will Delete user data 
class UserDataDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            user_data = UserData.objects.get(id=pk, user=request.user)
        except UserData.DoesNotExist:
            return Response({"error": "Data not found."}, status=status.HTTP_404_NOT_FOUND)

        user_data.delete()
        return Response({"message": "Data deleted successfully."}, status=status.HTTP_204_NO_CONTENT)