path="Capture34.png"

import http.client, urllib.request, urllib.parse, urllib.error, base64,json
import numpy as np
import cv2
import pandas as pd

threshold=0.1

def api_call(image):
    ## fonction prenant une image (format binary) et rendant le .json de l'API de customvision

    ### Lecture des credentials, dans le .gitignore, qui viennent de la clé d'API###
    with open("credential.json") as datafile:
        data = json.load(datafile)
    headers = {
        # Request headers
        "Prediction-Key" : data["Prediction-Key"],
        'Content-Type': 'application/octet-stream',
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'iterationId': '55da43e9-9d4e-4361-8878-1736f827062d',
        'application': '{string}',
    })

    body=image
    try:
        conn = http.client.HTTPSConnection('southcentralus.api.cognitive.microsoft.com')
        conn.request("POST", "/customvision/v2.0/Prediction/a013ec63-3327-4fcf-a5ff-cf36fc374ad6/image?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        #print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    return json.loads(data.decode('utf8'))


def draw(image,box,text):
    # dessine sur l'image la box en input et le text

    a,b,c,d=box
    img=image
    #dessine le rectangle
    cv2.rectangle(img,a,b,c,d)
    #écriture du texte. Le +20 est là pour décaler le texte de la ligne blanche
    cv2.putText(img,text,org=(a[0],a[1]+20), fontFace=2,fontScale=0.3,color=(250,250,250))
    print("image error",img)
    cv2.imshow('image',image)
   # cv2.waitKey(0)
   # cv2.destroyAllWindows()

def process_image(image,threshold=0.1):
    # fait le processing d'une image en faisant l'appel et le dessin
    # threshold : seuil de sensibilité pour détecter un objet

    height, width, channels = image.shape
    # Complexe because conversion from cv2 format to binary
    predictions=api_call(cv2.imencode('.jpg', image)[1].tostring())["predictions"]
    boxes=[item["boundingBox"] for item in predictions if item["probability"]>threshold]
    items=[item["tagName"] for item in predictions if item["probability"]>threshold]
    #image=cv2.imread(path)
    print(predictions)
    for k in range(len(boxes)):
        box=boxes[k]    
        text=items[k]
        draw(image,((int(box["left"]*width),int(box["top"]*height)),(int((box["left"]+box["width"])*width),int((box["top"]+box["height"])*height)),(255,255,255),3),text)

#process_image(cv2.imread(path))

def read_video(path):
    # TODO : processer les images sur toute une vidéo
    cap = cv2.VideoCapture(path)

    count=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if count<2600:
            #print("wainting to start")
            count+=1
        elif count>2650:
            break
        else:
            count+=1
            process_image(frame)
#            draw(frame,((0,0),(300,300),(250,250,250),3),"hello world")
            #cv2.imshow('frame',gray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
read_video("videos/falcon.mp4")