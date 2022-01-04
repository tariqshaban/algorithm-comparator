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

        :param int dimension: Specify to desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify to desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: The best algorithm (estimated)
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('invalid parameter value')

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension]

        algorithm_mean = {}
        count = 0

        for problem in df[parameter].index.get_level_values('Problem').unique():
            count += 1
            for algorithm in df[parameter].loc[problem]:
                if df[parameter].loc[problem][algorithm]['Mean'] is not None:
                    algorithm_mean[algorithm] = algorithm_mean.get(algorithm, 0) + \
                                                df[parameter].loc[problem][algorithm]['Mean']

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

        :param int dimension: Specify to desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify to desired parameter (must be within 'DataManifestProvider.PARAMETERS')
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

        :param int dimension: Specify to desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param str algorithm_to_compare: Specify to desired algorithm to compare
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

            df[parameter].reset_index(level=1, drop=True, inplace=True)

            df[parameter].dropna(how='all', axis=0, inplace=True)
            df[parameter].dropna(how='all', axis=1, inplace=True)

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

        :param int dimension: Specify to desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify to desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: A [statistic, pvalue] directly from the friedmanchisquare method
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('invalid parameter value')

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension]

        for problem in df[parameter].index.get_level_values('Problem').unique():
            for algorithm in df[parameter].loc[problem]:
                df[parameter].loc[problem][algorithm]['Std'] = None

        df[parameter].reset_index(level=1, drop=True, inplace=True)

        df[parameter].dropna(how='all', axis=0, inplace=True)
        df[parameter].dropna(how='all', axis=1, inplace=True)

        algorithm_values = {}
        for column in df[parameter]:
            algorithm_values[column] = algorithm_values.get(column, []) + df[parameter][column].tolist()

        result = friedmanchisquare(*list(algorithm_values.values()))

        return result

    @staticmethod
    def algorithm_ranking(dimension=10, parameter=0):
        """
        Returns the ranking of each algorithm.

        :param int dimension: Specify to desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify to desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: A dataframe of ranks for each algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('invalid parameter value')

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension]

        for problem in df[parameter].index.get_level_values('Problem').unique():
            for algorithm in df[parameter].loc[problem]:
                df[parameter].loc[problem][algorithm]['Std'] = None

        complete_df = df[parameter]

        complete_df = complete_df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0)\
            .dropna(how='all', axis=1) \
            .reset_index(drop=True)

        complete_df.index.name = 'Algorithm'

        complete_df = complete_df.rank(axis=1)

        complete_df = (complete_df.sum() / complete_df.count())

        friedman = NonParametricTestsProvider.friedman_test(dimension=dimension, parameter=parameter)

        complete_df['P_Value'] = friedman[1]
        complete_df['Statistic'] = friedman[0]

        return complete_df
