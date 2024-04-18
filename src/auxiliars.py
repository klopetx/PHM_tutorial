import pandas as pd
import numpy as np
import os
import re
import plotly.graph_objects as go

def concatenate_files(directory_path, file_prefix, one_in=1, parse_filename = False):
    """
    Concatenates files in the specified directory that start with the given prefix into a single DataFrame,
    selecting files according to the 'one_in' parameter. Logs the number of listed and read files.

    Parameters:
    - directory_path (str): The path to the directory containing the files.
    - file_prefix (str): The prefix of the files to be concatenated (e.g., 'acc_' or 'temp_').
    - one_in (int): Interval of files to be read. For example, one_in=2 reads every second file.

    Returns:
    - pd.DataFrame: A DataFrame containing the concatenated data from the selected files.
    """

    concatenated_df = pd.DataFrame()
    files_to_read = [filename for filename in os.listdir(directory_path) if filename.startswith(file_prefix)]
    files_to_read.sort()  # Ensure files are processed in order
    print(f"Total number of listed files with prefix '{file_prefix}': {len(files_to_read)}")

    files_read = 0  # Initialize counter for the number of files actually read
    for i, filename in enumerate(files_to_read):
        if i % one_in == 0:  # Process file based on one_in interval
            file_path = os.path.join(directory_path, filename)
            temp_df = pd.read_csv(file_path, header = None)

           # Parse filename and extract additional information if parse_filename is True
            if parse_filename:
                temp_df['OP_Condition'] = re.search(r'Bearing(\d+)_', file_path).group(1)
                temp_df['OPC_Test_Number'] = re.search(r'Bearing\d+_(\d+)', file_path).group(1)
                temp_df['Test_Index'] = pd.to_numeric(re.search(rf'(\d+).csv', file_path).group(1), errors = 'coerce')
           
            temp_df['file_name'] = file_path
            concatenated_df = pd.concat([concatenated_df, temp_df], ignore_index=True)
            files_read += 1  # Increment the counter

    print(f"Number of files read (based on one_in={one_in}): {files_read}")

    return concatenated_df


def compute_features(df, column_index, indicators, parse_filename = False):
    """
    Calculate specified features for a given column in a DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the data.
    - column_index (int): The index of the column to calculate features for.
    - indicators (dict): A dictionary mapping feature names to functions that calculate them.

    Returns:
    - pd.DataFrame: A DataFrame with the calculated features.
    """

    # Ensure column_index is within DataFrame range
    if column_index >= len(df.columns) or column_index < 0:
        raise ValueError("column_index is out of range.")

    # Calculate features
    grouped = df.groupby('file_name')
    features = grouped.apply(lambda x: pd.Series({name: func(x.iloc[:, column_index]) for name, func in indicators.items()})).reset_index()
    
    if parse_filename:
      features['OP_Condition'] = features['file_name'].str.extract(r'Bearing(\d+)_')[0]
      features['OPC_Test_Number'] = features['file_name'].str.extract(r'Bearing\d+_(\d+)')[0]
      features['Bearing'] = features['file_name'].str.extract(r'(Bearing\d+_\d+)')[0]
      test_index = features['file_name'].str.extract(r'(\d+).csv')[0]
      features['Test_Index'] = pd.to_numeric(test_index, errors='coerce')


    return features


def plot_fft_series_interactive(all_data, file_names, column_index, fs):
    """
    Interactively plots FFT of values for the specified column in 'all_data', grouped by 'file_name',
    with '/content/PHM_tutorial/data/10. FEMTO Bearing/' removed from the file names in the legend.

    Parameters:
    - all_data (pd.DataFrame): DataFrame containing the data.
    - file_names (list of str): List of file names to plot FFTs for.
    - column_index (int): Index of the column to plot FFT for.
    - fs (int): Sampling frequency of the signal.
    """
    fig = go.Figure()
    prefix_to_remove = "/content/PHM_tutorial/data/10. FEMTO Bearing/"

    for file_name in file_names:
        cleaned_file_name = file_name.replace(prefix_to_remove, "")  # Remove the prefix
        signal = all_data[all_data['file_name'] == file_name].iloc[:, column_index].values
        fft_result = np.fft.fft(signal)
        fft_freq = np.fft.fftfreq(len(signal), d=1/fs)

        # The previous mask removed non-positive values, but we want positive frequencies, so invert the mask
        mask = fft_freq > 0  # This will now create a mask for positive frequencies

        fig.add_trace(go.Scatter(x=fft_freq[mask], y=np.abs(fft_result)[mask],
                                 mode='lines', name=cleaned_file_name))

    fig.update_layout(title='FFT Plot by File Name',
                      xaxis_title='Frequency (Hz)',
                      yaxis_title='Magnitude',
                      legend_title="File Names")
    fig.update_xaxes(range=[0, fs/2])  # Set x-axis range to only show positive frequencies
    fig.show()
