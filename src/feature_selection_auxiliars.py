import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def compute_monotonicity(input):

  diff_input = np.diff(input)

  monotonicity = np.abs(np.sum(diff_input> 0)/(len(input) - 1) - np.sum(diff_input < 0)/(len(input) - 1))

  plt.plot(input)
  plt.title('Monotonicity: ' + np.array2string(monotonicity))
  plt.show()

def plot_indicator_by_bearing(indicators, target_variable):

    # Create a scatter plot
    indicators['Bearings_code'] = pd.Categorical(indicators['Bearing']).codes

    plt.figure(figsize=(10, 6))  # Adjust the size of the plot as needed
    scatter = plt.scatter(indicators['Duration'], indicators[target_variable], c=indicators['Bearings_code'], cmap='viridis')
    legend_labels = pd.unique(indicators['Bearing'])
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=bearing,
                          markersize=10, markerfacecolor=scatter.cmap(scatter.norm(indicators[indicators['Bearing'] == bearing]['Bearings_code'].iloc[0]))) for bearing in legend_labels]
    plt.legend(handles=handles, title='Bearing')
    plt.xlabel('Duration')
    plt.ylabel(target_variable)

    plt.show()

    return

def plot_indicator_vs_indicator(indicatordf, indicator_1, indicator_2):

    # Create a scatter plot
    indicatordf['Bearings_code'] = pd.Categorical(indicatordf['Bearing']).codes

    plt.figure(figsize=(10, 6))  # Adjust the size of the plot as needed
    scatter = plt.scatter(indicatordf[indicator_1], indicatordf[indicator_2], c=indicatordf['Bearings_code'], cmap='viridis')
    legend_labels = pd.unique(indicatordf['Bearing'])
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=bearing,
                          markersize=10, markerfacecolor=scatter.cmap(scatter.norm(indicatordf[indicatordf['Bearing'] == bearing]['Bearings_code'].iloc[0]))) for bearing in legend_labels]
    plt.legend(handles=handles, title='Bearing')
    plt.xlabel(indicator_1)
    plt.ylabel(indicator_2)

    plt.show()

    return
  
def find_closest_idx(arr, ref_arr):
    indices = []
    for value in ref_arr:
        index = (np.abs(arr - value)).argmin()
        indices.append(index)
    return np.array(indices)
  
def substract_homogeneous_RUL_values(bearing_grouped_df, RUL_idex):

    indexes_to_substract = find_closest_idx(bearing_grouped_df['RUL'], RUL_idex)

    output = bearing_grouped_df.iloc[indexes_to_substract]

    return output
  
def compute_lowest_correlation(data, column_name):
    """
    Given a DataFrame and a column name, compute the correlation
    between all groups identified by 'Bearing' for the specified column.

    Parameters:
    - data: DataFrame containing the groups and values
    - column_name: The name of the column to compute correlations on

    Returns:
    - A tuple containing the lowest correlation value and the pair of groups.
    """
    # Group the DataFrame by 'Bearing'
    grouped = data.groupby('Bearing')[column_name]

    # Get the unique groups
    groups = data['Bearing'].unique()

    # Initialize a variable to store the lowest correlation
    lowest_correlation = 1.0
    lowest_pair = None

    # Compute the correlation between all pairs of groups
    for i in range(len(groups)):
        for j in range(i+1, len(groups)):
            group1 = groups[i]
            group2 = groups[j]

            # Get the values for each pair of groups
            values1 = grouped.get_group(group1).values
            values2 = grouped.get_group(group2).values

            # To correlate, both arrays need to be of the same length
            min_length = min(len(values1), len(values2))
            if min_length == 0:  # Skip if there are no elements to compare
                continue

            # Truncate the arrays to the same length
            values1 = values1[:min_length]
            values2 = values2[:min_length]

            # Compute the correlation
            correlation = np.abs(np.corrcoef(values1, values2)[0, 1])

            # Check if this is the lowest correlation so far
            if correlation < lowest_correlation:
                lowest_correlation = correlation
                lowest_pair = (group1, group2)

    return lowest_correlation, lowest_pair
  
def plot_lowest_correlation(data, column_name):
    """
    Computes the lowest correlation between groups identified by 'Bearing' for the specified column,
    and plots the two bearings with the lowest correlation.

    Parameters:
    - data: DataFrame containing the groups and values.
    - column_name: The name of the column to compute correlations on.
    """
    # Compute the lowest correlation and the pair of bearings
    lowest_correlation, lowest_pair = compute_lowest_correlation(data, column_name)

    if lowest_pair is None:
        print("Insufficient data for correlation.")
        return

    # Extract the data for the two bearings with the lowest correlation
    bearing1_data = data[data['Bearing'] == lowest_pair[0]][column_name].values
    bearing2_data = data[data['Bearing'] == lowest_pair[1]][column_name].values

    # To plot, both arrays need to be of the same length
    min_length = min(len(bearing1_data), len(bearing2_data))
    bearing1_data = bearing1_data[:min_length]
    bearing2_data = bearing2_data[:min_length]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(bearing1_data, bearing2_data, marker='o', linestyle='')
    plt.xlabel(lowest_pair[0])
    plt.ylabel(lowest_pair[1])
    plt.title(f"Correlation: {lowest_correlation:.2f}")
    plt.show()
