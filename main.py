import cv2
import numpy as np

# Use YCrCb color space to detect skin
# If the skin is mapped to YCrCb space, the pixel points of the skin in YCrCb space are approximated as an elliptical distribution. 
# So if we get an ellipse of CrCb, for a point with coordinates (Cr, Cb), 
# we only need to determine whether it is inside the ellipse (including the boundary) to know whether it is a skin-colored point or not.
def detectSkin(img):

	YCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
	(y, cr, cb) = cv2.split(YCrCb)
	cr = cv2.GaussianBlur(cr, (5,5), 0)
	_, skin = cv2.threshold(cr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
	return skin

# Compute the contours of image and convex hull
def detectContours(img):

    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(contours)
    return contours, hull

# Use the ratio of the convex hull area to the actual area of the hand to distinguish between splay and fist, palm. 
# The area ratio of splay should between 0.65 and 0.85.The area ratio of fist or palm should between 0.85 and 1.0
# Use aspect ratio to distinguish between fist and palm. 
# The aspect ratio of fist should larger than 0.7. The aspect ratio of palm should between 0.4 and 0.7.
def detectGesture(contours, hull, img):
	handArea = cv2.contourArea(contours)
	hullArea = cv2.contourArea(hull)
	areaRatio = handArea / hullArea

	x, y, w, h = cv2.boundingRect(contours)
	aspectRatio = float(w) / h
	#print(areaRatio)
	if areaRatio < 0.85 and areaRatio > 0.65:
		if aspectRatio > 0.6:
			gesture = "splay"
		else:
			gesture = "unknown"
	elif areaRatio >= 0.85 and areaRatio < 1.0:
		if aspectRatio > 0.7:
			gesture = "fist"
		elif aspectRatio > 0.4:
			gesture = "palm"
		else:
			gesture = "unknown"
	else:
		gesture = "unknown"
	return gesture

	'''
	if areaRatio < 0.85 and areaRatio > 0.65:
		gesture = "splay"
	elif  areaRatio >= 0.85:
		gesture = "fist"
	else:
		return "unknown"
	return gesture
	'''



# Divided the picture into 9 parts.
# Used the center coordinates of the hand to determine it's position.
# Set the boundary of 9 parts as unknown
def detectPosition(contours, height, width):
	x, y, w, h = cv2.boundingRect(contours)

	centerX = x + w / 2
	centerY = y + h / 2

	heightLine = height / 3 #567
	widthLine = width / 3 #425

	lineY = 7 * heightLine / 8 #425
	lineX = 7 * widthLine / 8 #319

	if centerX <= lineX:
		if centerY <= lineY:
			return "upper left"
		elif centerY <= heightLine + lineY and centerY >= 2 * heightLine - lineY:
			return "center left"
		elif centerY >= 3 * heightLine - lineY:
			return "lower left"
		else:
			return "unknown"
		
	elif centerX <= widthLine + lineX and centerX >= 2 * widthLine - lineX:	
		if centerY <= lineY:
			return "upper center"
		elif centerY <= heightLine + lineY and centerY >= 2 * heightLine - lineY:
			return "center center"
		elif centerY > 3 * heightLine - lineY:
			return "lower center"
		else:
			return "unknown"

	elif centerX >= 3 * widthLine - lineX:
		if centerY <= lineY:
			return "upper right"
		elif centerY <= heightLine + lineY and centerY >= 2 * heightLine - lineY:
			return "center right"
		elif centerY >= 3 * heightLine - lineY:
			return "lower right"
		else:
			return "unknown"
		
	else:
		return "unknown"

def main():

	lock = [["fist","lower left"],["unknown","center center"],["palm","upper right"]]
	path = ["./images/good1.jpg", "./images/good2.jpg", "./images/good3.jpg"]
	correct = 0
	for i in range(3):
		img = cv2.imread(path[i])
		height = img.shape[0]
		width = img.shape[1]
		skin = detectSkin(img)
		contours, hull = detectContours(skin)
		gesture = detectGesture(contours, hull, img)
		position = detectPosition(contours, height, width)
		print(gesture + "," + position)
		cv2.namedWindow('img',cv2.WINDOW_NORMAL)
		cv2.resizeWindow("img", 630, 850)
		cv2.imshow("img", skin)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		if (gesture == lock[i][0] and position == lock[i][1]):
			correct += 1
	if correct == 3:
		print("Can open the lock")
	else:
		print("Can't open the lock")

if __name__ == '__main__':
	main()