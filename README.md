# Preprocessing
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

## Microservices
The module offers two microservices that responds to POST method:

* One for processing a PDF

INPUT:
```
{
  name: string,
  payload: string,
  contrastFactor: int,
  applyNoiseReduction: bool,
  segmentationFactor: int
}
```
  The name is the name of the PDF and the payload is PDF's content. The next 3 parameters are optional. 
  
  ContrastFactor has a default value of 1.5 and it is between 1 and 3. It represents the ration between the text color intensity and the background color intensity.
  
  ApplyNoiseReduction can be false or true, by default it is false. If set, it reduces the noise of the image, but doubles the execution time.
  
  SegmentationFactor is between 0.3 and 0.7. Higher value reduce the risk of characters placed on consecutive lines to be selected togheter, but increases the chances to exclude detection of characters such "'" or dot of the "i".
  
OUTPUT:
```
{
  names: string[],
  payloads: string[],
  coords: int[][]
}
```
  It returns the names of the resulted images with their content. The first image of the list is preprocessed(back-white) and the coordinates(upper-left and lower-right) of each character is stored in coords, which is a list of borders.



* One for processing an image

INPUT:
```
{
  name: string,
  payload: string,
  contrastFactor: int,
  applyNoiseReduction: bool,
  segmentationFactor: int
}
```

The name is the name of the image and the payload is images's content. The next 3 parameters are optional and are explained above. 

OUTPUT:
```
{
  name: string,
  payload: string,
  coords: int[][]
}
```

It returns the name of the preprocessed image and it's content in black-white. The coords is a list of points which represents the bordes of each character detected.

  
  
