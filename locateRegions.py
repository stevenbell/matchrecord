import cv2
import numpy as np
import code

def localizeText(img, rect):
  """
  Find (black) text within a small grayscale region.  Assuming that there
  are at least two rows of pixels along the top and bottom which do not contain
  text, we can find the light and dark colors by taking the minimum.  Given
  the light and dark values, we can pick a threshold and slice the image
  vertically.
  img - Input grayscale image.
  Returns - Tuple with (x, y, x2, y2) describing the bounding box.
  """
  subimg = img[rect[1]:rect[3], rect[0]:rect[2]]

  # Figure out a threshold for the text using minimum values horizontally
  centerY = subimg.shape[0] / 2 # Vertical center of the subimage
  rowMins = np.min(subimg, 1)
  dark = np.mean(rowMins[(centerY - 3):(centerY + 3)])
  light = np.mean([rowMins[0:2], rowMins[-2:]])
  thresh = (light + dark) / 2.0

  # Use the threshold to find the area which has text
  colMins = np.min(subimg, 0)
  textCols = np.nonzero(colMins < thresh)
  left = rect[0] + np.min(textCols)
  right = rect[0] + np.max(textCols)

  textRows = np.nonzero(rowMins < thresh)
  top = rect[1] + np.min(textRows)
  bottom = rect[1] + np.max(textRows)
  
  #code.interact(local=locals())
  #cv2.imshow("win", subimg)
  #cv2.waitKey()

  return (left, top, right, bottom)

def locateRegions(frame):
  regions = dict()

  # General position definitions
  # These should be calculated based on the size of the panel in the video
  barHeight = 16 # TODO calculate this
  centerX = frame.shape[1] / 2
  scoreOffsetX = 10
  scoreWidth = 100
  scoreHeight = 50

  # Search for the time
  # Use the green channel for finding the time
  regions['time'] = localizeText(frame[:, :, 1], (centerX - 50, 0, centerX + 50, 16))

  # Find the color of the time bar
  # This is easiest to do by looking at the left edge
  #colorBar = frame(

  # Use the red channel for finding the red score
  regions['redScore'] = localizeText(frame[:, :, 2], \
                              (centerX - scoreOffsetX - scoreWidth, 25,
                               centerX - scoreOffsetX, scoreHeight + 25))

  # Use the blue channel for finding the blue score
  regions['blueScore'] = localizeText(frame[:, :, 0], \
                              (centerX + scoreOffsetX, 25,
                               centerX + scoreOffsetX + scoreWidth, scoreHeight + 25))

  # Find the team numbers by looking for the bright green (blue < 70, green > 120)
  # Could also have yellow if they got a yellow card
  teamPatch = (frame[:, :, 0] < 70) & (frame[:, :, 1] > 140)
  vert = np.nonzero(np.any(teamPatch, 1))
  top = np.min(vert)
  bottom = np.max(vert)
  
  horzLeft = np.nonzero(np.any(teamPatch[:, 0:360], 0)) # TODO: don't hardcode
  left = np.min(horzLeft)
  right = np.max(horzLeft)
  regions['redTeam1'] = (left, top, right, bottom)

  horzRight = np.nonzero(np.any(teamPatch[:, 360:], 0)) # TODO: don't hardcode
  left = np.min(horzRight) + 360
  right = np.max(horzRight) + 360
  regions['blueTeam1'] = (left, top, right, bottom)

  regions['matchNum'] = localizeText(frame[:, :, 0], (500, 50, 719, 80))

  return regions


def displayRegions(frame, regions):

  frameDraw = np.array(frame) # Make another copy for drawing

  timeLoc = regions['time']
  cv2.rectangle(frameDraw, (timeLoc[0], timeLoc[1]), (timeLoc[2], timeLoc[3]), [0, 255, 255])

  redScoreLoc = regions['redScore']
  cv2.rectangle(frameDraw, (redScoreLoc[0], redScoreLoc[1]), \
                           (redScoreLoc[2], redScoreLoc[3]), [0, 0, 255])

  blueScoreLoc = regions['blueScore']
  cv2.rectangle(frameDraw, (blueScoreLoc[0], blueScoreLoc[1]), \
                           (blueScoreLoc[2], blueScoreLoc[3]), [255, 0, 0])

  redTeam1 = regions['redTeam1']
  cv2.rectangle(frameDraw, (redTeam1[0], redTeam1[1]), \
                           (redTeam1[2], redTeam1[3]), [0, 0, 255])

  blueTeam1 = regions['blueTeam1']
  cv2.rectangle(frameDraw, (blueTeam1[0], blueTeam1[1]), \
                           (blueTeam1[2], blueTeam1[3]), [255, 0, 0])

  matchNumLoc = regions['matchNum']
  cv2.rectangle(frameDraw, (matchNumLoc[0], matchNumLoc[1]), \
                           (matchNumLoc[2], matchNumLoc[3]), [0, 255, 255])


  cv2.namedWindow("win")
  cv2.imshow("win", frameDraw)
  cv2.waitKey()



def __main__():
  frame = cv2.imread('frames/out0250.jpg')

  # Definition of where the scoreboard/status bar is
  sbLeft = 40
  sbRight = 680
  sbTop = 362
  sbBottom = 460
  
  # Pull out the scoreboard and scale it to match our working template size
  scoreboard = frame[sbTop:sbBottom, sbLeft:sbRight, :]

  regions = locateRegions(scoreboard)
  displayRegions(scoreboard, regions)
  print "Done."

__main__()

