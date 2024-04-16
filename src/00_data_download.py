import os
import urllib.request  # Import the urllib.request module
import zipfile

url = "https://phm-datasets.s3.amazonaws.com/NASA/10.+FEMTO+Bearing.zip"
filename = "data/FEMTOBearingDataSet.zip"

urllib.request.urlretrieve(url, filename)


def extract_zips(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall()


# Extract the outer zip file
os.chdir("data")

extract_zips("FEMTOBearingDataSet.zip")

# Change to the "10. FEMTO Bearing" directory
os.chdir("10. FEMTO Bearing")

# Extract the outer zip file again (assuming it's the same file)
extract_zips("FEMTOBearingDataSet.zip")

# Extract Training_set.zip
extract_zips("Training_set.zip")

# Extract Test_set.zip
extract_zips("Test_set.zip")

# Extract Validation_Set.zip
extract_zips("Validation_Set.zip")

os.chdir('../..')

# Remove all remaining .zip files
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".zip"):
            os.remove(os.path.join(root, file))
