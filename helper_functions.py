########################################################################################################################
# Helper Functions
########################################################################################################################
# Author
#   David Cavanaugh
#
# Created Date
#   2021-11-16
#
# Description
#   Functions to help in the formatting and manipulation of data before modelling it
#
# Notes
#   1)
#
########################################################################################################################
# BEGIN WORKING DOCUMENTS
########################################################################################################################
# Import Statements
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


########################################################################################################################
# Formatting the raw data
def dataset_formatter(fips_code, fire_data, weather_data, min_date, max_date) -> pd.DataFrame:
    """Dataset creator

    Take in a FIPS Code and then output a fully formatted dataset

    Parameters
    ----------
    fips_code: str
        The FIPS code, it is a five digit string indicating the state/county to utilize
    fire_data: pd.DataFrame
        Dataframe of fire data
    weather_data: pd.DataFrame
        Weather data
    min_date: str
        Lowest date in the dataframe to build an index from
    max_date: str
        Highest date in the dataframe to build an index to

    Returns
    -------
    data: pd.DataFrame
        Formatted dataset
    """
    # Format Fire Data
    date_index = pd.date_range(start=min_date, end=max_date, freq='MS')

    subset_data = fire_data[fire_data['FIPS_CODE'] == fips_code].set_index('MONTH')

    subset_data = subset_data.reindex(date_index).reset_index().rename({'index': 'MONTH'}, axis=1)

    subset_data[["FIPS_CODE", "COUNTY_AREA", "STATE_CODE"]] = \
        subset_data[["FIPS_CODE", "COUNTY_AREA", "STATE_CODE"]].fillna(method='ffill').fillna(method='bfill')

    subset_data['TOTAL_BURN_AREA'] = subset_data['TOTAL_BURN_AREA'].fillna(0)

    # State Data

    state_data = fire_data.groupby(by=['MONTH', 'STATE_CODE']).agg({'TOTAL_BURN_AREA': sum}).reset_index()
    state_data.rename({'TOTAL_BURN_AREA': 'STATE_BURN_AREA'}, axis=1, inplace=True)

    # National Data
    nation_data = fire_data.groupby(by=['MONTH']).agg({'TOTAL_BURN_AREA': sum}).reset_index()
    nation_data.rename({'TOTAL_BURN_AREA': 'NATIONAL_BURN_AREA'}, axis=1, inplace=True)

    # Merge State Data
    subset_state = pd.merge(subset_data, state_data, how='inner', on=['STATE_CODE', 'MONTH'])

    # Merge National Data
    subset_national = pd.merge(subset_state, nation_data, how='inner', on='MONTH')

    # Merge Weather Data
    subset_weather = pd.merge(subset_national, weather_data, how='inner', on=['MONTH', 'STATE_CODE'])

    # Catch any last nulls from merges
    subset_weather[['STATE_BURN_AREA', 'NATIONAL_BURN_AREA']] = \
        subset_weather[['STATE_BURN_AREA', 'NATIONAL_BURN_AREA']].fillna(0)

    return subset_weather


########################################################################################################################
# END WORKING DOCUMENT
########################################################################################################################
