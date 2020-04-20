import numpy as np
import pandas as pd
import pandas_ta as ta

## Description of several TA features and their classification

# Price differences
# Awesome Oscillator (AO) --> Difference of prices
# Absolute Price Oscillator (APO) --> Difference of prices
# TRUERANGE --> Difference of prices
# Average True Range (ATR) --> Difference of prices
# Detrend Price Oscillator (DPO) --> Difference of prices
# Moving Average, Convergence/Divergence (contains MACD) --> Difference of prices (MACDH is difference of difference of prices)
# Momentum (MOM) --> Difference of prices
# Q Stick (QS) --> Difference of prices


# Volume
# AD --> ((close - open) * volume / (high - low + eps)).cumsum() --> somehow cumsum of weighted volume --> grows constantly
# 'OBV' in col  --> cumsum of signed volume
# Elder's Force Index (EFI) --> (Difference of prices) * Volumen --> Unbound
# Ease of Movement (EOM) --> (Unbound) Ponderation of how is moving high and low. Needs correct 'divisor' adapted to the volume
# Negative Volume Index (NVI) --> (Unbound) CumSum de volumen negativo por ROC
# Positive Volume Index (PVI) --> (Unbound) CumSum de volumen positivo por ROC
# Price-Volume (PVOL) --> (Unbound) Prices * Volumen
# Price-Volume Trend (PVT) --> (Unbound) CumSum of ROC * Volume

# Others
# CCI --> (Difference of prices) / c * MAD(mean price) --> where c is coefficient (default 0.015) and MAD is similar to std
# CG --> Value between 0 and length (default 10)
# Fisher Transform (FISHT) --> (Unbound) Because depends on the std dev of the market price, but it is important to see signals
# Mass Index (MASSI) --> (Unbound) However proportional and centered to slow (default 25) --> Substract and Divide by slow could be a solution
# Log Return (LOGRET) --> Logaritmic of (current price / previous price)
# Slope (SLOPE) --> Difference of prices / length --> Option would be to use as_angle=True which put it as radians
# Vortex (contains VTX) --> abs(Difference of prices) / abs(Difference of prices) --> (Unbound) > 0 centered around a bit less than 1

# Bounded index
# Rate of Change (ROC) --> -100 - 100
# Coppock Curve (COPC) --> -200 - 200 (weighted double of ROC)
# 'Know Sure Thing' (contains KST) --> -100000 - 100000 (weighted 1000 time of ROC) 
# Normalized Average True Range (NATR) --> 0 - 100
# Percent Return (PCTRET) --> -1 - 1
# Percentage Price Oscillator (PPO) --> -100 - 100
# Trix (TRIX)--> -100 - 100
# True Strength Index (TSI) --> -100 - 100
# Ultimate Oscillator (UO) --> -100 - 100
# William's Percent R (WILLR) --> -100 - 0

# Price ranges
# Kaufman's Adaptive Moving Average (KAMA) --> Price range

# Stadistical measures
# Kurtosis (KURT) --> (Unbound) It is a stadistical measure like skewness to measure tail (so if experiment extrem returns +/-)
# Skew (SKEW) --> (Unbound) It is a stadistical measure to measure tail (so if experiment extrem returns +/-)
# STDEV --> It is a stadistical measure --> Difference of prices
# Mean Absolute Deviation (MAD) --> It is a stadistical measure --> Difference of prices
# Variance (VAR) --> It is a stadistical measure --> Difference of prices
# Z Score (Z) --> Price normalized by Z score

eps = 1e-4

KNOWN_COLS = {
    'diff_prices': {
        'cols': ['AO', 'APO', 'ATR', 'DPO', 'MACD', 'MACDH', 'MACDS', 'MOM', 'QS'],
        'add_cols': False,
        'normalize': False,
    },
    'prices': {
        'cols': ['KAMA'],
        'add_cols': True,
        'ref_col': 'close',
        'normalize': False,
    },
    '0_1': {
        'cols': [],
        'add_cols': True,
        'normalize': True,
        'max': 1,
        'min': 0,
        'std': eps,
    },
    '-1_1': {
        'cols': ['PCTRET'],
        'add_cols': True,
        'normalize': True,
        'max': 1,
        'min': -1,
        'std': eps,
    },
    '0_100': {
        'cols': ['NATR', ],
        'add_cols': True,
        'normalize': True,
        'max': 100,
        'min': 0,
        'std': eps,
    },
    '-100_0': {
        'cols': ['WILLR'],
        'add_cols': True,
        'normalize': True,
        'max': 0,
        'min': -100,
        'std': eps,
    },
    '-100_100': {
        'cols': ['ROC', 'PPO', 'PPOH', 'PPOS', 'TRIX', 'TSI', 'UO'],
        'add_cols': True,
        'normalize': True,
        'max': 100,
        'min': -100,
        'std': eps,
    },
    '-200_200': {
        'cols': ['COPC'],
        'add_cols': False,
        'normalize': True,
        'max': 200,
        'min': -200,
        'std': eps,
    },
    '-100000_100000': {
        'cols': ['KST'],
        'add_cols': False,
        'normalize': True,
        'max': 100000,
        'min': -100000,
        'std': eps,
    }
}


def classifyColsByRanges(data, known_cols_dict=KNOWN_COLS):

    def removeFromAllColumns(all_columns, columns):
        for col in columns:
            try:
                i = all_columns.index(col)
                del all_columns[i]
            except ValueError:
                print(f'Column {col} not found in {all_columns}')

    # Transform all abreviated columns into the ones in data   
    ranges_dict = known_cols_dict.copy()
    all_known_columns = []
    for key, values in ranges_dict.items():
        clean_cols = values['cols']
        range_cols = []
        for clean_col in clean_cols:
            columns = list(data.columns[data.columns.str.startswith(clean_col+'_')])
            all_known_columns += columns
            range_cols += columns
        ranges_dict[key]['cols'] = range_cols

    all_columns = list(data.columns)

    # Remove all the already known columns
    removeFromAllColumns(all_columns, all_known_columns)

    for key in ranges_dict:
        columns = []
        if ranges_dict[key]['add_cols']:
            # Get parameters of current range
            if key == 'prices':
                max_ = data[ranges_dict[key]['ref_col']].max()
                min_ = data[ranges_dict[key]['ref_col']].min()
                std_ = data[ranges_dict[key]['ref_col']].std()
                ranges_dict[key]['max'] = max_
                ranges_dict[key]['min'] = min_
                ranges_dict[key]['std'] = std_
            else:
                max_ = ranges_dict[key]['max']
                min_ = ranges_dict[key]['min']
                std_ = ranges_dict[key]['std']

            # Extract columns which match the specification
            columns = list(data[all_columns].dtypes[(data.max() <= max_ + std_) & (data.min() >= min_ - std_)].index)

            # Remove from all_columns
            removeFromAllColumns(all_columns, columns)
            
            # Add sorted unique columns to the pertinent range
            ranges_dict[key]['cols'] = sorted(list(set(columns + ranges_dict[key]['cols'])))

    ranges_dict['others'] = {}
    ranges_dict['others']['cols'] = sorted(all_columns)
    ranges_dict['others']['normalize'] = False 

    return ranges_dict


def normalizeFeatures(data, ranges_dict):
    
    for _, values in ranges_dict.items():
        if values['normalize']:
            columns = values['cols']
            max_ = values['max']
            min_ = values['min']
            data[columns] = (data[columns] - min_) / (max_ - min_)

    return data


def generateTAFeatures(data, exclude_ind=[], args=None, drop_na_rows=True):
    # Indicators not posible to use 'short_run' and 'cross'
    not_ind = ['long_run', 'short_run', 'cross']
    not_ind.append('ichimoku') # Output has to be treaten different because is returning two DataFrames
    not_ind.append('trend_return') # Required trend column

    # Add exclude_ind
    not_ind += exclude_ind

    indicators = [ind for ind in data.ta.indicators(as_list=True) if ind not in not_ind]

    if args is None:
        basic_args = {'append': True, 'ewm': True, 'adjust': True}
        basic_args = dict(zip(indicators, [basic_args] * len(indicators)))

        args = basic_args

    # TODO: Implement short-term and long-term arguments for each indicator

    n_args = len(args)
    for i, (ind, arg) in enumerate(args.items()):
        print(f'{i} out of {n_args} features', end='\r')
        data.ta(kind=ind, **arg)

    if drop_na_rows:
        print(f'Dropping {data.isnull().any(axis=1).sum()} rows because of NaN values')
        data = data[data.notnull().all(axis=1)]

    return data