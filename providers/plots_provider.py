import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from scipy.stats import stats
import statsmodels.api as sm

from providers.data_acquisition_provider import DataAcquisitionProvider
from providers.data_manifest_provider import DataManifestProvider
from providers.non_parametric_tests_provider import NonParametricTestsProvider


class PlotsProvider:
    """
    Static methods which perform the plotting functionality.

    Methods
    -------
        plot_algorithm_normality_histogram(dimension=10, parameter=1, algorithm='', alpha=0.05):
            Checks normality for the given parameters and displays rejects/accepts the null hypothesis
        plot_algorithm_normality_qq(dimension=10, parameter=1, algorithm='', alpha=0.05):
            Checks normality for the given parameters and displays rejects/accepts the null hypothesis

        plot_algorithm_comparison_bar(dimension=10, parameter=1):
            Shows the mean difference between each algorithm and the optimal result.
        plot_algorithm_comparison_box(dimension=10, parameter=1):
            Shows the general distribution of each algorithm.

        plot_algorithm_performance_fluctuation(parameter=1):
            Shows each algorithm performance fluctuation when changing the dimension
    """

    @staticmethod
    def plot_algorithm_normality_histogram(dimension=10, parameter=1, algorithm='', alpha=0.05):
        """
        Checks normality for the given parameters and displays rejects/accepts the null hypothesis

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param float alpha: Specify the level of significance
        :param str algorithm: Specify the desired algorithm, default is the best algorithm
        """
        if len(algorithm) == 0:
            algorithm = NonParametricTestsProvider.get_best_algorithm(dimension=dimension,
                                                                      parameter=parameter)

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm_ in df.loc[problem]:
                df.loc[problem][algorithm_]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        df = df[algorithm]

        p_value = stats.normaltest(df)[1]

        reject = 'REJECTED' if p_value <= alpha else 'FAILED TO REJECT'

        df.plot(kind='hist',
                title=f'{algorithm} Distribution, Dimension: {dimension} | Parameter: {parameter}'
                      f'\n Null Hypothesis: {reject}',
                figsize=(12, 8)
                )

        plt.xlabel('Mean')

        plt.show()

    @staticmethod
    def plot_algorithm_normality_qq(dimension=10, parameter=1, algorithm='', alpha=0.05):
        """
        Checks normality for the given parameters and displays rejects/accepts the null hypothesis

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param float alpha: Specify the level of significance
        :param str algorithm: Specify the desired algorithm, default is the best algorithm
        """
        if len(algorithm) == 0:
            algorithm = NonParametricTestsProvider.get_best_algorithm(dimension=dimension,
                                                                      parameter=parameter)

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm_ in df.loc[problem]:
                df.loc[problem][algorithm_]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        df = df[algorithm]

        p_value = stats.normaltest(df)[1]

        reject = 'REJECTED' if p_value <= alpha else 'FAILED TO REJECT'

        with mpl.rc_context():
            mpl.rc("figure", figsize=(12, 8))
            sm.qqplot(df, line='45')

        plt.suptitle(f'{algorithm} Distribution, Dimension: {dimension} | Parameter: {parameter}'
                     f'\n Null Hypothesis: {reject}')

        plt.xlabel('Mean')

        plt.show()

    @staticmethod
    def plot_algorithm_comparison_bar(dimension=10, parameter=1):
        """
        Shows the mean difference between each algorithm and the optimal result.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        """

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        df = df.mean()

        df.index = df.index.to_series().apply(lambda x: (x[:10] + '..') if len(x) > 10 else x)

        best_algorithm = NonParametricTestsProvider.get_best_algorithm(dimension=dimension, parameter=parameter)

        df.plot(kind='bar',
                title=f'Normalized Algorithm Comparisons, Dimension: {dimension} | Parameter: {parameter}\n'
                      f'Best Algorithm is {best_algorithm}',
                figsize=(12, 8),
                label='Normalized (logarithm) difference from optimal result',
                legend=True
                )

        plt.xticks(rotation=35)
        plt.yscale('log')

        plt.show()

    @staticmethod
    def plot_algorithm_comparison_box(dimension=10, parameter=1):
        """
        Shows the mean difference between each algorithm and the optimal result.

        :param int dimension: Specify the desired dimension (must be within 'DataManifestProvider.DIMENSIONS')
        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        """

        df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

        for problem in df.index.get_level_values('Problem').unique():
            for algorithm in df.loc[problem]:
                df.loc[problem][algorithm]['Std'] = None

        df = df \
            .reset_index(level=1, drop=True) \
            .dropna(how='all', axis=0) \
            .dropna(how='all', axis=1)

        df.columns = df.columns.to_series().apply(lambda x: (x[:10] + '..') if len(x) > 10 else x)

        best_algorithm = NonParametricTestsProvider.get_best_algorithm(dimension=dimension, parameter=parameter)

        df.plot(kind='box',
                title=f'Normalized Algorithm Comparisons, Dimension: {dimension} | Parameter: {parameter}\n'
                      f'Best Algorithm is {best_algorithm}',
                figsize=(12, 8)
                )

        plt.xticks(rotation=35)
        plt.yscale('log')

        plt.show()

    @staticmethod
    def plot_algorithm_performance_fluctuation(parameter=1, normalize=True):
        """
        Shows each algorithm performance fluctuation when changing the dimension

        :param int parameter: Specify the desired parameter (must be within 'DataManifestProvider.PARAMETERS')
        :param bool normalize: Specify whether to normalize the results or not (using the logarithm)
        """

        result = []

        for dimension in DataManifestProvider.DIMENSIONS:
            df = DataAcquisitionProvider.get_algorithms_comparisons()[dimension][parameter]

            for problem in df.index.get_level_values('Problem').unique():
                for algorithm in df.loc[problem]:
                    df.loc[problem][algorithm]['Std'] = None

            df = df \
                .reset_index(level=1, drop=True) \
                .dropna(how='all', axis=0) \
                .dropna(how='all', axis=1)

            df = df.mean()

            result.append(df.to_list())

        algorithm_names = \
            DataAcquisitionProvider.get_algorithms_comparisons()[DataManifestProvider.DIMENSIONS[0]][parameter].columns

        result = pd.DataFrame(result, columns=algorithm_names, index=[str(x) for x in DataManifestProvider.DIMENSIONS])

        if normalize:
            title = f'Normalized Algorithm Performance Fluctuation, Parameter: {parameter}'
        else:
            title = f'Algorithm Performance Fluctuation, Parameter: {parameter}'

        result.plot(kind='line',
                    title=title,
                    figsize=(12, 8),
                    style=['r-', 'g-', 'b-', 'c-', 'm-', 'y-',
                           'r--', 'g--', 'b--', 'c--', 'm--', 'y--',
                           'r:', 'g:', 'b:', 'c:', 'm:', 'y:'
                           ]
                    )

        if normalize:
            plt.yscale('log')

        plt.show()
