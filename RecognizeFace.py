import cv2

import serverConfig
import face

def recognizeFace(model):

   # Initialize camer and box.
   camera = serverConfig.get_camera()
   # Check for the positive face and unlock if found.
   print("Trying to read an image from the camera.")
   image = camera.read()
   # Convert image to grayscale.
   print("Converting image to greyscale.")
   image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
   cv2.equalizeHist(image, image)
   # Get coordinates of single face in captured image.
   print("Trying to detect a single face.")
   result = face.detect_single(image)

   if result is None:
      print('Could not detect single face!  Check the image in capture.pgm' \
      ' to see what was captured and try again with only one face visible.')
      return 'NoFace'

   x, y, w, h = result
   # Crop and resize image to face.
   crop = face.resize(face.crop(image, x, y, w, h))
   # Test face against model.
   label, confidence = model.predict(crop)

   print(label)
   print(confidence)

   if label == serverConfig.NEGATIVE_LABEL:
      return 'Neg'
   else:
      for i in range(len(serverConfig.USERS)):
         if label == serverConfig.POSITIVE_LABELS[i] and confidence < serverConfig.POSITIVE_THRESHOLD :
            print('Found a match')
            return serverConfig.USERS[i]

      # Must not be a match
            print('No Match')
      return 'Neg'