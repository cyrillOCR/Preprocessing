# Preprocessing . 
Preprocessing module for cyrillOCR

## Dependencies:
* pillow
```python
pip install Pillow
```

* open-cv

```python
pip install opencv-python
```

* argparse

```python
pip install argparse
```

* pypdf2

```python
pip install PyPDF2
```

* pdf2image

```python
pip install pdf2image
```

* numpy 

```python
pip install numpy --user
```

* imageio 

```python
pip install imageio --user
```

* flask-CORS

```python
pip install -U flask-cors
```

* poppler from the following link https://poppler.freedesktop.org/ and include it in your PATH


## Microservices:
The module offers 3 microservices that responds to ```POST``` request:

* One for processing a PDF

INPUT:
```
{
  name: string,
  payload: string,
  contrastFactor: float,
  applyDilation: bool,
  applyNoiseReduction: bool,
  segmentationFactor: float,
  separationFactor: int
}
```
  The name is the name of the PDF and the payload is PDF's content encoded in base64. The next 3 parameters are optional. 
  
The contrastFactor parameter is used to apply a certain amount of contrast to the image. It is an exponential function, so the default value is one if you want the contrast to be unchanged. A subunitary value will decrease the contrast, while a supraunitary value will increase the contrast of the image. Usually a value between 1.5 and 3.0 is recommended. In our test cased we used 2.0.
  
  ApplyDilation can be true or false, by default is true. If set, it dilates and erosions the characters, making them more clear and improve detection of characters with discontinuous lines such as 'N' or 'K', but has long execution time.
  
  ApplyNoiseReduction can be false or true, by default it is false. If set, it totally removes the noise of the image, making it sharp and clear but increases the execution time.
  
  SegmentationFactor is between 0.3 and 0.7. Higher value reduce the risk of characters placed on consecutive lines to be selected togheter, but increases the chances to exclude detection of characters placed on upper and lower bound of the line such as "'" or dot of the "i".For most case scenarios we recommend using 0.45 value.
  
  SeparationFactor is between 2 and 4, depending on the image resolution. It represents the maximum distance in pixels for which two separate consecutive characters can be joined. By default is 3 pixels. It is used to improve detection of characters that are altered by conversion to black-white.
  
OUTPUT:
```
{
  names: string[],
  payloads: string[],
  pName: string,
  pPayload: string
  coords: int[][]
}
```
  It returns the names of the resulted images with their content from the PDF encoded in base64. Pname is the name of the first image which is preprocessed(black-white) and the coordinates(upper-left and lower-right) of each character is stored in coords, which is a list of borders.



* One for processing an image

INPUT:
```
{
  name: string,
  payload: string,
  contrastFactor: float,
  applyDilation: bool,
  applyNoiseReduction: bool,
  segmentationFactor: float,
  separationFactor: int
}
```

The name is the name of the image and the payload is images's content encoded in base64. The next 3 parameters are optional and are explained above. 

OUTPUT:
```
{
  name: string,
  payload: string,
  coords: int[][]
}
```

It returns the name of the preprocessed image and it's content in black-white encoded in base64. The coords is a list of points which represents the bordes of each character detected.


* One to convert a pdf to images

INPUT:
```
{
  name: string,
  payload: string
}
```
It receives the name of the pdf and it's content in payload.

OUTPUT:
```
{
  names: string[],
  payloads: string[]
}
```

It returns a list of images names and their corresponding content.
  

## Installing a flask server for Python 3, using Windows
### The easy way:
  1. Install & open Pycharm
  2. Create a new project
  3. Select Flask
  4. Open Project Interpreter
  5. New environment using Virtualenv
  6. Go to settings -> Project: __ProjectName__
  7. Add the required dependencies
  8. Run
  9. Consult the documentation to learn : http://flask.pocoo.org/docs/1.0/tutorial/
  
### The harder way
  1. Create a folder for the Flask server
  2. Open CMD
  3. Go to the created folder using ```cd```
  4. Create a new virtual environment ```py -m venv venv```
  5. Activate the virtual environment ```venv\Scripts\activate```
  6. Install Flask ```py -m pip install Flask```
  7. Create a file ```app.py``` in the root of the project with this content:
  ```
  from flask import Flask
  app = Flask(__name__)
  @app.route('/')
  def hello():
      return 'Hello, World!'
  if(__name__=='__main__'):
	  app.run()
  ```
  8. Run ```app.py``` with Python
  9. To run again after you close the cmd, you need to redo the steps 2,3,5,8
  10. To install modules/packages you need to have the virtual envionment actiavated
  11. Consult the documentation to learn : http://flask.pocoo.org/docs/1.0/tutorial/

