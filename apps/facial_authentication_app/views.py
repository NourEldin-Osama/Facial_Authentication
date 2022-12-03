import base64
import numpy as np
import cv2
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import face_recognition
import pickle


def home(request):
    context = {"title": "Home"}
    return render(request, 'home.html', context)


def encode_user(image):
    face_encoding = face_recognition.face_encodings(image, num_jitters=100, model='large')[0]
    return face_encoding


def image_from_js_to_cv2(data):
    data = str(data)
    data = data.replace('data:image/jpeg;base64,', '').replace(' ', '+')
    imgdata = base64.b64decode(data)
    np_arr = np.fromstring(imgdata, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # concert to RGB
    return img


@api_view(['POST'])
def add_user(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            if username is not None and username != "Unknown" and username.strip() != "":
                frame = request.POST.get('image')
                img = image_from_js_to_cv2(frame)

                try:
                    with open("test.pkl", "rb") as f:
                        known_face_encodings = pickle.load(f)
                        known_face_names = pickle.load(f)
                except FileNotFoundError:
                    known_face_encodings = []
                    known_face_names = []

                known_face_encodings.append(encode_user(img))
                known_face_names.append(username)
                print('Learned encoding for', len(known_face_encodings), 'images.')

                with open("test.pkl", "wb") as f:
                    pickle.dump(known_face_encodings, f)
                    pickle.dump(known_face_names, f)
                response = F"User {username} add successfully"
            else:
                if username is not None:
                    response = "Error username = None"
                elif username.strip() != "":
                    response = "Error username is empty"
                else:
                    response = "Error username = Unknown"
        except Exception as e:
            print('Error', e)
    try:
        r = response
    except NameError:
        response = "ERROR"
    return Response({'Response': response}, status=200)


@api_view(['POST'])
def recognize_user(request):
    if request.method == 'POST':
        try:
            frame = request.POST.get('image')
            unknown_image = image_from_js_to_cv2(frame)
            with open("test.pkl", "rb") as f:
                known_face_encodings = pickle.load(f)
                known_face_names = pickle.load(f)

            face_locations = face_recognition.face_locations(unknown_image, model="cnn")
            face_encodings = face_recognition.face_encodings(unknown_image, face_locations, num_jitters=100,
                                                             model='large')
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)

                name = "Unknown"

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                face_match_percentage = (1 - face_distances) * 100
                best_match_percentage = face_match_percentage[np.argmax(face_match_percentage)]
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    response_percentage = F"{best_match_percentage:.2f}"
                if name != "Unknown":
                    response_username = F"{name}"
                    break
        except Exception as e:
            print('Error', e)
    try:
        r = response_username
    except NameError:
        response_username = ""
    try:
        r = response_percentage
    except NameError:
        response_percentage = ""
    return Response({'username': response_username, "accuracy": response_percentage}, status=200)
