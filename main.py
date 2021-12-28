from providers.data_acquisition_provider import AlgorithmsProvider

print('Comparing....')
print('--------------------------------------------------')

AlgorithmsProvider.get_algorithms_raw()
AlgorithmsProvider.get_algorithms_comparisons()

print(AlgorithmsProvider.get_algorithms_comparisons()[10][0])

#########################################################
#########################################################

print('--------------------------------------------------')
print('Done.')
