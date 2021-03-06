import ee
import os
import geojson
import requests
import time
from PIL import Image
import argparse
ee.Initialize()


def get_images(location, start_date, end_date):
    #Program starts 

    if os.path.exists("Images/") is False:
        os.mkdir("Images/")

    start = time.time()
    filename = location + ".geojson"

    with open("Locations\\" + filename) as f:
        gj = geojson.load(f)

    coords = gj['features'][0]['geometry']['coordinates']
    aoi = ee.Geometry.Polygon(coords)


    ffa_db = (ee.ImageCollection('COPERNICUS/S1_GRD')
                        .filter(ee.Filter.eq('instrumentMode', 'IW'))
                        .filterBounds(aoi)
                        .filterDate(ee.Date(start_date), ee.Date(end_date))
                        .sort('system:time_start'))


    im_list = ffa_db.toList(ffa_db.size())
    size = ffa_db.size().getInfo()

    mode = "VH"

    if mode == "VV":
        min_vision = -25
        max_vision = 10
    elif mode == "VH":
        min_vision = -20
        max_vision = 0

    acq_times = ffa_db.aggregate_array('system:time_start').getInfo()
    dates = [time.strftime("-%Y%m%d-%H%M%S", time.gmtime(acq_time/1000)) for acq_time in acq_times]

    images_path = r"Images"

    if os.path.exists("Images/" + location) is False:
        os.mkdir("Images/" + location)

    for i,date in enumerate(dates):
        url = ee.Image(im_list.get(i)).select(mode).clip(aoi).getThumbURL({'min': min_vision, 'max': max_vision})

        img_data = requests.get(url).content
        info_img = str(i+1) + date+ '.png'
        img_name = os.path.join(images_path, location, f"{location}_{info_img}" )
        #img_name = r'Images/Shenzhen bay/Shenzhen_' + str(i+1) + date+ '.png'
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
            RGB = Image.open(img_name).convert('RGB').save(img_name)

    end = time.time()
    minutes = (end -start)/60

    format_minutes = "{:.2f}".format(minutes)

    print(f"The program finished in {format_minutes} minutes")

def main():
        # Create the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--location', type=str, required=True) #YYYY-MM-DD
    parser.add_argument('--start_date', type=str, required=True)
    parser.add_argument('--end_date', type=str, required=True)
    # Parse the argument
    args = parser.parse_args()

    location = args.location
    start_date = args.start_date
    end_date = args.end_date

    get_images(location, start_date, end_date)

if __name__ == "__main__":
    main()