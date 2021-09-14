import datetime
import time

import numpy as np

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from preprocess import process_image_for_ocr
import cv2



if __name__ == '__main__':
    url = 'https://123news.tv/cnbc-live-stream/'
    options = Options()
    options.add_argument("--window-size=1920,1080");
    options.add_argument("--headless");
    options.add_argument("--mute-audio")

    driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
    driver.get(url)
    driver.maximize_window()
    driver.execute_script("window.scrollTo(0, 250)")

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="player"]/div/div[1]/div[2]/div'))).click()
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    for i in range(5):
        if i == 0:
            print('* Waiting for stream to load...')
        time.sleep(1)
        print('\t' + str(5-i) + '...')

    count = 0
    while True:
        path_pic = './current_screen/curr.png'
        driver.save_screenshot(path_pic)
        cropped = Image.open(path_pic)
        # Size of the image in pixels (size of original image)
        width, height = cropped.size

        # Setting the points for cropped image
        left = 55
        top = height / 6 + 20
        right = 1350
        bottom = height - 200

        # Cropped image of above dimension
        # (It will not change original image)
        cropped = cropped.crop((left, top, right, bottom))
        cropped.save(path_pic)
        print('\n------------------------\n* Cropped image')
        # Load .png image
        image = cv2.imread(path_pic)

        # Save .jpg image
        cv2.imwrite('./current_screen/curr.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        print('* PNG -> JPG')

        # Test pic
        # image2 = cv2.imread(r'C:\Users\Brennan\Desktop\headline.jpg')
        img = cv2.resize(image, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        cv2.threshold(cv2.bilateralFilter(img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                              31, 2)

        cv2.adaptiveThreshold(cv2.bilateralFilter(img, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                              cv2.THRESH_BINARY, 31, 2)

        cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
        cv2.imwrite('./current_screen/processed.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        print('* Preprocessing complete')

        cropped = Image.open('./current_screen/processed.jpg')
        # Size of the image in pixels (size of original image)
        width, height = cropped.size

        # Setting the points for cropped image
        left = 300
        top = 620
        right = 1140
        bottom = 740

        # Cropped image of above dimension
        # (It will not change original image)
        cropped = cropped.crop((left, top, right, bottom))
        cropped.save('./current_screen/processed.jpg')
        processed_cropped = cv2.imread('./current_screen/processed.jpg')
        text = pytesseract.image_to_string(processed_cropped)
        print(text)
        now = datetime.datetime.now()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        print(dt_string)

        count += 1
        #if count > 0:
        #    break
    print('* Closing driver')
    driver.close()
