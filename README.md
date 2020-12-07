# Luna16 Data Processing

### Making dataset for training object detection model

#### Manually
1. Download the zip files
2. Extract **.raw** and **.mhd** files to a specific folder
3. Download the annotation file and put into the same folder
4. Run **to_coco_format.py** to extract data:

`python to_coco_format.py --set_name={set_name(fe. train/test)} --data={data_dir} --output={output_dir} --num_processes={num_process}`

Arguments:
* set_name = name of the json annotation file that the script will produce(fe. train.json)
* data_dir = raw data folder
* output_dir = output folder(relative path)
* num_processes = number of process to use

#### Using shell script
The scripts **make_train_set.sh** and **make_test_set.sh** do all the manual steps in one command. By executing `sh make_train_set.sh`(or `sh make_test_set.sh`), the raw data will be downloaded into `./data` folder and the processed output will be put into `./dataset` folder with the annotation file name `train.json`(`test.json` for **make_test_set.sh**).

*NOTE: By default, the train set is composed of subset 0-6 of LUNA dataset while the test set is subset 7 - 9.*
