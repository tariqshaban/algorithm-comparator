import copy
import os
from datetime import datetime

import numpy as np
import pandas as pd

from helpers.progress_handler import ProgressHandler
from providers.data_manifest_provider import DataManifestProvider


class DataAcquisitionProvider:
    """
    Static methods which handles data acquisition and transformation.

    Attributes
    ----------
        __algorithms_raw            Acts as a cache for storing raw algorithm input
        __algorithms_comparisons      Acts as a cache for storing reordered algorithm input

    Methods
    -------
        __get_algorithms_raw():
            Loads raw txt algorithms from assets/algorithms directory in a dataframe,
            while adding the mean and the standard deviation in the process.
        get_algorithms_raw():
            Calls __get_algorithms_raw if __algorithms_raw is None, otherwise,
            it retrieves __algorithms_raw immediately.
        __get_algorithms_performance_dataframe_by_dimension_and_parameter(dimension=10, parameter=0):
            Shows each algorithm performance for each problem set by showing the mean and the standard deviation.
        __get_cached_algorithms_comparisons():
            Retrieves the algorithm comparison's snapshot.
        cache_algorithms_comparisons():
            Collects a snapshot of algorithms comparisons for faster fetch in the future.
        __get_algorithms_comparisons(fast_fetch=True):
            Processes the loaded raw txt file into display a dataframe suitable for algorithms comparisons.
        get_algorithms_comparisons(fast_fetch=True):
            Calls __get_algorithms_comparisons if __algorithms_comparisons is None, otherwise,
            it retrieves __algorithms_comparisons immediately.
    """

    __algorithms_raw = None
    __algorithms_comparisons = None

    @staticmethod
    def __get_algorithms_raw():
        """
        Loads raw txt algorithms from assets/algorithms directory in a dataframe,
        while adding the mean and the standard deviation in the process.

        :return: A dictionary of algorithms containing a dictionary of problems containing a dictionary of dimensions
                 containing dataframes as the value pair, {str: {str: {str: DataFrame()}}}.
        """

        dataframes = {}
        processed = 0

        for algorithm in os.listdir('assets/algorithms'):
            print(ProgressHandler.show_progress(processed, len(os.listdir('assets/algorithms'))))
            processed += 1
            dataframes[algorithm] = {}
            for problem_set in os.listdir(f'assets/algorithms/{algorithm}'):
                filename = os.path.splitext(problem_set)[0].split('_')
                problem = filename[-2]
                dimension = filename[-1]

                if problem not in dataframes[algorithm]:
                    dataframes[algorithm][problem] = {}

                dataframes[algorithm][problem][dimension] = pd.read_csv(
                    f'assets/algorithms/{algorithm}/{problem_set}',
                    delim_whitespace=True,
                    header=None)

                current_df = dataframes[algorithm][problem][dimension]  # type: pd.DataFrame

                current_df['mean'] = current_df.mean(axis=1)
                current_df['std'] = current_df.std(axis=1)

        ProgressHandler.reset_progress()

        DataAcquisitionProvider.__algorithms_raw = dataframes

    @staticmethod
    def get_algorithms_raw():
        """
        Calls __get_algorithms_raw if __algorithms_raw is None, otherwise,
        it retrieves __algorithms_raw immediately.

        :return: A dictionary of algorithms containing a dictionary of problems containing a dictionary of dimensions
                 containing dataframes as the value pair, {str: {str: {str: DataFrame()}}}.
        """

        if DataAcquisitionProvider.__algorithms_raw is None:
            print('Fetching Raw Files, this is a one time process...')
            DataAcquisitionProvider.__get_algorithms_raw()

        return DataAcquisitionProvider.__algorithms_raw

    @staticmethod
    def __get_algorithms_performance_dataframe_by_dimension_and_parameter(dimension=10, parameter=0):
        """
        Shows each algorithm performance for each problem set by showing the mean and the standard deviation.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: A dataframe indicating each algorithm performance for a selected dimension and parameter
        """

        # Since appending to a dataframe is inefficient, we will be using 3D arrays,
        # then we will instantiate a new dataframe from the array's values.

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('invalid parameter value')

        algorithm_names = DataAcquisitionProvider.get_algorithms_raw().keys()
        index_names = []
        performance_array = []

        for algorithm in DataAcquisitionProvider.get_algorithms_raw():
            performance_array.append([])
            index_names = []
            for problem in DataAcquisitionProvider.get_algorithms_raw()[algorithm]:
                index_names.append(problem)
                if str(dimension) in DataAcquisitionProvider.get_algorithms_raw()[algorithm][problem]:

                    row = DataAcquisitionProvider.get_algorithms_raw()[algorithm][problem][str(dimension)].iloc[
                        parameter]

                    performance_array[-1].append([row['mean'],
                                                  row['std']
                                                  ])
                else:
                    performance_array[-1].append([None, None])

        performance_array = np.array(performance_array)

        names = ['Algorithm', 'Problem', 'Measurement']
        index = pd.MultiIndex.from_product([range(s) for s in performance_array.shape], names=names)
        df = pd.DataFrame({'A': performance_array.flatten()}, index=index)['A']

        index_names = [int(k) for k in index_names]

        df.index = df.index.set_levels([algorithm_names, index_names, ['Mean', 'Std']])
        df = df.unstack(level='Algorithm')

        return df.sort_index()

    @staticmethod
    def __get_cached_algorithms_comparisons():
        """
        Retrieves the algorithm comparison's snapshot.
        """

        root_directory = 'assets/cached_instances/algorithms_comparisons'

        dataframes = {}

        for dimension in DataManifestProvider.DIMENSIONS:
            dataframes[dimension] = {}
            for parameter in DataManifestProvider.PARAMETERS:
                file_directory = f'{root_directory}/{dimension}D/{parameter}.csv'
                dataframes[dimension][parameter] = pd.read_csv(file_directory, skiprows=1)

                dataframes[dimension][parameter] = dataframes[dimension][parameter].set_index(
                    ['Problem', 'Measurement'])

        return dataframes

    @staticmethod
    def cache_algorithms_comparisons():
        """
        Collects a snapshot of algorithms comparisons for faster fetch in the future.
        """

        root_directory = 'assets/cached_instances/algorithms_comparisons'

        algorithms_comparisons = DataAcquisitionProvider.get_algorithms_comparisons()

        for dimension in algorithms_comparisons:
            for parameter in algorithms_comparisons[dimension]:
                file_directory = f'{root_directory}/{dimension}D/{parameter}.csv'

                if not os.path.exists(os.path.dirname(file_directory)):
                    os.makedirs(os.path.dirname(file_directory))

                f = open(f'{file_directory}', "w+")
                f.write(f'# Timestamp: {datetime.utcnow()}\n')
                f.close()

                algorithms_comparisons[dimension][parameter].to_csv(f'{file_directory}', mode='a')

    @staticmethod
    def __get_algorithms_comparisons(fast_fetch=True):
        """
        Processes the loaded raw txt file into display a dataframe suitable for algorithms comparisons.

        :param bool fast_fetch: Retrieves algorithms comparisons from a saved snapshot instantly
        :return: A dictionary of dimensions containing a dictionary of parameters
                 containing dataframes as the value pair, {str: {str: DataFrame()}}.
        """

        if fast_fetch:
            DataAcquisitionProvider.__algorithms_comparisons = \
                DataAcquisitionProvider.__get_cached_algorithms_comparisons()
            return

        dataframes = {}
        processed = 0

        for dimension in DataManifestProvider.DIMENSIONS:
            dataframes[dimension] = {}
            for parameter in DataManifestProvider.PARAMETERS:
                print(ProgressHandler.show_progress(processed, len(DataManifestProvider.DIMENSIONS) * len(
                    DataManifestProvider.PARAMETERS)))
                processed += 1
                dataframes[dimension][parameter] = \
                    DataAcquisitionProvider.__get_algorithms_performance_dataframe_by_dimension_and_parameter(
                        dimension=dimension, parameter=parameter)

        ProgressHandler.reset_progress()

        DataAcquisitionProvider.__algorithms_comparisons = dataframes

    @staticmethod
    def get_algorithms_comparisons(fast_fetch=True):
        """
        Calls __get_algorithms_comparisons if __algorithms_comparisons is None, otherwise,
        it retrieves __algorithms_comparisons immediately.

        :param bool fast_fetch: Retrieves algorithms comparisons from a saved snapshot instantly
        :return: A dictionary of dimensions containing a dictionary of parameters
                 containing dataframes as the value pair, {str: {str: DataFrame()}}.
        """

        if DataAcquisitionProvider.__algorithms_comparisons is None:
            print('Reordering Dataframe, this is a one time process...')
            DataAcquisitionProvider.__get_algorithms_comparisons(fast_fetch=fast_fetch)

        return copy.deepcopy(DataAcquisitionProvider.__algorithms_comparisons)
