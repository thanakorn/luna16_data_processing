import os
import json
import pandas as pd
import cv2 as cv
import concurrent.futures
import argparse
from tqdm import tqdm
from models.ct_image import CTImage
from concurrent.futures import ThreadPoolExecutor

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--data', type=str, default='./data')
argument_parser.add_argument('--output', type=str, default='./output')
argument_parser.add_argument('--set_name', type=str, default='annotations')
argument_parser.add_argument('--num_processes', type=int, default=1)

args = argument_parser.parse_args()
data_path = args.data
output_path = args.output
set_name = args.set_name
num_processes = int(args.num_processes)

def get_seriesuid(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def extract_CT_images(ct_filename):
    seriesuid = get_seriesuid(ct_filename)
    ct_img = CTImage(ct_filename)
    for s in range(ct_img.get_num_slice()):
        img_filename = f'{seriesuid}-{s}.jpg'
        full_filename = f'{output_path}/{img_filename}'
        img = cv.normalize(ct_img.get_slice(s), None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
        cv.imwrite(full_filename, img)

def get_nodule_pxl_location(seriesuid, coordXYZ, diameter_mm):
    ct_img = CTImage(f'{data_path}/{seriesuid}.mhd')
    coord_x, coord_y, coord_z = coordXYZ
    dx, dy = (int(diameter_mm / ct_img.get_x_space()), int(diameter_mm / ct_img.get_y_space()) )
    x, y, z = ct_img.get_pxl_localtion((coord_x, coord_y, coord_z))
    x_min, x_max = x - dx, x + dx
    y_min, y_max = y - dx, y + dy
    print(f'{seriesuid}-{z}.jpg')
    return x_min, y_min, x_max, y_max

if __name__=='__main__':
    
    thread_pool = ThreadPoolExecutor(num_processes)
    annotation = pd.read_csv(f'{data_path}/annotations.csv')
    nodules_log = open('./nodules_log.csv', 'w')
    nodules_log.write('seriesuid,slice\n')
    
    if not os.path.exists(f'{output_path}'): os.mkdir(f'{output_path}')
    
    print('Extract CTScan images')    
    input_files = list(filter(lambda filename: filename.endswith('.mhd'), os.listdir(data_path)))
    input_files = [f'{data_path}/{file}' for file in input_files]
    with tqdm(total=len(input_files), desc=f'Extract images') as pbar:
        for _ in thread_pool.map(extract_CT_images, input_files): pbar.update()
    
    print('Construct annotation file')
    images = []
    image_idx = {}
    detections = []
    for idx, filename in enumerate(filter(lambda filename: filename.endswith(('jpg', 'png', 'jpeg')), (os.listdir(output_path)))):
        height, width = cv.imread(os.path.join(output_path, filename)).shape[:2]
        images.append(dict(
            id=idx,
            file_name=filename,
            height=height,
            width=width
        ))
        image_idx[filename] = idx

    obj_count = 0
    for idx in annotation.index:
        seriesuid = annotation.loc[idx, 'seriesuid']
        try:
            ct_img = CTImage(f'{data_path}/{seriesuid}.mhd')
            coord_x, coord_y, coord_z, diameter_mm = annotation.loc[idx, 'coordX'], annotation.loc[idx, 'coordY'], annotation.loc[idx, 'coordZ'], annotation.loc[idx, 'diameter_mm']
            dx, dy = (int(diameter_mm / ct_img.get_x_space()), int(diameter_mm / ct_img.get_y_space()) )
            x, y, z = ct_img.get_pxl_localtion((coord_x, coord_y, coord_z))
            x_min, x_max = x - dx, x + dx
            y_min, y_max = y - dx, y + dy

            detections.append(dict(
                id=obj_count,
                image_id=image_idx[f'{seriesuid}-{z}.jpg'],
                category_id=0,
                bbox=[x_min, y_min, x_max - x_min, y_max - y_min],
                area=(x_max - x_min) * (y_max - y_min),
                segmentation=[], 
                iscrowd=0
            ))
            obj_count += 1
            
        except:
            pass

    # print(images[0:5])
    # print(detections[0:5])

    annotation_json = dict(
        images=images,
        annotations=detections,
        categories=[{'id':0, 'name': 'nodule'}]
    )
    with open(f'{output_path}/{set_name}.json', 'w') as f:
        json.dump(annotation_json, f)
    