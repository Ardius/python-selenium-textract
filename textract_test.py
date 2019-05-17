import boto3
from selenium import webdriver
from statistics import mean
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

def find_average_pixel(width,height,blocks,text,type):
    for block in blocks:
        if block['BlockType'] == type and block['Text'] == text and block['Confidence'] > 98:
            pixel_area = block['Geometry']['Polygon']
            x_location_array = []
            y_location_array = []
            for pixel in pixel_area:
                x_location_array.append(pixel['X'])
                y_location_array.append(pixel['Y'])
            #Use mean value to find the centre of the rectangle
            mean_x = mean(x_location_array)
            mean_y = mean(y_location_array)
            #As the x and y values are ratios, they need to be converted to a pixel location
            x_pixel = mean_x * width
            y_pixel = mean_y * height
            return x_pixel,y_pixel
    print("Could not find text")

if __name__ == "__main__":

    #Setup Webdriver, navigate to a page and take a screenshot
    driver = webdriver.Firefox()
    width = 800
    height = 600
    driver.set_window_size(width, height)
    driver.get("https://google.com")
    screenshot = driver.get_screenshot_as_png()

    #Send the screenshot to AWS Textract
    client = boto3.client('textract')
    response = client.detect_document_text(Document={'Bytes': screenshot})
    blocks = response['Blocks']

    #Analyse response and find the location for a given text string
    x,y = find_average_pixel(width,height,blocks,"Store","WORD")

    #Tell the browser to click the location via Javascript
    script = 'el = document.elementFromPoint(%d, %d); el.click();'%(x,y)
    driver.execute_script(script)

    #Check to see if we successfully navigated to the correct page
    try:
        WebDriverWait(driver, 10).until(expected_conditions.title_contains("Google Store"))
        print("Yay it worked")
    except TimeoutException:
        print("It didn't work")

    driver.close()
