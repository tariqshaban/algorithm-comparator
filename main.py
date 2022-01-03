import pandas as pd

from providers.data_acquisition_provider import AlgorithmsProvider
from providers.non_parametric_tests_provider import NonParametricTestsProvider

pd.set_option('display.float_format', '{:e}'.format)

print('Comparing....')
print('--------------------------------------------------')

pd.set_option('display.expand_frame_repr', False)

AlgorithmsProvider.get_algorithms_raw()
AlgorithmsProvider.get_algorithms_comparisons()

print(AlgorithmsProvider.get_algorithms_comparisons()[10][0])

print(NonParametricTestsProvider.wilcoxon_test(dimension=10))

print(NonParametricTestsProvider.estimate_worst_algorithm(dimension=10, parameter=8))
print(NonParametricTestsProvider.estimate_worst_algorithm(dimension=30, parameter=8))
print(NonParametricTestsProvider.estimate_worst_algorithm(dimension=50, parameter=8))
print(NonParametricTestsProvider.estimate_worst_algorithm(dimension=100, parameter=8))

print(NonParametricTestsProvider.get_worst_algorithm(dimension=10, parameter=8))
print(NonParametricTestsProvider.get_worst_algorithm(dimension=30, parameter=8))
print(NonParametricTestsProvider.get_worst_algorithm(dimension=50, parameter=8))
print(NonParametricTestsProvider.get_worst_algorithm(dimension=100, parameter=8))

print(NonParametricTestsProvider.algorithm_ranking())
#########################################################
#########################################################

print('--------------------------------------------------')
print('Done.')
