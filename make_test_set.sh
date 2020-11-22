sudo apt-get install p7zip-full

mkdir data

echo "Downloading Annotations"
wget https://zenodo.org/record/3723295/files/annotations.csv -P ./data/

for i in 7 8 9
do
  echo 'Downloading subset$i'
  wget https://zenodo.org/record/3723299/files/subset$i.zip -P ./data/
  7z x ./data/subset$i.zip
  mv subset$i ./data/
  rm ./data/subset$i.zip
done

mkdir /content/test_raw
cp ./data/annotations.csv /content/test_raw/
for i in 7 8 9
do
  rsync -vau --remove-source-files ./data/subset$i/ /content/test_raw/
done

python to_coco_format.py --set_name=test --data=/content/test_raw --output=/content/LUNA --num_processes=4
rm -rf /content/test_raw