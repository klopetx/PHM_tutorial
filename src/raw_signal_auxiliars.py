import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def process_acc_files(base_dir, first_only =True):

    # Initialize an empty DataFrame to concatenate all first 'acc' CSVs
    all_data = pd.DataFrame()

    # Traverse the directory structure
    for subdir, dirs, files in os.walk(base_dir):
        # Sort the files to ensure we are getting the first one when using 'acc' prefix
        sorted_files = sorted(files)
        for file in sorted_files:
            # Check if the file starts with 'acc' and is a CSV
            if file.startswith('acc') and file.endswith('.csv'):
                # Construct the full file path
                file_path = os.path.join(subdir, file)
                # Read the CSV file
                df = pd.read_csv(file_path, header=None)  # Assuming there is no header row

                # Parse the folder name to get the bearing name
                bearing_name = os.path.basename(subdir)

                # Add additional columns for 'bearing' and 'file_name'
                df['bearing'] = bearing_name
                df['file_name'] = file_path

                # Concatenate the individual dataframe to the main dataframe
                all_data = pd.concat([all_data, df], ignore_index=True)

                # Optionally break after adding the first 'acc' file
                if first_only:
                    break

    # Additional processing
    all_data.rename(columns={all_data.columns[4]: 'AccX', all_data.columns[5]: 'AccY'}, inplace=True)
    all_data['OP_Condition'] = all_data['bearing'].str.extract(r'Bearing(\d+)_')[0]
    all_data['OPC_Test_Number'] = all_data['bearing'].str.extract(r'Bearing\d+_(\d+)')[0]

    return all_data
  
def plot_time_series(all_data, file_names, column_index):
    """
    Plots values over time for the specified files and column index in 'all_data'.

    Parameters:
    - all_data (pd.DataFrame): DataFrame containing the data, including 'file_name' and data columns.
    - file_names (list of str): List of file names to plot.
    - column_index (int): Index of the column to plot.
    """

    # Filter rows for the specified file names
    files_to_print = all_data[all_data.file_name.isin(file_names)].copy()

    # Add a 'Time' column based on the order of rows within each file
    files_to_print['Time'] = files_to_print.groupby('file_name').cumcount() + 1

    # Generate unique colors for each file name
    colors = plt.cm.jet(np.linspace(0, 1, len(file_names)))

    plt.figure(figsize=(10, 5))  # Sets the figure size

    # Plots each time series with a different color
    for file_name, color in zip(file_names, colors):
        subset = files_to_print[files_to_print['file_name'] == file_name]
        plt.plot(subset['Time'], subset.iloc[:, column_index], label=file_name, color=color)

    plt.title('Time Series Plot by File Name')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()  # Shows the legend with file names
    plt.show()
    
def concatenate_files(directory_path, file_prefix, one_in=1):
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
            temp_df['file_name'] = file_path
            concatenated_df = pd.concat([concatenated_df, temp_df], ignore_index=True)
            files_read += 1  # Increment the counter

    print(f"Number of files read (based on one_in={one_in}): {files_read}")

    return concatenated_df
