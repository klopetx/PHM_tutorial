# PHM_tutorial

A small repository that helps you understand the basics about prognostics and health management (PHM) by using Python and the an open dataset known as FEMTO Bearings.

## Disclaimer

Please, forgive the code quality, this repo just aims to teach the whys not to show how to program. 

## Index 

- [1) Raw Signal visualization](src/01_Raw_singal_vis.ipynb): Combining data and visualizing the raw signals of the tests.
- [2a) Feature extraction: Time domain](src/02.A_Feature_Extraction_I_time_domain.ipynb): Extracting indicator directly over the raw signal.
- [2b) Feature extraction: Frequency domain](src/02.B_Feature_Extraction_II_frequency.ipynb): Working a bit with frequency domain indicators and the fft.
- [2c) Feature extraction: Time-frequency domain](src/02.C_Feature_Extraction_III_time-frequency.ipynb): Small example of the Short Time Fourier Transform.
- [3. Feature selection](src/03_Feature_selection.ipynb): Some examples on how to select interesting features for modelling.
- [4. RUL Model](src/04_Modelling.ipynb): Building a model to compute the Remaining Useful Life of an asset. 
 
# Interesting links

## About the dataset

[FEMTO explanations](https://yanncalec.github.io/dpmhm/datasets/femto/)

[Challenge paper](https://hal.science/hal-00719503/file/PHM33.pdf)

[Challenge details](https://github.com/wkzs111/phm-ieee-2012-data-challenge-dataset/blob/master/IEEEPHM2012-Challenge-Details.pdf)
