import pandas as pd

from helpers.dataframe_beautifier import DataframeBeautifier
from providers.data_acquisition_provider import AlgorithmsProvider
from providers.non_parametric_tests_provider import NonParametricTestsProvider

pd.set_option('display.float_format', '{:e}'.format)

print('Comparing....')
print('--------------------------------------------------')

pd.set_option('display.expand_frame_repr', False)

AlgorithmsProvider.get_algorithms_raw()
AlgorithmsProvider.get_algorithms_comparisons()

DataframeBeautifier.print_console_stream(
    NonParametricTestsProvider.get_algorithms_comparisons_wtl(dimension=10, parameter=0))

DataframeBeautifier.print_console_stream(NonParametricTestsProvider.wilcoxon_test(dimension=10))

print(NonParametricTestsProvider.estimate_best_algorithm(dimension=10, parameter=8))
print(NonParametricTestsProvider.estimate_best_algorithm(dimension=30, parameter=8))
print(NonParametricTestsProvider.estimate_best_algorithm(dimension=50, parameter=8))
print(NonParametricTestsProvider.estimate_best_algorithm(dimension=100, parameter=8))

print(NonParametricTestsProvider.get_best_algorithm(dimension=10, parameter=8))
print(NonParametricTestsProvider.get_best_algorithm(dimension=30, parameter=8))
print(NonParametricTestsProvider.get_best_algorithm(dimension=50, parameter=8))
print(NonParametricTestsProvider.get_best_algorithm(dimension=100, parameter=8))

DataframeBeautifier.print_console_stream(NonParametricTestsProvider.algorithm_ranking(dimension=10, parameter=8))
#########################################################
#########################################################

print('--------------------------------------------------')
print('Done.')
