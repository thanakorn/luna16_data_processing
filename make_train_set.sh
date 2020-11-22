sudo apt-get install p7zip-full

mkdir data

echo "Downloading Annotations"
wget https://zenodo.org/record/3723295/files/annotations.csv -P ./data/

for i in 0 1 2 3 4 5 6
do
  echo 'Downloading subset$i'
  wget https://zenodo.org/record/3723295/files/subset$i.zip -P ./data/
  7z x ./data/subset$i.zip
  mv subset$i ./data/
  rm ./data/subset$i.zip
done

mkdir /content/train_raw
cp ./data/annotations.csv /content/train_raw/
for i in 0 1 2 3 4 5 6
do
  rsync -vau --remove-source-files ./data/subset$i/ /content/train_raw/
done

python to_coco_format.py --set_name=train --data=/content/train_raw --output=/content/LUNA --num_processes=4
rm -rf /content/train_raw