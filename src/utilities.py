from PIL import Image

def FileToImage(inputPath):
    inp = Image.open(inputPath)
    return inp

def ImageToFile(image, outputPath):
    image = image.convert("RGB")
    image.save(outputPath)
