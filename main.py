import pandas as pd

from providers.data_acquisition_provider import AlgorithmsProvider
from providers.non_parametric_tests_provider import NonParametricTestsProvider

pd.set_option('display.float_format', '{:e}'.format)

print('Comparing....')
print('--------------------------------------------------')

pd.set_option('display.expand_frame_repr', False)

AlgorithmsProvider.get_algorithms_raw()
AlgorithmsProvider.get_algorithms_comparisons()

# print(AlgorithmsProvider.get_algorithms_comparisons()[10][0])

print(NonParametricTestsProvider.wilcoxon_test(dimension=100))

#########################################################
#########################################################

print('--------------------------------------------------')
print('Done.')
