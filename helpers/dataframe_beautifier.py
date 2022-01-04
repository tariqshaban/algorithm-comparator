from tabulate import tabulate


class DataframeBeautifier:
    """
    Static methods for beautifying the output of the dataframe.

    Methods
    -------
        print_console_stream(dataframe):
            Beautifying the output of the dataframe for the console stream.
        print_markup_text(dataframe):
            Beautifying the output of the dataframe for markup languages (specifically GitHub readme file).
    """

    @staticmethod
    def print_console_stream(dataframe):
        """
        Beautifying the output of the dataframe for the console stream.

        :param pd.DataFrame() dataframe: Specify the desired dataframe
        """

        print(tabulate(dataframe, headers='keys', tablefmt='fancy_grid', numalign="left"))

    @staticmethod
    def print_markup_text(dataframe):
        """
        Beautifying the output of the dataframe for markup languages (specifically GitHub readme file).

        :param pd.DataFrame() dataframe: Specify the desired dataframe
        :return: The dataframe beautified
        """

        print(tabulate(dataframe, headers='keys', tablefmt='github', numalign="left"))
