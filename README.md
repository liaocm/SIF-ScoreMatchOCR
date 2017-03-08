# SIF-ScoreMatchOCR
This script allows you to get a rough guess of score match points, the change of that points, total score and combo for each player. All you need to do is to provide a "good" screenshot, meaning that the "FULL COMBO" mark cand be at most as large as the ones in the test data set. Any screenshot with a mark larger than that of the test data set will contaminate combo data and the script will fail.

## Prerequisites:

Python 3+

PIL (Pillow) 

tesseract

pytesseract


## Usage

./ocr.py path-to-screenshot

Note that the resolution of the screenshot must be at least 1080x720. Any screenshot smaller than that significantly reduces the accuracy and thus is not allowed.

## Output

A json string with raw interpreted data and final, sanitized data.

## Example

$ ./ocr.py test/test-noisy.png

{"raw": [["22485pt", "(+154)", "582081", "415"], ["22904pt", "(+99)", "487499", "415"], ["22079:\u201c", "(- 31)", "489693", "415"], ["22015!\u201d", "(-52)", "464581", "219"]], "sanitized": [[22485, 154, 582081, 415], [22904, 99, 487499, 415], [22079, -31, 489693, 415], [22015, -52, 464581, 219]]}