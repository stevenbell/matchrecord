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

  w = cv2.namedWindow("match")
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
      #ssd[i] = np.sum(abs(image[:, i:(i+templateImage.shape[1])] - templateImage))
      ssd[i] = np.sum((image[:, i:(i+templateImage.shape[1])] - templateImage)**2)
      
    # Normalize by the size of the template
    ssd = ssd / np.prod(templateImage.shape)

    # Find all of the detections below a certain threshold
    # TODO: take only the local minimum
    # TODO: remove conflicts
    finds = np.nonzero(ssd < 150)
    #code.interact(local=locals())

    for f in finds[0]:
      # Only add the last of consecutive detections
      if (f+1) not in finds[0]:
        # Search for things this might overlap with
        another = False
        for i in range(f-5, f+5):
          if i in detections:
            another = True
            if ssd[f] < detections[i][1]:
              print "replacing %d (%f) with %d (%f)" % (detections[i][0], detections[i][1], digit, ssd[f])
              detections.pop(i) # Remove the inferior detection
              detections[f] = (digit, ssd[f]) # Replace with better detection
        # If there were none,
        if another == False:
          detections[f] = (digit, ssd[f]) # New detection
 
  # Sort the detections by position
  #print detections

  #if len(detections) >= 3:
  #  code.interact(local=locals())

  # Build the number
  value = 0
  for key in sorted(detections.keys()):
    value *= 10
    value += detections[key][0]

  #code.interact(local=locals())
  
  return value

def __main__():
  frameNum = 0 # Count of frames we've processed
  inputVideo = cv2.VideoCapture('2012ok_qm003.mp4')
  frame = inputVideo.read()
  while frame[0] is True:
    inputImage = frame[1]
  
    # Definition of where the scoreboard/status bar is
    sbLeft = 40
    sbRight = 680
    sbTop = 362
    sbBottom = 460
    
    # Pull out the scoreboard and scale it to match our working template size
    scoreboard = inputImage[sbTop:sbBottom, sbLeft:sbRight, :]
  
    # Pull out the timer patch and convert it to grayscale
    timerLeft = 295
    timerTop = 0
    timerWidth = 50
    timerHeight = 16
    timerPatch = scoreboard[timerTop:(timerTop+timerHeight), timerLeft:(timerLeft+timerWidth)]
  
    # Convert to "grayscale" by just keeping the green
    # The green channel keeps the highest contrast when the bar crosses the numbers
    timerPatch = timerPatch[:, :, 1]
    time = findNumber('templates/timer/%d.png', timerPatch)

    print "%04d, %d" % (frameNum, time)

    
    #if frameNum >= 510 and frameNum <= 520:
    #  cv2.imshow("match", inputImage)
    #  cv2.waitKey()
 
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
    frame = inputVideo.read()
    frameNum += 1

__main__()

