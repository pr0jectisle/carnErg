import cv2
   
class Face:
    def __init__(self):
        self.face_detected = False
        cv2.namedWindow("preview")
        cap = cv2.VideoCapture(0)

        face_classifier = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )


        if cap.isOpened():
            status, photo = cap.read()
        else:
            status = False

        while status:
            #cv2.imshow("preview", photo)
            status, photo = cap.read()

            gray_image = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
            face = face_classifier.detectMultiScale(
                gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
            )
            face_detected = len(face) == 0
            for (x, y, w, h) in face:
                cv2.rectangle(photo, (x, y), (x + w, y + h), (0, 255, 0), 4)

            img_rgb = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
        
            cv2.imshow("preview", photo)
        
            key = cv2.waitKey(20)
            if key == 27: # exit on ESC
                break


        cv2.destroyWindow("preview")
        cap.release()


f = Face()