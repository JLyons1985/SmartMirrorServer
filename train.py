"""Raspberry Pi Face Recognition Treasure Box
Face Recognition Training Script
Copyright 2013 Tony DiCola 

Run this script to train the face recognition system with positive and negative
training images.  The face recognition model is based on the eigen faces
algorithm implemented in OpenCV.  You can find more details on the algorithm
and face recognition here:
  http://docs.opencv.org/modules/contrib/doc/facerec/facerec_tutorial.html
"""
import fnmatch
import os

import cv2
import numpy as np

import serverConfig
import face


MEAN_FILE = 'mean.png'
POSITIVE_EIGENFACE_FILE = 'positive_eigenface.png'
NEGATIVE_EIGENFACE_FILE = 'negative_eigenface.png'


def walk_files(directory, match='*'):
	"""Generator function to iterate through all files in a directory recursively
	which match the given filename match parameter.
	"""
	for root, dirs, files in os.walk(directory):
		for filename in fnmatch.filter(files, match):
			yield os.path.join(root, filename)

def prepare_image(filename):
   """Read an image as grayscale and resize it to the appropriate size for
   training the face recognition model.
   """
   image = face.resize(cv2.imread(filename, cv2.IMREAD_GRAYSCALE))
   cv2.equalizeHist(image,  image)
   return image

def normalize(X, low, high, dtype=None):
	"""Normalizes a given array in X to a value between low and high.
	Adapted from python OpenCV face recognition example at:
	  https://github.com/Itseez/opencv/blob/2.4/samples/python2/facerec_demo.py
	"""
	X = np.asarray(X)
	minX, maxX = np.min(X), np.max(X)
	# normalize to [0...1].
	X = X - float(minX)
	X = X / float((maxX - minX))
	# scale to [low...high].
	X = X * (high-low)
	X = X + low
	if dtype is None:
		return np.asarray(X)
	return np.asarray(X, dtype=dtype)

def train():
   print("Reading training images...")
   faces = []
   labels = []
   pos_count = 0
   neg_count = 0

   # Need to loop through all the positive directories based off serverConfig
   # Read all positive images
   for i in range(len(serverConfig.USERS)):
      for filename in walk_files(serverConfig.IMAGE_DIR + serverConfig.USERS[i], '*.pgm'):
         faces.append(prepare_image(filename))
         labels.append(serverConfig.POSITIVE_LABELS[i])
         pos_count += 1

   # Read all negative images
   for filename in walk_files(serverConfig.IMAGE_DIR + serverConfig.NEGATIVE_DIR, '*.pgm'):
      faces.append(prepare_image(filename))
      labels.append(serverConfig.NEGATIVE_LABEL)
      neg_count += 1
   print('Read', pos_count, 'positive images and', neg_count, 'negative images.')

   # Train model
   print('Training model...')
   model = cv2.face.createFisherFaceRecognizer()
   model.train(np.asarray(faces), np.asarray(labels))

   # Save model results
   model.save(serverConfig.TRAINING_FILE)
   print('Training data saved to', serverConfig.TRAINING_FILE)

   # Save mean and eignface images which summarize the face recognition model.
   mean = model.getMean().reshape(faces[0].shape)
   cv2.imwrite(MEAN_FILE, normalize(mean, 0, 255, dtype=np.uint8))
   #eigenvectors = model.getFisherVectors()
   #pos_eigenvector = eigenvectors[:, 0].reshape(faces[0].shape)
   #cv2.imwrite(POSITIVE_EIGENFACE_FILE, normalize(pos_eigenvector, 0, 255, dtype=np.uint8))
   #neg_eigenvector = eigenvectors[:, 1].reshape(faces[0].shape)
   #cv2.imwrite(NEGATIVE_EIGENFACE_FILE, normalize(neg_eigenvector, 0, 255, dtype=np.uint8))

if __name__ == '__main__':
   train()