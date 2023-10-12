from PIL import ImageGrab
import pytesseract
import pandas as pd

# If you haven't added Tesseract to PATH, specify its location here
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_screenshot_with_location():
    # Capture screenshot
    screenshot = ImageGrab.grab()

    # Perform OCR on the screenshot and get detailed data
    data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DATAFRAME)

    # Filter rows with non-empty text
    valid_rows = data[data['text'].notnull() & (data['text'] != ' ')]

    # Extract text and its location (bounding box)
    extracted_data = []
    for _, row in valid_rows.iterrows():
        extracted_data.append({
            'text': row['text'],
            'x': row['left'],
            'y': row['top'],
            'width': row['width'],
            'height': row['height']
        })

    return extracted_data

if __name__ == '__main__':
    extracted_data = ocr_screenshot_with_location()
    for item in extracted_data:
        print(f"Text: {item['text']}, Location: (X: {item['x']}, Y: {item['y']}, Width: {item['width']}, Height: {item['height']})")
