from pathlib import Path
import pandas as pd
import numpy as np
import re

def calculate_bearing_indicators(df, signal_index, rotating_speed, sampling_frequency, deltaF):
    # Constants from bearing data
    Nb = 13  # Number of rolling elements
    Bd = 3.5  # Diameter of rolling elements in mm
    D = 25.6  # Bearing mean diameter in mm
    alpha = 0  # Contact angle, assuming 0 for simplification

    # Calculate the fundamental train frequencies
    BPFO = (Nb / 2) * (1 - Bd / D * np.cos(alpha)) * rotating_speed
    BPFI = (Nb / 2) * (1 + Bd / D * np.cos(alpha)) * rotating_speed
    BSF = (D / (2 * Bd)) * (1 - (Bd / D * np.cos(alpha))**2) * rotating_speed

    # Extract the signal from the DataFrame
    signal = df.iloc[:, signal_index]

    # Compute the FFT
    n = len(signal)
    freqs = np.fft.rfftfreq(n, 1/sampling_frequency)
    fft_values = np.fft.rfft(signal)

    # Global indicators

    # Mean of the signal
    mean = np.mean(signal)

    # Standard deviation of the signal
    std_dev = np.std(signal)

    # RMS (Root Mean Square) value of the signal
    rms = np.sqrt(np.mean(signal**2))

    # Peak value of the signal
    peak = np.max(np.abs(signal))

    # Peak-to-Peak value of the signal
    peak_to_peak = np.ptp(signal)  # Max - Min

    # Skewness of the signal
    skewness = pd.Series(signal).skew()

    # Kurtosis of the signal
    kurtosis = pd.Series(signal).kurtosis()

    # Crest factor (Peak value divided by RMS value)
    crest_factor = peak / rms if rms != 0 else None

    # Form factor (RMS value divided by the absolute mean value)
    form_factor = rms / np.mean(np.abs(signal)) if np.mean(np.abs(signal)) != 0 else None

    # Impulse factor (Peak value divided by the absolute mean value)
    impulse_factor = peak / np.mean(np.abs(signal)) if np.mean(np.abs(signal)) != 0 else None

    # Margin factor (Peak value divided by the sum of the absolute mean value and three times the standard deviation)
    margin_factor = peak / (np.mean(np.abs(signal)) + 3 * std_dev) if (np.mean(np.abs(signal)) + 3 * std_dev) != 0 else None

    # Calculate the magnitude of the FFT
    fft_magnitude = np.abs(fft_values)

    # Calculate the power spectral density (PSD)
    psd = np.square(fft_magnitude) / n

    # Calculate the total energy in the frequency domain
    total_energy = np.sum(psd)

    # Find the frequency corresponding to the maximum power
    max_power_freq = freqs[np.argmax(psd)]

    # Calculate the spectral centroid (weighted mean of the frequencies)
    spectral_centroid = np.sum(freqs * psd) / np.sum(psd)

    # Calculate the spectral bandwidth (standard deviation of the frequency distribution)
    spectral_bandwidth = np.sqrt(np.sum(psd * ((freqs - spectral_centroid) ** 2)) / np.sum(psd))

    # Calculate the spectral flatness (a measure of noise-like vs tone-like aspects of the signal)
    spectral_flatness = 10.0 * np.log10(np.exp(np.mean(np.log(psd + 1e-10))) / np.mean(psd + 1e-10))

    # Calculate the spectral roll-off (frequency below which a specified percentage of the total spectral energy lies)
    roll_off_threshold = 0.85 * total_energy
    cumulative_energy = np.cumsum(psd)
    spectral_roll_off = freqs[np.where(cumulative_energy >= roll_off_threshold)[0][0]]

    # Function to find the maximum and RMS value in the frequency window
    def find_max_and_rms(frequencies, fft_data, target_freq, window):
        # Find the indices of the window around the target frequency
        indices = (frequencies >= (target_freq - window)) & (frequencies <= (target_freq + window))
        window_fft_values = fft_data[indices]
        max_value = np.max(np.abs(window_fft_values))
        rms_value = np.sqrt(np.mean(np.abs(window_fft_values)**2))
        return max_value, rms_value

    # Compute max and RMS values for each frequency
    indicators = {
        'Mean': mean,
        'Standard Deviation': std_dev,
        'RMS': rms,
        'Peak': peak,
        'Peak-to-Peak': peak_to_peak,
        'Skewness': skewness,
        'Kurtosis': kurtosis,
        'Crest Factor': crest_factor,
        'Form Factor': form_factor,
        'Impulse Factor': impulse_factor,
        'Margin Factor': margin_factor,
        'Total Energy': total_energy,
        'Max Power Frequency': max_power_freq,
        'Spectral Centroid': spectral_centroid,
        'Spectral Bandwidth': spectral_bandwidth,
        'Spectral Flatness': spectral_flatness,
        'Spectral Roll-off': spectral_roll_off,
        'BPFO_max': find_max_and_rms(freqs, fft_values, BPFO, deltaF)[0],
        'BPFO_rms': find_max_and_rms(freqs, fft_values, BPFO, deltaF)[1],
        'BPFI_max': find_max_and_rms(freqs, fft_values, BPFI, deltaF)[0],
        'BPFI_rms': find_max_and_rms(freqs, fft_values, BPFI, deltaF)[1],
        'BSF_max': find_max_and_rms(freqs, fft_values, BSF, deltaF)[0],
        'BSF_rms': find_max_and_rms(freqs, fft_values, BSF, deltaF)[1]
    }

    # Create the output DataFrame
    output_df = pd.DataFrame(indicators, index = [0])

    return output_df
def process_duration_data(indicators):
  # Create a string representation of time
  indicators['time_str'] = indicators['Hour'].astype(str) + ':' + indicators['Minute'].astype(str) + ':' + indicators['Second'].astype(str)

  # Convert string to datetime
  indicators['Timestamp'] = pd.to_datetime( '2000-01-01 ' + indicators['time_str'])

  # Drop the temporary string column if not needed
  indicators = indicators.drop(columns=['time_str'])

  indicators['Duration'] = indicators.groupby('Bearing')['Timestamp'].transform(lambda x: (x - x.min()).dt.total_seconds())

  indicators = indicators.sort_values(by='Timestamp')

  return indicators

def detect_rotating_speed(OperatingCondition):

  rotatingSpeed = 1000

  if OperatingCondition == '1':
    rotatingSpeed = 1800
  elif OperatingCondition == '2':
      rotatingSpeed = 1650
  elif OperatingCondition == '3':
      rotatingSpeed = 1500

  return rotatingSpeed
def process_raw_signals(acc_path):

  metadata = parse_path_info(acc_path)

  rawdf = pd.read_csv(acc_path, header=None)

  timestampdata = pd.DataFrame({'Hour':rawdf.iloc[0,0], 'Minute':rawdf.iloc[0,1], 'Second':rawdf.iloc[0,2], 'Mili/centisecond':rawdf.iloc[0,3]}, index = [0])

  metadata = pd.concat([metadata, timestampdata], axis = 1)  

  acc_idx = 4
  sampling_frequency = 25600
  deltaF = 10


  rotating_speed = detect_rotating_speed(metadata.OperatingCondition[0])

  indicator_df = calculate_bearing_indicators(rawdf, 4, rotating_speed, sampling_frequency, deltaF)

  metaIndicator = pd.concat([metadata,indicator_df], axis = 1)

  return metaIndicator


def create_class_dataframe():
  # https://github.com/wkzs111/phm-ieee-2012-data-challenge-dataset/blob/master/IEEEPHM2012-Challenge-Details.pdf
    class_data = [
        {'Bearing': 'Bearing1_3', 'Actual_RUL': 5730},
        {'Bearing': 'Bearing1_4', 'Actual_RUL': 339},
        {'Bearing': 'Bearing1_5', 'Actual_RUL': 1610},
        {'Bearing': 'Bearing1_6', 'Actual_RUL': 1460},
        {'Bearing': 'Bearing1_7', 'Actual_RUL': 7570},
        {'Bearing': 'Bearing2_3', 'Actual_RUL': 7530},
        {'Bearing': 'Bearing2_4', 'Actual_RUL': 1390},
        {'Bearing': 'Bearing2_5', 'Actual_RUL': 3090},
        {'Bearing': 'Bearing2_6', 'Actual_RUL': 1290},
        {'Bearing': 'Bearing2_7', 'Actual_RUL': 580},
        {'Bearing': 'Bearing3_3', 'Actual_RUL': 820}
    ]
    class_data = pd.DataFrame(class_data)
    return class_data
def parse_path_info(path):
    # Use regular expressions to capture the required parts of the path
    origin_pattern = re.compile(r'/10\. FEMTO Bearing/(.*?)/')
    bearing_pattern = re.compile(r'Bearing(\d+)_(\d+)/')
    test_idx_pattern = re.compile(r'acc_(\d+)\.csv')
    bearing_full_pattern = re.compile(r'(Bearing\d+_\d+)')
    bearing_full_match = re.search(r'Bearing\d+_\d+', path)
    
    
    # Search the path using the compiled patterns
    origin_search = origin_pattern.search(path)
    bearing_search = bearing_pattern.search(path)
    test_idx_search = test_idx_pattern.search(path)
    bearing_full_search = bearing_full_pattern.search(path)

    # Extract the information if found
    origin = origin_search.group(1) if origin_search else None
    operating_condition = bearing_search.group(1) if bearing_search else None
    test_number = bearing_search.group(2) if bearing_search else None
    test_idx = test_idx_search.group(1) if test_idx_search else None
    bearing_full_search = bearing_full_search.group(1) if bearing_full_search else None
    
    # Create a DataFrame with the extracted information
    data = {
        'Origin': [origin],
        'Bearing': [bearing_full_search],
        'OperatingCondition': [operating_condition],
        'TestNumber': [test_number],
        'TestIdx': [test_idx]
    }
    df = pd.DataFrame(data)
    
    return df

# Path to the directory you want to search
directory_path = 'data/10. FEMTO Bearing/Full_Test_Set/'

# Create a Path object
path = Path(directory_path)

# List all CSV files in the directory and its subdirectories
csv_files = path.rglob('acc*.csv')

# Print the list of CSV files

masterDF = pd.DataFrame()

for file in csv_files:
    try:
      outdf = process_raw_signals(str(file))
      masterDF = pd.concat([masterDF, outdf], axis=0)
    except Exception as e:
      pass
        #print(f"Error processing file {file}: {e}")


masterDF.reset_index(drop=True, inplace=True)

masterDF = process_duration_data(masterDF) 
class_data = create_class_dataframe()
masterDF = masterDF.merge(class_data, on= 'Bearing', how = 'left')
masterDF['RUL'] = masterDF['Actual_RUL'] - masterDF['Duration']
masterDF['Alive'] = masterDF['RUL'] > 0

masterDF.to_csv('data/indicators.csv', sep='\t', encoding='utf-8', index=False)


