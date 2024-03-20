from functions.et_helper import winmean, winmean_cl_boot, agg_catcont
import logging
import numpy as np
import pandas as pd
# import scipy.stats

def grid_duration(etmsgs):
    # FIXME I'm not sure we need this function anymore. Remove?
    gridlist = ['LARGEGRID_stop','SMALLGG_before_stop','SMALLGG_after_stop']

    x = etmsgs.query('condition=="Instruction"&exp_event in @gridlist').groupby(['subject','eyetracker','block'],as_index=False).msg_time.apply(np.diff).reset_index()

    x[['grid_time_before','grid_time_beforeAfterDiff']] = pd.DataFrame(x.msg_time.values.tolist(), index= x.index)
    x['grid_time_after'] = x.grid_time_before + x.grid_time_beforeAfterDiff


    try:
        x = x.drop('msg_time',axis=1)
    except  KeyError:
        pass
    #x
    def percentile(n):
        def percentile_(x):
            return np.percentile(x, n)
        percentile_.__name__ = 'percentile_%s' % n
        return percentile_
    y = x.groupby('eyetracker').agg([winmean,percentile(5),percentile(95)])

    y.astype('datetime64[s]')[['grid_time_before','grid_time_after']]
    return(y)


def percentile_(x, n):
    """
    Calculate the n-th percentile of the input array x.
    """
    return np.percentile(x, n)


def percentile(x, n=25, percentile_func=percentile_):
    """
    Set the name of the percentile function based on the provided percentile value n.
    """
    percentile_func.__name__ = 'percentile_%s' % n
    return percentile_func(x, n)


def print_results(df, fields=['duration', 'accuracy', 'rms', 'sd'], round_to=2, agg_first_over_blocks=True, tex=False):
    """
    Print results from a DataFrame with optional formatting for EyeLink and TrackPixx data.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing the data.
        fields (list): List of fields to display results for.
        round_to (int): Number of decimal places to round the results to.
        agg_first_over_blocks (bool): Flag to indicate whether to aggregate first over blocks.
        tex (bool): Flag to enable LaTeX formatting for printing.

    Returns: None

    Notes:
    - This function processes the input DataFrame, calculates statistics, and prints the results.
    - It handles different eyetracker names and formats the output accordingly.
    - The results can be displayed in plain text or LaTeX format based on the 'tex' parameter.
    """

    logger = logging.getLogger(__name__)

    # Determine eyetracker names based on column presence
    if 'eyetracker' in df.columns:
        et = 'eyetracker'
        el = 'el'
        tpx = 'tpx'
    else:
        et = 'et'
        el = 'EyeLink'
        tpx = 'TrackPixx'

    # Aggregate data
    if agg_first_over_blocks:
        df_agg = df.groupby([et, 'subject', 'block'], as_index=False, observed=False).agg(agg_catcont(winmean)).groupby([et, 'subject'], as_index=False, observed=False).agg(agg_catcont(winmean))
    else:
        df_agg = df.groupby([et, 'subject'], as_index=False, observed=False).agg(agg_catcont(winmean))[[et, 'subject'] + fields]

    # Calculate main statistics and differences
    # FIXME this should technically work with `agg_catcont` but it does not.
    tmp_main = df_agg.groupby([et], as_index=False, observed=False).agg([agg_catcont(winmean), lambda x: x.iat[0] if ((x.dtype.name == "object") | (x.dtype.name == "category")) else percentile(x, n=25), lambda x: x.iat[0] if ((x.dtype.name == "object") | (x.dtype.name == "category")) else percentile(x, n=75)])
    
    tmp_el = df_agg.loc[df_agg[et] == el, fields]
    tmp_tpx = df_agg.loc[df_agg[et] == tpx, fields]

    tmp_diff = tmp_el.reset_index(drop=True) - tmp_tpx.reset_index(drop=True)
    tmp_diff_agg = tmp_diff.agg([winmean_cl_boot])
    
    roundto = str(round_to)

    logger.warning('Showing data for the following fields: %s', fields)

    # Print results for each field
    for c in tmp_diff_agg.columns.levels[0]:
        diff_tuple = tuple(tmp_diff_agg[c].values[0])
        main_tuple = tuple(tmp_main[c].values[0],) + tuple(tmp_main[c].values[1])
        all_tuple = (c,) + main_tuple + diff_tuple

        if tex is True:
            results = 'For EyeLink the winsorized mean %s was \SI{%.' + roundto + 'f}{} (IQR: \SI{%.' + roundto + 'f}{} to \SI{%.2f}{}), for TrackPixx \SI{%.' + roundto + 'f}{} (IQR: \SI{%.' + roundto + 'f}{} to \SI{%.' + roundto + 'f}{}), with a paired difference of \SI{%.' + roundto + 'f}{} ($CI_{95}$: \SI{%.' + roundto + 'f}{} to \SI{%.' + roundto + 'f}{})'
            print(results % (all_tuple))
        else:
            results = f'For EyeLink, the winsorized mean {all_tuple[1]:.{roundto}f} (IQR: {all_tuple[2]:.{roundto}f} to {all_tuple[3]:.2f}), for TrackPixx {all_tuple[4]:.{roundto}f} (IQR: {all_tuple[5]:.{roundto}f} to {all_tuple[6]:.{roundto}f}), with a paired difference of {all_tuple[7]:.{roundto}f} (95% CI : {all_tuple[8]:.{roundto}f} to {all_tuple[9]:.{roundto}f})'
            print(results)
