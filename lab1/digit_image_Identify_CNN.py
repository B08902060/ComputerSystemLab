TF_LITE_MODEL = './mnist.tflite'  # TF Lite 模型

import imp
from tracemalloc import is_tracing
import attr
import cv2
from cv2 import putText
from cv2 import waitKey
import numpy as np
from tflite_runtime.interpreter import Interpreter
interpreter = Interpreter(model_path=TF_LITE_MODEL)
# 準備模型
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
# 讀取輸入長寬
INPUT_H, INPUT_W = input_details[0]['shape'][1:3]

# Choose your webcam: 0, 1, ...
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("number_4_to_9.mp4")
#knn = cv2.ml.KNearest_load('mnist_knn.xml')   # 載入模型

# cv2.namedWindow('Threshold Sliders')
def doNothing(x):
	pass
# cv2.createTrackbar('R', 'Threshold Sliders', 142, 255, doNothing)
# cv2.createTrackbar('delta', 'Threshold Sliders', 100, 200, doNothing)
# cv2.createTrackbar('R-B_thresh', 'Threshold Sliders', 128, 255, doNothing)
#cv2.createTrackbar('R-G+100', 'Threshold Sliders', 100, 200, doNothing)
sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
blur_kernel = np.ones((3,3),np.float32)/9
frame_count = 0


is_tracing = False
last_time_tracing = -1
img_count = 8

while(True):
	frame_count += 1
# for i in range(1):
	# Get one frame from the camera
	ret, frame = cap.read()

	height, width, layers = frame.shape
	frame = cv2.resize(frame, (int(width/2), int(height/2)))


	b,g,r = cv2.split(frame)
	zeros = np.zeros(frame.shape[:2], dtype="uint8")

	# thresR = cv2.getTrackbarPos('R', 'Threshold Sliders')
	thresR = 10
	thresB = 10
	# thresB = thresR - cv2.getTrackbarPos('delta', 'Threshold Sliders')+100
	# thresRmB = cv2.getTrackbarPos('R-B_thresh', 'Threshold Sliders')+100
	# thresG = thresR - cv2.getTrackbarPos('R-G+100', 'Threshold Sliders')+100


	_, r = cv2.threshold(r, thresR, 255, cv2.THRESH_BINARY)
	# _, g = cv2.threshold(g, thresG, 255, cv2.THRESH_BINARY)
	_, b = cv2.threshold(b, thresB, 255, cv2.THRESH_BINARY)

	# cv2.imshow("Red", cv2.merge([zeros, zeros, r]))
	# cv2.imshow("Green", cv2.merge([zeros, g, zeros]))
	# cv2.imshow("Blue", cv2.merge([b, zeros, zeros]))
	
	RminusB = cv2.bitwise_and(r, cv2.bitwise_not(b), mask=None)
	RminusB = cv2.GaussianBlur(RminusB, (5, 5), 0)
	RminusB = cv2.threshold(RminusB, 10, 255, cv2.THRESH_BINARY)[1]
	# cv2.imshow("R-B", cv2.merge([RminusB, RminusB, RminusB]))

	contours, hierarchy = cv2.findContours(RminusB,
	cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# Draw the contours (for debugging)
	display = cv2.cvtColor(RminusB, cv2.COLOR_GRAY2BGR) 
	cv2.drawContours(display, contours, -1, (0,0,255))
	circle_count = 0
	for cnt in contours:
	# Calculate the area of the contour
		area = cv2.contourArea(cnt) 
		# Find the centroid
		(x,y), radius = cv2.minEnclosingCircle(cnt)
		if radius < 15:
			cv2.circle(display, (int(x), int(y)), int(radius), (0,0,0), -1)
			continue
		circle_count += 1
		# if circle_count > 1:
		# 	print("Noise")
		# 	break
		cv2.circle(display, (int(x), int(y)), int(radius), (0, 0, 0), -1)
		cv2.circle(display, (int(x), int(y)), int(radius/3), (255,255,255), -1)
		# cv2.circle(display, (int(x), int(y)), int(radius), (255,255,255), -1)
		# print("x: ", x, "y: ", y, "radius: ", radius)
		if is_tracing:
			digit_images = cv2.bitwise_or(digit_images, RminusB)
			last_time_tracing = frame_count
		else:
			digit_images = np.zeros(frame.shape[:2], dtype="uint8")
			digit_images = cv2.bitwise_or(digit_images, RminusB)
			is_tracing = True
			last_time_tracing = frame_count
	if circle_count == 0 and frame_count - last_time_tracing > 10 and is_tracing:
		is_tracing = False
		digit_images = cv2.flip(digit_images, 1)
		
		### KNN
		# img_num = digit_images.copy()		 # 複製image
		# img_num = img_num[45:, 200:]          # 擷取辨識的區域(因為原圖嚴重右移，會影響辨識率)

		# img_num = cv2.resize(img_num,(28,28))   # 縮小成 28x28，和訓練模型對照
		# cv2.imwrite("./images/digit_test_images_" + str(img_count) + ".png", img_num)	# 儲存辨識影像以確認影響調整無誤

		# img_num = img_num.astype(np.float32)    # 轉換格式
		# img_num = img_num.reshape(-1,)          # 打散成一維陣列資料，轉換成辨識使用的格式
		# img_num = img_num.reshape(1,-1)
		# img_num = img_num/255
		# img_pre = knn.predict(img_num)          # 進行辨識
		# num = str(int(img_pre[1][0][0]))        # 取得辨識結果
		# print(num, img_count)

		###CNN
		img_digit = digit_images.copy()
		img_digit = img_digit[45:, 200:] 
		# 調整影像為模型輸入大小
		img_digit = cv2.resize(img_digit, (INPUT_W, INPUT_H), interpolation=cv2.INTER_AREA)
		cv2.imwrite("./images/digit_test_images_" + str(img_count) + ".png", img_digit)	# 儲存辨識影像以確認影響調整無誤
		# 做預測
		interpreter.set_tensor(input_details[0]['index'], np.expand_dims(img_digit, axis=0))
		interpreter.invoke()
		predicted = interpreter.get_tensor(output_details[0]['index']).flatten()
			
		# 讀取預測標籤及其概率
		label = predicted.argmax(axis=0)
		prob = predicted[label]
			
		# 若概率低於門檻就忽略之
		if prob < 0.5:
			continue
		# 印出預測結果、概率與數字的位置
		print(f'Detected digit: [{label}] ({prob*100:.3f}%)',img_count)

		cv2.imwrite("./images/digit_images_" + str(img_count) + ".png", digit_images)
		img_count += 1
		# cv2.imshow("digit_images", digit_images)
		# cv2.waitKey(0)
		# print(area,(x,y), radius)
		# cv2.putText(display, str((x,y)), (int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX, 10, color=(0,255,0))
	cv2.imshow("display", display)
	# Split RGB channels


	# Perform thresholding to each channel


	# Get the final result using bitwise operation


	# Find and draw contours


	# Iterate through each contour, check the area and find the center


	# Show the frame
	# cv2.imshow('frame', frame)
	# Press q to quit
	# cv2.waitKey(0)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# Release the camera
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
