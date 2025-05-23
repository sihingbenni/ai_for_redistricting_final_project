import pickle
import geopandas as gpd
import os

import maup
import pandas as pd
from geopandas import GeoDataFrame
from gerrychain import Partition, Graph
from matplotlib import pyplot as plt


# Setup for pickle
def save_cached_data(data, filename):
    # Save the data to a file using pickle
    with open(filename, 'wb') as file:
        pickle.dump(data, file)


def load_cached_data(filename):
    # Try to load the data from the cache file
    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        # Return None if the file does not exist
        return None


def load_shapefile(path) -> gpd.GeoDataFrame:
    """
    Loads a shapefile and saves the result.

    :param path: Path to the shapefile
    :return: The loaded shapefile
    """

    print(f"Loading shapefile from {path}...")

    # set up the path for the cached data
    pickle_path = path + '.pkl'

    # Check if the data is already cached
    existing_data = load_cached_data(pickle_path)

    return_file: gpd.GeoDataFrame

    if existing_data is not None:
        print(f"Shapefile data loaded from cache.")
        return_file = existing_data
        pass
    else:
        print("Loading shapefile...")
        shapefile = gpd.read_file(path)

        # Save the loaded data
        save_cached_data(shapefile, pickle_path)

        print(f"Shapefile data saved successfully to {pickle_path}.")
        return_file = shapefile
        pass

    return return_file

def load_graph(path) -> Graph:
    """
    Loads a shapefile and saves graph result.

    :param path: Path to the shapefile
    :return: The loaded shapefile Graph
    """

    print(f"Loading shapefile graph from {path}...")

    # set up the path for the cached data
    pickle_path = path + '.graph.pkl'

    # Check if the data is already cached
    existing_data = load_cached_data(pickle_path)

    return_file: Graph

    if existing_data is not None:
        print(f"Shapefile data loaded from cache.")
        return_file = existing_data
        pass
    else:
        print("Loading shapefile...")
        shapefile = Graph.from_file(path)

        # Save the loaded data
        save_cached_data(shapefile, pickle_path)

        print(f"Shapefile data saved successfully to {pickle_path}.")
        return_file = shapefile
        pass

    return return_file


def checkpoint(checkpoint_name: str, data):
    """
    Function to create a checkpoint in the code.
    :param checkpoint_name: Name of the checkpoint
    :param data: Data to be saved
    :return: The data that was saved or cached
    """
    print(f"Checkpoint: {checkpoint_name}")

    checkpoint_dir = "checkpoints"
    # Check if the directory exists, if not create it
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)

    # save or load data if pickle file exists
    pickle_path = f"{checkpoint_dir}/{checkpoint_name}.pkl"

    # Check if the data is already cached
    existing_data = load_cached_data(pickle_path)

    if existing_data is not None:
        print(f"Data loaded from cache.")
        return_file = existing_data
        pass
    else:
        print("Saving data...")

        with open(pickle_path, 'wb') as file:
            if isinstance(data, Partition):
                # Save only the assignment dictionary
                pickle.dump(data.assignment, file)
                return_file = data.assignment
            else:
                pickle.dump(data, file)
                return_file = data
        print(f"Data saved successfully to {pickle_path}.")
        pass

    return return_file


def assign_population_data_to(
        df: gpd.GeoDataFrame,
        population_df: gpd.GeoDataFrame,
        vap_df: gpd.GeoDataFrame,
        pop_column_names: list,
        vap_column_names: list,
):
    """
        Assigns population data to a GeoDataFrame based on spatial assignment.
        This will change the dataframe outside the function.
        :param df: The GeoDataFrame to which the population data will be assigned
        :param population_df: The GeoDataFrame containing population data
        :param vap_df: The GeoDataFrame containing VAP data
        :param pop_column_names: List of column names in population_df to be assigned
        :param vap_column_names: List of column names in vap_df to be assigned
    """

    blocks_to_precincts_assignment = maup.assign(population_df.geometry, df.geometry)
    vap_blocks_to_precincts_assignment = maup.assign(vap_df.geometry, df.geometry)

    for name in pop_column_names:
        df[name] = population_df[name].groupby(blocks_to_precincts_assignment).sum()
    for name in vap_column_names:
        df[name] = vap_df[name].groupby(vap_blocks_to_precincts_assignment).sum()
    pass
