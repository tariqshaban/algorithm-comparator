from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon, friedmanchisquare

from providers.data_acquisition_provider import AlgorithmsProvider
from providers.data_manifest_provider import DataManifestProvider


class NonParametricTestsProvider:
    """
    Static methods which handles implementing nonparametric tests the transformed data.

    Methods
    -------
        estimate_best_algorithm(dimension=10, parameter=0):
            Provides a broad estimation of the best algorithm by calculating the mean for a given dimension.
        get_best_algorithm(dimension=10, parameter=0):
            Provides a relatively accurate estimation of the best algorithm by calculating the mean of the ranks.
        wilcoxon_test(dimension=10, algorithm_to_compare=''):
            Compare all algorithms with a provided reference algorithm (preferably the best).
        friedman_test(dimension=10, parameter=0):
            Conducts friedman test on each algorithm.
        algorithm_ranking(dimension=10, parameter=0):
            Returns the ranking of each algorithm.
    """

    @staticmethod
    def estimate_best_algorithm(dimension=10, parameter=0):
        """
        Provides a broad estimation of the best algorithm by calculating the mean for a given dimension.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: The best algorithm (estimated)
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('invalid parameter value')

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension][parameter]

        algorithm_mean = {}
        count = 0

        for problem in df.index.get_level_values('Problem').unique():
            count += 1
            for algorithm in df.loc[problem]:
                if df.loc[problem][algorithm]['Mean'] is not None:
                    algorithm_mean[algorithm] = algorithm_mean.get(algorithm, 0) + \
                                                df.loc[problem][algorithm]['Mean']

        for key in algorithm_mean:
            algorithm_mean[key] = algorithm_mean.get(key, 0) / count

        best = min(algorithm_mean, key=algorithm_mean.get)

        print(
            f'Best Algorithm is {best} with an average difference from optimal of {algorithm_mean[best]}.')

        return best

    @staticmethod
    def get_best_algorithm(dimension=10, parameter=0):
        """
        Provides a relatively accurate estimation of the best algorithm by calculating the mean of the ranks.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: The best algorithm
        """

        ranking = NonParametricTestsProvider.algorithm_ranking(dimension=dimension, parameter=parameter)

        ranking = ranking.drop(['P_Value', 'Statistic'])

        best_algorithm = ranking[ranking == ranking.min()].index.format()[0]

        return best_algorithm

    @staticmethod
    def wilcoxon_test(dimension=10, algorithm_to_compare=''):
        """
        Compare all algorithms with a provided reference algorithm (preferably the best).

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param str algorithm_to_compare: Specify the desired algorithm to compare
        :return: A dataframe of p values obtained for Wilcoxon in concurrence with the selected reference algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')

        if len(algorithm_to_compare) == 0:
            algorithm_to_compare = NonParametricTestsProvider.get_best_algorithm(dimension=dimension)

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension]

        for parameter in DataManifestProvider.PARAMETERS:
            for problem in df[parameter].index.get_level_values('Problem').unique():
                for algorithm in df[parameter].loc[problem]:
                    df[parameter].loc[problem][algorithm]['Std'] = None

            df[parameter] = df[parameter] \
                .reset_index(level=1, drop=True) \
                .dropna(how='all', axis=0) \
                .dropna(how='all', axis=1)

        result = {}
        column_names = [column for column in df[0]]

        for parameter in DataManifestProvider.PARAMETERS:
            algorithm_values = []

            for column in df[parameter]:
                if column != algorithm_to_compare:
                    algorithm_values.append(
                        wilcoxon(df[parameter][column].tolist(), df[parameter][algorithm_to_compare].tolist())[1])
                else:
                    algorithm_values.append(0)
            result[parameter] = algorithm_values

        wilcoxon_result = pd.DataFrame(result).T

        wilcoxon_result.columns = column_names

        wilcoxon_result.columns.name = 'Algorithm'
        wilcoxon_result.index.name = 'Parameter'

        return wilcoxon_result

    @staticmethod
    def friedman_test(dimension=10, parameter=0):
        """
        Conducts friedman test on each algorithm.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: A [statistic, p-value] directly from the 'friedmanchisquare' method
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('invalid parameter value')

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        algorithm_values = {}
        for column in df:
            algorithm_values[column] = algorithm_values.get(column, []) + df[column].tolist()

        result = friedmanchisquare(*list(algorithm_values.values()))

        return result

    @staticmethod
    def algorithm_ranking(dimension=10, parameter=0):
        """
        Returns the ranking of each algorithm.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: A dataframe of ranks for each algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('invalid parameter value')

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        df.index.name = 'Algorithm'

        df = df.rank(axis=1)

        df = (df.sum() / df.count())

        friedman = NonParametricTestsProvider.friedman_test(dimension=dimension, parameter=parameter)

        df['P_Value'] = friedman[1]
        df['Statistic'] = friedman[0]

        return df.to_frame()

    @staticmethod
    def get_algorithms_comparisons_wtl(dimension=10, parameter=0):
        """
        Adds win-tie-lose attribute with the get_algorithms_comparisons method.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: A dataframe of Measurements for each algorithm and problem with a w/t/l for each algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('invalid parameter value')

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        df.index.name = 'Algorithm'

        total_result = defaultdict(dict)

        for index, row in df.iterrows():
            max_val = row.min()
            result = np.zeros(len(df.columns))
            for column_index, column in enumerate(df.columns):
                if row[column] == max_val:
                    result[column_index] = 1
            if (result == 1).sum() != 1:
                result[result == 1] = -1
            for column_index, column in enumerate(df.columns):
                if result[column_index] == 1:
                    total_result[column]['win'] = total_result[column].get('win', 0) + 1
                elif result[column_index] == -1:
                    total_result[column]['draw'] = total_result[column].get('draw', 0) + 1
                else:
                    total_result[column]['lose'] = total_result[column].get('lose', 0) + 1

        results_str = []
        for key, value in total_result.items():
            results_str.append(f'{value.get("win", 0)}/'
                               f'{value.get("draw", 0)}/'
                               f'{value.get("lose", 0)}')

        results_df = AlgorithmsProvider.get_algorithms_comparisons()[dimension][parameter] \
            .append(pd.DataFrame({'w/t/l': results_str}, index=df.columns).T)

        return results_df
