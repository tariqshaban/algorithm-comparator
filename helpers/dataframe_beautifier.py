from tabulate import tabulate


class DataframeBeautifier:
    """
    Static methods for beautifying the output of the dataframe.

    Methods
    -------
        __is_number(s):
            Checks if the provided string is a number.
        __convert_to_float(s, is_scientific=True, max_digits=4):
            Converts the string to a formatted value.
        __apply_base_operations(dataframe, apply_scientific_notation_to_all_columns=True,
                                    floating_scientific_notation_columns=None,
                                    floating_scientific_notation_rows=None,
                                    max_digits=4,
                                    transpose=False):
            Acts as an abstraction layer for applying the provided parameters.
        print_console_stream(dataframe):
            Beautifying the output of the dataframe for the console stream.
        print_markup_text(dataframe):
            Beautifying the output of the dataframe for markup languages (specifically GitHub readme file).
    """

    @staticmethod
    def __is_number(s):
        """
        Checks if the provided string is a number.

        :param str s: The string value to be checked
        :return: Whether the string is numeric or not
        """

        if isinstance(s, float) or isinstance(s, int):
            return True

        try:
            float(s.replace('(X)', '').replace('(✓)', ''))
            return True
        except ValueError:
            return False

    @staticmethod
    def __convert_to_float(s, is_scientific=True, max_digits=4):
        """
        Converts the string to a formatted value.

        :param str s: The string value to be checked
        :param bool is_scientific: Formats the number to scientific notation or not
        :param int max_digits: Specify the maximum floating number digits
        :return: formatted string
        """

        append = ''

        if isinstance(s, str):
            if '(✓)' in s:
                append = ' (✓)'
            elif '(X)' in s:
                append = ' (X)'
            s = s.replace('(X)', '').replace('(✓)', '')

        scientific_precision = '{:.' + str(max_digits) + 'e}'
        floating_precision = '{:.' + str(max_digits) + 'g}'

        if is_scientific:
            result = scientific_precision.format(float(s))
        else:
            result = floating_precision.format(float(s))

        return result + append

    @staticmethod
    def __apply_base_operations(dataframe, apply_scientific_notation_to_all_columns=True,
                                floating_scientific_notation_columns=None,
                                floating_scientific_notation_rows=None,
                                max_digits=4,
                                transpose=False):
        """
        Acts as an abstraction layer for applying the provided parameters.

        :param pd.DataFrame() dataframe: Specify the desired dataframe
        :param bool apply_scientific_notation_to_all_columns: Specify if all columns should be in scientific format
        :param list() floating_scientific_notation_columns: Specify the columns that should be in scientific format,
                        ignored when apply_scientific_notation_to_all_columns is set to true
        :param list() floating_scientific_notation_rows: Specify the columns that should be in scientific format,
                        ignored when apply_scientific_notation_to_all_columns is set to true or
                        floating_scientific_notation_columns is filled
        :param int max_digits: Specify the maximum floating number digits
        :param bool transpose: Specify weather to transpose the dataframe or not
        :return: A dataframe
        """

        if apply_scientific_notation_to_all_columns:
            dataframe = dataframe.applymap(
                lambda x: DataframeBeautifier.__convert_to_float(x, max_digits=max_digits)
                if DataframeBeautifier.__is_number(x)
                else x
            )
        elif floating_scientific_notation_columns is not None:
            dataframe[floating_scientific_notation_columns] = \
                dataframe[floating_scientific_notation_columns].applymap(
                    lambda x: DataframeBeautifier.__convert_to_float(x, max_digits=max_digits)
                    if DataframeBeautifier.__is_number(x)
                    else x
                )

            floating_scientific_notation_columns_complement = \
                dataframe.columns.difference(floating_scientific_notation_columns)

            dataframe[floating_scientific_notation_columns_complement] = \
                dataframe[floating_scientific_notation_columns_complement].applymap(
                    lambda x: DataframeBeautifier.__convert_to_float(x, is_scientific=False, max_digits=max_digits)
                    if DataframeBeautifier.__is_number(x)
                    else x
                )
        elif floating_scientific_notation_rows is not None:
            dataframe.loc[floating_scientific_notation_rows] = \
                dataframe.loc[floating_scientific_notation_rows].applymap(
                    lambda x: DataframeBeautifier.__convert_to_float(x, max_digits=max_digits)
                    if DataframeBeautifier.__is_number(x)
                    else x)

            floating_scientific_notation_rows_complement = \
                dataframe.index.difference(floating_scientific_notation_rows)

            dataframe.loc[floating_scientific_notation_rows_complement] = \
                dataframe.loc[floating_scientific_notation_rows_complement].applymap(
                    lambda x: DataframeBeautifier.__convert_to_float(x, is_scientific=False, max_digits=max_digits)
                    if DataframeBeautifier.__is_number(x)
                    else x
                )
        else:
            dataframe = dataframe.applymap(
                lambda x: DataframeBeautifier.__convert_to_float(x, is_scientific=False, max_digits=max_digits)
                if DataframeBeautifier.__is_number(x)
                else x
            )

        if transpose:
            dataframe = dataframe.T

        return dataframe

    @staticmethod
    def print_console_stream(dataframe, apply_scientific_notation_to_all_columns=True,
                             floating_scientific_notation_columns=None,
                             floating_scientific_notation_rows=None,
                             max_digits=4,
                             transpose=False):
        """
        Beautifying the output of the dataframe for the console stream.

        :param pd.DataFrame() dataframe: Specify the desired dataframe
        :param bool apply_scientific_notation_to_all_columns: Specify if all columns should be in scientific format
        :param list() floating_scientific_notation_columns: Specify the columns that should be in scientific format,
                        ignored when apply_scientific_notation_to_all_columns is set to true
        :param list() floating_scientific_notation_rows: Specify the columns that should be in scientific format,
                        ignored when apply_scientific_notation_to_all_columns is set to true
        :param int max_digits: Specify the maximum floating number digits
        :param bool transpose: Specify weather to transpose the dataframe or not
        """

        dataframe = DataframeBeautifier.__apply_base_operations(
            dataframe=dataframe,
            apply_scientific_notation_to_all_columns=apply_scientific_notation_to_all_columns,
            floating_scientific_notation_columns=floating_scientific_notation_columns,
            floating_scientific_notation_rows=floating_scientific_notation_rows,
            max_digits=max_digits,
            transpose=transpose
        )

        print(tabulate(dataframe, headers='keys', tablefmt='fancy_grid', numalign='left', disable_numparse=True))

    @staticmethod
    def print_markup_text(dataframe, apply_scientific_notation_to_all_columns=True,
                          floating_scientific_notation_columns=None,
                          floating_scientific_notation_rows=None,
                          max_digits=4,
                          transpose=False):
        """
        Beautifying the output of the dataframe for markup languages (specifically GitHub readme file).

        :param pd.DataFrame() dataframe: Specify the desired dataframe
        :param bool apply_scientific_notation_to_all_columns: Specify if all columns should be in scientific format
        :param list() floating_scientific_notation_columns: Specify the columns that should be in scientific format,
                        ignored when apply_scientific_notation_to_all_columns is set to true
        :param list() floating_scientific_notation_rows: Specify the columns that should be in scientific format,
                        ignored when apply_scientific_notation_to_all_columns is set to true
        :param int max_digits: Specify the maximum floating number digits
        :param bool transpose: Specify weather to transpose the dataframe or not
        """

        dataframe = DataframeBeautifier.__apply_base_operations(
            dataframe=dataframe,
            apply_scientific_notation_to_all_columns=apply_scientific_notation_to_all_columns,
            floating_scientific_notation_columns=floating_scientific_notation_columns,
            floating_scientific_notation_rows=floating_scientific_notation_rows,
            max_digits=max_digits,
            transpose=transpose
        )

        print(tabulate(dataframe, headers='keys', tablefmt='github', numalign='left', disable_numparse=True))
