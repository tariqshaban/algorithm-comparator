from collections import defaultdict

import deprecation
import numpy as np
import pandas as pd
import statsmodels.stats.multitest as smt
import scikit_posthocs as sp
from scikit_posthocs import posthoc_nemenyi_friedman
from scipy.stats import wilcoxon, friedmanchisquare, mannwhitneyu
from enums.adjusted_p_value_methods import AdjustedPValueMethods
from providers.data_acquisition_provider import DataAcquisitionProvider
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
        wilcoxon_test(dimension=10, parameter=0, algorithm_to_compare=''):
            Compare all algorithms with a provided reference algorithm (preferably the best).
        __friedman_test(dimension=10, parameter=0):
            Conducts friedman test on each algorithm.
        friedman_test(dimension=10, parameter=0):
            Returns the ranking of each algorithm.
        get_algorithms_comparisons_wtl(dimension=10, parameter=0):
            Adds win-tie-lose attribute with the get_algorithms_comparisons method.
        get_algorithms_comparisons_wtl_mannwhitneyu(dimension=10, parameter=0, alpha=0.05):
            Adds win-tie-lose attribute with the get_algorithms_comparisons method using Mann–Whitney U test
            and utilizing the raw iterations, does not respect caching.
        __get_nemenyi_post_hoc_test(dimension=10, parameter=0, algorithm_to_compare=''):
            Displays adjusted p values from Nemenyi test.
        __get_nemenyi_friedman_post_hoc_test(dimension=10, parameter=0, algorithm_to_compare=''):
            Displays adjusted p values from Nemenyi-friedman test, used when Friedman p is significant.

        get_post_hoc_tests(dimension=10, parameter=0, algorithm_to_compare=''):
            Displays unadjusted p values obtained from wilcoxon in addition with selected correction methods.
    """

    @staticmethod
    @deprecation.deprecated(details="Use the get_best_algorithm function instead")
    def estimate_best_algorithm(dimension=10, parameter=0):
        """
        Provides a broad estimation of the best algorithm by calculating the mean for a given dimension.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: The best algorithm (estimated)
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('Invalid parameter value')

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

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

        return best

    @staticmethod
    def get_best_algorithm(dimension=10, parameter=0):
        """
        Provides a relatively accurate estimation of the best algorithm by calculating the mean of the ranks.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: The best algorithm
        """

        ranking = NonParametricTestsProvider.friedman_test(dimension=dimension, parameter=parameter)

        ranking = ranking.drop(['P-Value', 'Statistic'])

        best_algorithm = ranking[ranking == ranking.min()].index.format()[0]

        return best_algorithm

    @staticmethod
    def wilcoxon_test(dimension=10, parameter=0, algorithm_to_compare='', alpha=0.05):
        """
        Compare all algorithms with a provided reference algorithm (preferably the best).

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param str algorithm_to_compare: Specify the desired algorithm to compare, default is the best algorithm
        :param float alpha: Specify the level of significance
        :return: A dataframe of p values obtained for Wilcoxon in concurrence with the selected reference algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')

        if len(algorithm_to_compare) == 0:
            algorithm_to_compare = NonParametricTestsProvider.get_best_algorithm(dimension=dimension,
                                                                                 parameter=parameter)

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        sample_size = len(df.index.get_level_values('Problem').unique())

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        algorithm_values = []

        for column in df:
            if column != algorithm_to_compare:
                wilcoxon_result = wilcoxon(df[column].tolist(), df[algorithm_to_compare].tolist())

                reject = 'X' if wilcoxon_result[1] < alpha else '✓'
                reject = f'({reject})'

                algorithm_values.append([
                    wilcoxon_result[1],
                    reject,
                    (sample_size * (sample_size + 1) / 2) - wilcoxon_result[0],
                    wilcoxon_result[0]
                ])
            else:
                algorithm_values.append([1, '(✓)', 0, 0])

        wilcoxon_result = pd.DataFrame(algorithm_values).T

        wilcoxon_result.columns = df.columns
        wilcoxon_result.index = ['P-Value', 'Hypothesis', 'W+', 'W-']

        return wilcoxon_result.T

    @staticmethod
    def __friedman_test(dimension=10, parameter=0):
        """
        Conducts friedman test on each algorithm.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: A [statistic, p-value] directly from the 'friedmanchisquare' method
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('Invalid parameter value')

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

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
    def friedman_test(dimension=10, parameter=0, alpha=0.05):
        """
        Returns the ranking of each algorithm.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param float alpha: Specify the level of significance
        :return: A dataframe of ranks for each algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('Invalid parameter value')

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        df.index.name = 'Algorithm'

        df = df.rank(axis=1)

        df = df.mean()

        friedman = NonParametricTestsProvider.__friedman_test(dimension=dimension, parameter=parameter)

        reject = 'X' if friedman[1] < alpha else '✓'
        p_values = f'{friedman[1]}  ({reject})'

        df['P-Value'] = p_values
        df['Statistic'] = friedman[0]

        return df

    @staticmethod
    @deprecation.deprecated(details="Use the get_algorithms_comparisons_wtl_wilcoxon function instead")
    def get_algorithms_comparisons_wtl(dimension=10, parameter=0):
        """
        Adds win-tie-lose attribute with the get_algorithms_comparisons method.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :return: A dataframe of Measurements for each algorithm and problem with a w/t/l for each algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('Invalid parameter value')

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

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
            min_val = row.min()
            result = np.zeros(len(df.columns))
            for column_index, column in enumerate(df.columns):
                if row[column] == min_val:
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

        results_df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter] \
            .append(pd.DataFrame({'w/t/l': results_str}, index=df.columns).T)

        return results_df

    @staticmethod
    def get_algorithms_comparisons_wtl_mannwhitneyu(dimension=10, parameter=0, alpha=0.05):
        """
        Adds win-tie-lose attribute with the get_algorithms_comparisons method using Mann–Whitney U test
        and utilizing the raw iterations, does not respect caching.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param float alpha: Specify the level of significance
        :return: A dataframe of Measurements for each algorithm and problem with a w/t/l for each algorithm
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('Invalid parameter value')

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        df.index.name = 'Algorithm'

        df = df.astype('str')

        total_result = defaultdict(dict)

        raw_df = DataAcquisitionProvider.get_algorithms_raw()

        best_algorithm = NonParametricTestsProvider.get_best_algorithm(dimension=dimension, parameter=parameter)

        for rowIndex, row in df.iterrows():
            for columnIndex, value in row.items():

                problem = str(rowIndex)
                algorithm = columnIndex
                dimension = str(dimension)
                parameter = parameter

                best_algorithm_iterations = raw_df[algorithm][problem][str(dimension)].loc[parameter]
                this_algorithm_iterations = raw_df[best_algorithm][problem][str(dimension)].loc[parameter]

                best_algorithm_iterations = best_algorithm_iterations.drop(labels=['mean', 'std'])
                this_algorithm_iterations = this_algorithm_iterations.drop(labels=['mean', 'std'])

                if best_algorithm_iterations.equals(this_algorithm_iterations):
                    p_value = 1
                else:
                    p_value = mannwhitneyu(best_algorithm_iterations,
                                           this_algorithm_iterations)[1]

                if p_value < alpha:
                    if value < row[best_algorithm]:
                        df.at[rowIndex, columnIndex] = str(df[columnIndex][rowIndex]) + ' (w)'
                        total_result[columnIndex]['win'] = total_result[columnIndex].get('win', 0) + 1
                    else:
                        df.at[rowIndex, columnIndex] = str(df[columnIndex][rowIndex]) + ' (l)'
                        total_result[columnIndex]['lose'] = total_result[columnIndex].get('lose', 0) + 1
                else:
                    df.at[rowIndex, columnIndex] = str(df[columnIndex][rowIndex]) + ' (t)'
                    total_result[columnIndex]['draw'] = total_result[columnIndex].get('draw', 0) + 1

        results_str = []
        for key, value in total_result.items():
            results_str.append(f'{value.get("win", 0)}/'
                               f'{value.get("draw", 0)}/'
                               f'{value.get("lose", 0)}')

        results_df = df.append(pd.DataFrame({'w/t/l': results_str}, index=df.columns).T)

        return results_df

    @staticmethod
    def __get_nemenyi_post_hoc_test(dimension=10, parameter=0, algorithm_to_compare=''):
        """
        Displays adjusted p values from Nemenyi test.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param str algorithm_to_compare: Specify the desired algorithm to compare
        :return: A dataframe of p values obtained for Wilcoxon in addition to p values from selected correction methods
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('Invalid parameter value')

        if len(algorithm_to_compare) == 0:
            algorithm_to_compare = NonParametricTestsProvider.get_best_algorithm(dimension=dimension,
                                                                                 parameter=parameter)

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        p_values = []
        for algorithm in df.columns:
            if algorithm != algorithm_to_compare:
                comparison = [df[algorithm], df[algorithm_to_compare]]
                p_values.append(sp.posthoc_nemenyi(comparison)[1][2])

        return p_values

    @staticmethod
    def __get_nemenyi_friedman_post_hoc_test(dimension=10, parameter=0, algorithm_to_compare=''):
        """
        Displays adjusted p values from Nemenyi-friedman test, used when Friedman p is significant.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param str algorithm_to_compare: Specify the desired algorithm to compare
        :return: A dataframe of p values obtained for Wilcoxon in addition to p values from selected correction methods
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('Invalid parameter value')

        if len(algorithm_to_compare) == 0:
            algorithm_to_compare = NonParametricTestsProvider.get_best_algorithm(dimension=dimension,
                                                                                 parameter=parameter)

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        p_values = []
        for algorithm in df.columns:
            if algorithm != algorithm_to_compare:
                comparison = np.array([df[algorithm], df[algorithm_to_compare]]).T
                p_values.append(posthoc_nemenyi_friedman(comparison)[0][1])

        return p_values

    @staticmethod
    def get_post_hoc_tests(dimension=10, parameter=0, algorithm_to_compare='', alpha=0.05):
        """
        Displays unadjusted p values obtained from wilcoxon in addition with selected correction methods.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param str algorithm_to_compare: Specify the desired algorithm to compare
        :param float alpha: Specify the level of significance
        :return: A dataframe of p values obtained for Wilcoxon in addition to p values from selected correction methods
        """

        if dimension not in DataManifestProvider.DIMENSIONS:
            raise ValueError('Invalid dimension value')
        if parameter not in DataManifestProvider.PARAMETERS:
            raise ValueError('Invalid parameter value')

        include_versus = True

        if len(algorithm_to_compare) == 0:
            algorithm_to_compare = NonParametricTestsProvider.get_best_algorithm(dimension=dimension,
                                                                                 parameter=parameter)
            include_versus = False

        unadjusted_p_values = \
            NonParametricTestsProvider.wilcoxon_test(dimension=dimension,
                                                     parameter=parameter,
                                                     algorithm_to_compare=algorithm_to_compare)['P-Value']

        algorithm_names = unadjusted_p_values.index.to_list()

        unadjusted_p_values = unadjusted_p_values.tolist()

        algorithm_to_compare_index = algorithm_names.index(algorithm_to_compare)
        del unadjusted_p_values[algorithm_to_compare_index]

        p_values = [unadjusted_p_values]

        for method in AdjustedPValueMethods:
            result = smt.multipletests(unadjusted_p_values, method=method.value, alpha=alpha)
            p_values.append(result[1])

        p_values.append(NonParametricTestsProvider.
                        __get_nemenyi_post_hoc_test(dimension=dimension,
                                                    parameter=parameter,
                                                    algorithm_to_compare=algorithm_to_compare
                                                    ))

        p_values.append(NonParametricTestsProvider.
                        __get_nemenyi_friedman_post_hoc_test(dimension=dimension,
                                                             parameter=parameter,
                                                             algorithm_to_compare=algorithm_to_compare
                                                             ))

        for count, method in enumerate(p_values):
            p_values[count] = np.insert(method, algorithm_to_compare_index, 1)

        for index, value in enumerate(p_values):
            p_values[index] = [str(x) for x in p_values[index]]
            for inner_index, inner_value in enumerate(p_values[index]):
                reject = 'X' if float(inner_value) < alpha else '✓'
                p_values[index][inner_index] = f'{inner_value}  ({reject})'

        verdict = []
        for algorithm in np.array(p_values).T:
            reject_count = 0
            for p_val in algorithm:
                if '(X)' in p_val:
                    reject_count += 1
            verdict.append('(X)' if reject_count >= len(algorithm) / 2 else '(✓)')

        p_values.append(verdict)

        if include_versus:
            algorithm_names = [algorithm_to_compare + ' VS ' + x for x in algorithm_names]

        df = pd.DataFrame(p_values, columns=algorithm_names,
                          index=['unadjusted-p'] +
                                [e.value for e in AdjustedPValueMethods] +
                                ['nemenyi', 'nemenyi-friedman', 'verdict']).T

        return df
