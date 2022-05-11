import torch
import os
import numpy as np
from PIL import Image
from itertools import product
import shutil

import sys
print(sys.version)

def detect_vessels(filename, dir_in, dir_out, model): 
    d = 800
    name, ext = os.path.splitext(filename)
    img = Image.open(os.path.join(dir_in, filename))
    w, h = img.size

    divided_filenames = []

    grid = list(product(np.arange(0, h, d), np.arange(0, w, d)))
    for i, j in grid:
        jj, ii = w if j+d>w else j+d,  h if i+d>h else i+d
        box = (j, i, jj, ii)
        divided_filename = f"{name}_{i}_{j}_{ext}"
        out_file = os.path.join(dir_out, divided_filename)
        divided_filenames.append(divided_filename)
        img.crop(box).save(out_file)


    preprocess_files = [os.path.join(dir_out, filename) for filename in divided_filenames]   

    for folder in os.listdir("runs/detect"):
        shutil.rmtree(folder)

    # Inference
    results = model(preprocess_files)
    results.save()
    vessels_in_picture = sum([len(vessel_image) for vessel_image in results.xyxy])
    try:
        for file in preprocess_files:
            os.remove(file)
    except:
        pass

    detect_dir = r"runs/detect/exp"

    detect_filenames = [os.path.splitext(filename)[0] for filename in divided_filenames]
    detect_files = [os.path.join(detect_dir, filename+".jpg") for filename in detect_filenames]

    imgs = [Image.open(filename) for filename in detect_files]

    final_image = Image.new('RGB', size=(w, h))

    for picture in imgs:
        name, ext = os.path.splitext(picture.filename)
        i = int(name.split("_")[-3])
        j = int(name.split("_")[-2])

        final_image.paste(picture, box=(j, i))

    shutil.rmtree(detect_dir)
    (os.remove(file) for file in detect_files)
    out_filename = os.path.join(dir_out, f'{filename}')
    final_image.save(out_filename)

    return vessels_in_picture


def main():
    dir_in = r"Images\Shenzhen bay"
    dir_out = r"Images\Final"

    model = torch.hub.load('ultralytics/yolov5', 'custom', path=r"G:\Mi unidad\Data\Simulations\yolov5s\weights\best.pt", force_reload=True)

    filenames = os.listdir(dir_in)
    n_vessels = 0
    for filename in filenames:
        vessels_in_picture = detect_vessels(filename, dir_in, dir_out, model)
        n_vessels += vessels_in_picture

    print(f"{n_vessels} vessels have been detected")
    
if __name__ == "__main__":
    main()