from enum import Enum


class AdjustedPValueMethods(Enum):
    """
    Enumerate adjusted p-value methods
    """

    BONFERRONI = 'bonferroni'  # one-step correction

    HOLM = 'holm'  # step-down method using Bonferroni adjustments

    SIMES_HOCHBERG = 'simes-hochberg'  # step-up method (independent)

    HOMMEL = 'hommel'  # closed method based on Simes tests (non-negative)
