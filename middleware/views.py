from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
import json
import requests
from django.conf import settings
from firebase_admin import auth

# Create your views here.

@api_view(['GET', 'PUT', 'DELETE'])
def proxy(request):
    try:
        # Creating URL
        method = request.method
        path = request.get_full_path()
        if path.startswith("/users/"):
            url = f"{settings.HOST["USERS"]}{path}"
        elif path.startswith("/books/"):
            url = f"{settings.HOST["BOOKS"]}{path}"
        elif path.startswith("/book-user/"):
            url = f"{settings.HOST["BOOK-USER"]}{path}"
        else:
            return JsonResponse({"error": "Unknown host."}, status=400)

        # Checking for valid authorization token
        bypass_auth = ['/users/add']
        if path not in bypass_auth:
            if 'Authorization' in request.headers:
                id_token = request.headers['Authorization'].split(' ')[1]
            else:
                return JsonResponse({"error": "No authorization token provided."}, status=401)
            
            try:
                decoded_token = auth.verify_id_token(id_token)
            except auth.RevokedIdTokenError:
                return JsonResponse({"error": "Revoked authorization token."}, status=401)
            except auth.InvalidIdTokenError:
                return JsonResponse({"error": "Invalid authorization token."}, status=401)
        
        # Sending request
        if method == "GET":
            resp = requests.get(url)
        elif method == "DELETE":
            resp = requests.delete(url)
        elif method == "PUT":
            data = json.loads(request.body.decode("utf-8") or "{}")
            if data is not None:
                resp = requests.put(url, json=data)
            else:
                resp = requests.put(url)
        else:
            return JsonResponse({"error": "Unknown method."}, status=400)
        
        return JsonResponse(resp.json(), status=resp.status_code, safe=False)
    except:
        return JsonResponse({"error":"Server error."}, status=500)

