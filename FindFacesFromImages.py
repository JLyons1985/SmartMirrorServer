import glob
import os
import sys
import select
import fnmatch

import cv2

import serverConfig
import face

# Prefix for positive training image filenames.
POSITIVE_FILE_PREFIX = 'positive_'

def walk_files(directory, match='*'):
	"""Generator function to iterate through all files in a directory recursively
	which match the given filename match parameter.
	"""
	for root, dirs, files in os.walk(directory):
		for filename in fnmatch.filter(files, match):
			yield os.path.join(root, filename)

def is_letter_input(letter):
	# Utility function to check if a specific character is available on stdin.
	# Comparison is case insensitive.
	if select.select([sys.stdin,],[],[],0.0)[0]:
		input_char = sys.stdin.read(1)
		return input_char.lower() == letter.lower()
	return False

def convertImage(file):
   print('Converting image...')
   tmpimage = cv2.imread(file, cv2.COLOR_RGB2GRAY)
   # Get coordinates of single face in captured image.
   tmpresult = face.detect_single(tmpimage)
   if tmpresult is None:
      print('Could not detect single face! File: ' + file)
      return None

   x, y, w, h = tmpresult
   # Crop image as close as possible to desired face aspect ratio.
   # Might be smaller if face is near edge of image.
   crop = face.crop(tmpimage, x, y, w, h)
   return crop


if __name__ == '__main__':
   print("Looping through folders and creating images.")
   # Walk the directories taking non pgm  files and converting

   for i in range(len(serverConfig.USERS)):
      # Find the largest ID of existing positive images.
      # Start new images after this ID value.
      files = sorted(glob.glob(os.path.join(serverConfig.IMAGE_DIR, serverConfig.USERS[i],
                                            POSITIVE_FILE_PREFIX + '[0-9][0-9][0-9].pgm')))
      count = 0
      if len(files) > 0:
         # Grab the count from the last filename.
         count = int(files[-1][-7:-4]) + 1

      for filename in walk_files(serverConfig.IMAGE_DIR + serverConfig.USERS[i], '*.jpg'):
         image = convertImage(filename)
         # Get coordinates of single face in captured image.
         if image is None:
            continue

         newname = os.path.join(serverConfig.IMAGE_DIR, serverConfig.USERS[i],
                                 POSITIVE_FILE_PREFIX + '%03d.pgm' % count)
         cv2.imwrite(newname, image)
         print('Found face and wrote training image', newname)
         count += 1