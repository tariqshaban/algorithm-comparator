import pandas as pd
from scipy.stats import wilcoxon

from providers.data_acquisition_provider import AlgorithmsProvider
from providers.data_manifest_provider import DataManifestProvider


class NonParametricTestsProvider:
    """
    Static methods which handles implementing nonparametric tests the transformed data.

    Methods
    -------
        estimate_worst_algorithm(dimension=10):
            Provides a broad estimation of the worst algorithm by calculating the mean for a given dimension
        wilcoxon_test(dimension=10, algorithm_to_compare=''):
            Compare all algorithms with a provided reference algorithm (preferably the worst)
    """

    @staticmethod
    def estimate_worst_algorithm(dimension=10):
        """
        Provides a broad estimation of the worst algorithm by calculating the mean for a given dimension

        :param int dimension: Specify to desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :return: The worst algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')

        df = AlgorithmsProvider.get_algorithms_comparisons()[dimension]

        algorithm_mean = {}
        count = 0

        for parameter in DataManifestProvider.PARAMETERS:
            for problem in df[parameter].index.get_level_values('Problem').unique():
                count += 1
                for algorithm in df[parameter].loc[problem]:
                    if df[parameter].loc[problem][algorithm]['Mean'] is not None:
                        algorithm_mean[algorithm] = algorithm_mean.get(algorithm, 0) + \
                                                    df[parameter].loc[problem][algorithm]['Mean']

        for key in algorithm_mean:
            algorithm_mean[key] = algorithm_mean.get(key, 0) / count

        worst = max(algorithm_mean, key=algorithm_mean.get)

        print(
            f'Worst Algorithm is {worst} with an average difference from optimal '
            f'of {algorithm_mean[worst]} in the {dimension}th dimension.')

        return worst

    @staticmethod
    def wilcoxon_test(dimension=10, algorithm_to_compare=''):
        """
        Provides a broad estimation of the worst algorithm by calculating the mean for a given dimension

        :param int dimension: Specify to desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param str algorithm_to_compare: Specify to desired algorithm to compare
        :return: A dataframe of p values obtained for Wilcoxon in concurrence with the selected reference algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('invalid dimension value')

        if len(algorithm_to_compare) == 0:
            algorithm_to_compare = NonParametricTestsProvider.estimate_worst_algorithm(dimension=dimension)

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

                if not all(x == column[0] for x in column) and \
                        column != algorithm_to_compare and \
                        len(df[parameter][column]) != 0:  # Wilcoxon does not operate if all values are identical
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
