from helpers.dataframe_beautifier import DataframeBeautifier
from providers.data_acquisition_provider import DataAcquisitionProvider
from providers.non_parametric_tests_provider import NonParametricTestsProvider
from providers.plots_provider import PlotsProvider

print('Comparing....')
print('--------------------------------------------------')

########################################################################################################################
########################################################################################################################
# 1) Set your custom data's absolute path here 'optional'
# DataAcquisitionProvider.set_algorithms_raw_directory(
#     r'D:/algorithm-comparator/assets/algorithms'
# )
# Or use a relative path
# DataAcquisitionProvider.set_algorithms_raw_directory(
#     r'assets/algorithms'
# )

# 2) Cache your data -Time consuming- 'One time only, when assets/cached_instances is empty'
# DataAcquisitionProvider.cache_algorithms_comparisons()

# 3) Specify The Desired Dimension, Parameter, & Alpha to Test
DIMENSION = 10
PARAMETER = 8
ALPHA = 0.05

# 4) Invoke any method that you wish
########################################################################################################################
########################################################################################################################

# Get Algorithm Comparisons With W/T/L in Footer (DEPRECATED)-----------------------------------------------------------
df = NonParametricTestsProvider.get_algorithms_comparisons_wtl(
    dimension=DIMENSION,
    parameter=PARAMETER,
)
DataframeBeautifier.print_console_stream(df)

# Get Algorithm Comparisons With W/T/L in Footer------------------------------------------------------------------------
df = NonParametricTestsProvider.get_algorithms_comparisons_wtl_mannwhitneyu(
    dimension=DIMENSION,
    parameter=PARAMETER,
    alpha=ALPHA,
)
DataframeBeautifier.print_console_stream(df)

# Wilcoxon Test---------------------------------------------------------------------------------------------------------
df = NonParametricTestsProvider.wilcoxon_test(
    dimension=DIMENSION,
    parameter=PARAMETER,
    alpha=ALPHA,
)
DataframeBeautifier.print_console_stream(
    df,
    apply_scientific_notation_to_all_columns=False,
    floating_scientific_notation_columns=['P-Value'],
)

# Best Algorithm (DEPRECATED)-------------------------------------------------------------------------------------------
best = NonParametricTestsProvider.estimate_best_algorithm(
    dimension=DIMENSION,
    parameter=PARAMETER,
)
print(best)

# Best Algorithm--------------------------------------------------------------------------------------------------------
best = NonParametricTestsProvider.get_best_algorithm(
    dimension=DIMENSION,
    parameter=PARAMETER,
)
print(best)

# Friedman Test---------------------------------------------------------------------------------------------------------
df = NonParametricTestsProvider.friedman_test(
    dimension=DIMENSION,
    parameter=PARAMETER,
    alpha=ALPHA,
).to_frame()

DataframeBeautifier.print_console_stream(
    df.T,
    apply_scientific_notation_to_all_columns=False,
    floating_scientific_notation_columns=['P-Value', 'Statistic'],
    transpose=True,
)

# Post Hoc Tests With Pair-wise Comparisons-----------------------------------------------------------------------------
df = NonParametricTestsProvider.get_post_hoc_tests(
    dimension=DIMENSION,
    parameter=PARAMETER,
    alpha=ALPHA,
    algorithm_to_compare='GaAPADE',
)
DataframeBeautifier.print_console_stream(df)

# Post Hoc Tests (Compare With Best Algorithm)--------------------------------------------------------------------------
df = NonParametricTestsProvider.get_post_hoc_tests(
    dimension=DIMENSION,
    parameter=PARAMETER,
    alpha=ALPHA,
)
DataframeBeautifier.print_console_stream(df)

# Normality Plotting----------------------------------------------------------------------------------------------------
PlotsProvider.plot_algorithm_normality_histogram(
    dimension=DIMENSION,
    parameter=PARAMETER,
    alpha=ALPHA,
)
PlotsProvider.plot_algorithm_normality_qq(
    dimension=DIMENSION,
    parameter=PARAMETER,
    alpha=ALPHA,
)

# Comparisons Plotting--------------------------------------------------------------------------------------------------
PlotsProvider.plot_algorithm_comparison_bar(
    dimension=DIMENSION,
    parameter=PARAMETER
)
PlotsProvider.plot_algorithm_comparison_box(
    dimension=DIMENSION,
    parameter=PARAMETER
)

# Performance Plotting--------------------------------------------------------------------------------------------------
PlotsProvider.plot_algorithm_performance_fluctuation(
    parameter=PARAMETER
)
PlotsProvider.plot_algorithm_performance_fluctuation(
    parameter=PARAMETER,
    normalize=False
)

# Best Algorithm Plotting-----------------------------------------------------------------------------------------------
PlotsProvider.plot_best_algorithms()

print('--------------------------------------------------')
print('Done.')
