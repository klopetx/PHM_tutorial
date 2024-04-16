import os

femto_dir = os.path.join("data", "10. FEMTO Bearing")
project_dir = "/content/PHM_tutorial"

if not os.path.isdir(femto_dir):
  print("The '10. FEMTO Bearing' directory does not exist inside 'data'" )

  if os.getcwd() == project_dir:
    print("Runnning data download...")
    import subprocess
    subprocess.run(['python', 'src/00_data_download.py'])
    print("FEMTO downloaded")

  else:
    print("Current working diretory is" + os.getcwd())
    print("Please, change the working directory to: " + project_dir)
else:
  print('FEMTO dataset is already downloaded.')
