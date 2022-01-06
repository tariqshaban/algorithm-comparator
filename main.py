from helpers.dataframe_beautifier import DataframeBeautifier
from providers.non_parametric_tests_provider import NonParametricTestsProvider

print('Comparing....')
print('--------------------------------------------------')

DataframeBeautifier.print_console_stream(
    NonParametricTestsProvider.get_algorithms_comparisons_wtl(dimension=10, parameter=8))

DataframeBeautifier.print_console_stream(
    NonParametricTestsProvider.wilcoxon_test(dimension=10, parameter=8),
    apply_scientific_notation_to_all_columns=False,
    floating_scientific_notation_rows=['P-Value']
)

print(NonParametricTestsProvider.estimate_best_algorithm(dimension=10, parameter=8))
print(NonParametricTestsProvider.estimate_best_algorithm(dimension=30, parameter=8))
print(NonParametricTestsProvider.estimate_best_algorithm(dimension=50, parameter=8))
print(NonParametricTestsProvider.estimate_best_algorithm(dimension=100, parameter=8))

print(NonParametricTestsProvider.get_best_algorithm(dimension=10, parameter=8))
print(NonParametricTestsProvider.get_best_algorithm(dimension=30, parameter=8))
print(NonParametricTestsProvider.get_best_algorithm(dimension=50, parameter=8))
print(NonParametricTestsProvider.get_best_algorithm(dimension=100, parameter=8))

DataframeBeautifier.print_console_stream(
    NonParametricTestsProvider.friedman_test(dimension=10, parameter=8).to_frame().T,
    apply_scientific_notation_to_all_columns=False,
    floating_scientific_notation_columns=['P-Value', 'Statistic'],
    transpose=True
)
#########################################################
#########################################################

print('--------------------------------------------------')
print('Done.')
