import os
import json
import requests
from ..utils.ocrTools import _check_image_file, cv2_to_base64

def format_ocr_result(ocr_result):
    formatted_result = []
    for item in ocr_result:
        text = item[0][0]
        confidence = item[0][1]
        coordinates = item[1]
        formatted_result.append({
            'text': text,
            'confidence': confidence,
            'text_region': coordinates
        })
    return formatted_result

def perform_ocr(img_path_list):
    url = "http://127.0.0.1:9998/ocr/prediction"
    ocr_results = []  # List to store results from all images

    for img_file in img_path_list:
        with open(img_file, 'rb') as file:
            image_data = file.read()

        image = cv2_to_base64(image_data)
        data = {"key": ["image"], "value": [image]}
        response = requests.post(url=url, data=json.dumps(data))
        result = response.json()

        if result["err_no"] == 0:
            ocr_result = eval(result["value"][0])
            formatted_res = format_ocr_result(ocr_result)
            ocr_results.append({
                'file': img_file,
                'ocr_result': formatted_res
            })
        else:
            print("Error processing file {}: {}".format(img_file, result["err_msg"]))

    return ocr_results

