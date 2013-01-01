# Extract bits of data from a single frame of FRC match video
# Steven Bell <botsnlinux@gmail.com>
# 31 December 2012

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import code

def findNumber(templatePath, image):
  """
  Takes an image patch and does a correlation-based template search to find
  the numbers in the image.  templatePath is a string pointing to the directory
  and filenames containing templates for each of the digits 0-9.  This code uses
  %-substitution on the string to generate filenames. image is a 2-D (grayscale)
  numpy array which should have the same height as the templates.
  """

  #w = cv2.namedWindow("match")
  #cv2.imshow("match", diff)
  #cv2.waitKey()
      
  detections = dict()

  for digit in range(10):
    templateImage = cv2.imread(templatePath % digit)
    # TODO: Use grayscale images for templates and skip this
    templateImage = cv2.cvtColor(templateImage, cv2.COLOR_RGB2GRAY)
    templateImage = templateImage.astype(np.int16) # Convert to I16 so we can subtract
  
    if image.shape[0] != templateImage.shape[0]:
      print "Input size doesn't match template!"
      return None
  
    # Do a 1-D sliding window, calculating the sum of absolute differences
    slideLength = image.shape[1] - templateImage.shape[1] + 1
    ssd = np.zeros(slideLength)
    for i in range(slideLength):
      ssd[i] = np.sum(abs(image[:, i:(i+templateImage.shape[1])] - templateImage))
      
    # Normalize by the size of the template
    ssd = ssd / np.prod(templateImage.shape)

    # Find all of the detections below a certain threshold
    # TODO: take only the local minimum
    # TODO: remove conflicts
    finds = np.nonzero(ssd < 15)
    #code.interact(local=locals())

    for f in finds[0]:
      # Only add the last of consecutive detections
      if (f+1) not in finds[0]:
        detections[f] = digit
 
  # Sort the detections by position
  print detections

  # Build the number
  value = 0
  for p,val in detections.items():
    value *= 10
    value += val
    
  #code.interact(local=locals())
  
  return value

def __main__():
  inputImage = cv2.imread('frames/out0120.jpg')

  # Definition of where the scoreboard/status bar is
  sbLeft = 40
  sbRight = 680
  sbTop = 360
  sbBottom = 460
  
  # Pull out the scoreboard and scale it to match our working template size
  scoreboard = inputImage[sbTop:sbBottom, sbLeft:sbRight, :]

  # Pull out the timer patch and convert it to grayscale
  timerLeft = 295
  timerTop = 0
  timerWidth = 50
  timerHeight = 20
  timerPatch = scoreboard[timerTop:(timerTop+timerHeight), timerLeft:(timerLeft+timerWidth)]

  timerPatch = cv2.cvtColor(timerPatch, cv2.COLOR_RGB2GRAY)
  print findNumber('templates/timer/%d.png', timerPatch)
  #cv2.imwrite('timer.png', timerPatch)
  #code.interact(local=locals())


  ## Draw the scoreboard and some bounding boxes
  #imFig = plt.imshow(scoreboard)
  #ax = imFig.get_axes()
  #
  #ax.add_patch(patches.Rectangle([timerLeft, timerTop], timerWidth, timerHeight, fill=False)) 


  #plt.show()

  # Score

  # Teams playing

  #cv2.imwrite('scoreboard.png', scoreboard)

__main__()

