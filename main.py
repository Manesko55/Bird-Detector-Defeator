import picamera
import os
from  google.cloud import vision


windowWidth = 4056
windowHeight = 3040

def takePhoto():
	camera = picamera.PiCamera()
	camera.capture('image.jpg')

def main():
	takePhoto()

	os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"profile.json"
	client = vision.ImageAnnotatorClient()
	file_name = 'image.jpg'

	with open('image.jpg','rb') as image_file:
		content = image_file.read()
		
	image = vision.Image(content = content)

	response = client.object_localization(image = image)
	objects = response.localized_object_annotations

	#print(objects)
	for obj in objects:
		print('=' * 30)
		print(obj)
		if( obj.name == "Bird"):
			print("MATCH!!!!!!!!!")
			verX1 = obj.bounding_poly.normalized_vertices[0].x
			verY1 = obj.bounding_poly.normalized_vertices[0].y
			verX2 = obj.bounding_poly.normalized_vertices[2].x
			verY2 = obj.bounding_poly.normalized_vertices[2].y

			avpX = findCenterpoint(verX1, verX2)
			avpY = findCenterpoint(verY1, verY2)

			print(findNormalValuesX(avpX))
			print(findNormlValuesY(avpY))

			
def findCenterpoint(ver1, ver2):
	avp = (ver1 + ver2) / 2
	return avp

def findNormalValuesX(avp):
	norm = avp * windowWidth
	return norm

def findNormlValuesY(avp):
	norm = avp * windowHeight
	return norm


main()

	
