from plotnine import *
import numpy as np
import pandas as pd
import functions.et_make_df as make_df
from functions.et_helper import winmean, winmean_cl_boot, agg_catcont
import MISC
import logging
from scipy.stats import binned_statistic

logger = logging.getLogger(__name__)

def process_lum(etsamples, etmsgs):
    """
    Process pupil dilation and luminance data from the dilation task. It calls the `process_lum_singlesub()` 
    function for both EyeLink and TrackPixx for each participant. Then it concatenates the result.

    Parameters:
        etsamples (pd.DataFrame): A DataFrame containing the eye-tracking sample data.
        etmsgs (pd.DataFrame): A DataFrame containing the eye-tracking message data.

    Returns:
        all_lum (pd.DataFrame): A consolidated DataFrame containing the processed luminance information.

    """
    all_lum = pd.DataFrame()
    for subject in etsamples.subject.unique():
        for et in ['tpx','el']:
            logger.info("subject:%s, et:%s"%(subject,et))
            all_lum = pd.concat([all_lum, process_lum_singlesub(etsamples,etmsgs)])
            
    return(all_lum)


def process_lum_singlesub(etsamples, etmsgs, td=[-1,5]):
    """
    Process the luminance information for a single subject and eyetracker. It filters the `etsamples` and 
    `etmsgs` DataFrames for the specified subject and eyetracker. Then it calles the `make_epochs()` function
    from make_df, which finds all samples that are in the range of +/-td. Lastly, the  function then applies 
    the `standardize_lum()` to normalize the luminance values based on SD.

    Parameters:
        etsamples (pd.DataFrame): A DataFrame containing the eyetracking sample data.
        etmsgs (pd.DataFrame): A DataFrame containing the eyetracking message data.
        td (list, optional): The time window (in seconds) to consider for the luminance information. Default is [-1, 5].

    Returns:
        lum_epoch (pd.DataFrame): A DataFrame containing the processed luminance information for the specified subject and eye-tracking modality.
    """
    
    condquery = 'condition == "DILATION" & exp_event=="lum"'
    td = [-1, 12]
    query = 'subject==@subject & eyetracker==@eyetracker'

    lum_epoch = make_df.make_epochs(etsamples.query(query),etmsgs.query(query+'&'+condquery), td=td)

    #normalize by SD division. Could be made better e.g. by quantile division
    lum_epoch = lum_epoch.groupby(["msg_time"], as_index=False).apply(lambda rows:standardize_lum(rows))
    return(lum_epoch)


def standardize_lum(df):
    """
    Normalize the luminance values in the input DataFrame by dividing them by the median of the baseline period.
    If there are no baseline time points, the function sets the 'pa_norm' (normalized pupil area) column to NaN for all rows.
    If there are baseline time points, the function calculates the median of the luminance values ('pa') during 
    the baseline period, and divides all the luminance values by this median to obtain the normalized luminance values.
    These values are added as the 'pa_norm' column to the input DataFrame.

    Parameters:
        df (pd.DataFrame): A DataFrame containing the luminance data, with a 'td' column indicating the time relative to an event, and a 'pa' column containing the luminance values.

    Returns:
        df (pd.DataFrame): The input DataFrame with a new 'pa_norm' column containing the normalized luminance values.
    """
    logger = logging.getLogger(__name__)

    if np.sum(df.td<0) == 0:
        logger.warning('Trial has no baseline.')
        df.loc[:,"pa_norm"] = np.nan
    else:
        df.loc[:,"pa_norm"] = df.pa / np.median(df.loc[df.td<0,'pa'])
    return(df)


def normalize_lum_bin(rows, epochs, nbins=100):
    """
    Bin the normalized luminance values in the input DataFrame and calculate the mean value for each bin.

    Parameters:
        rows (pd.DataFrame): A DataFrame containing the luminance data for a single group (defined by the grouping columns).
        epochs (pd.DataFrame): The original DataFrame containing the luminance data, used to determine the minimum and maximum time values for the binning.
        nbins (int, optional): The number of bins to use for the binning. Default is 100.

    Returns:
        df (pd.DataFrame): A DataFrame containing the binned and averaged luminance data, with columns for subject, block, eyetracker, time (td), normalized luminance (pa_norm), and the original luminance (lum).

    Functionality:
    1. The function first creates a set of bin edges by linearly spacing `nbins + 1` values between the minimum and maximum time values in the `epochs` DataFrame.
    2. It then uses the `binned_statistic()` function from the `scipy.stats` module to bin the normalized luminance values (`rows.pa_norm`) based on the time values (`rows.td`), and calculate the mean value for each bin.
    3. The function then creates a new DataFrame with the binned time values (calculated as the midpoint of each bin), the mean normalized luminance values, and the original subject, block, eyetracker, and luminance values.
    """
    newtd = np.linspace(epochs.td.min(), epochs.td.max(),nbins+1)
    binned = binned_statistic(x=rows.td, values=rows.pa_norm, statistic="mean", bins=newtd)    
    df = pd.DataFrame({"subject":rows.subject.iloc[0],
                        "block":rows.block.iloc[0],
                        "eyetracker":rows.eyetracker.iloc[0],
                        "td":newtd[1:]-(newtd[1]-newtd[0])/2,
                        "pa_norm":binned[0],
                        "lum":rows.lum.iloc[0]})
    return df


def bin_lum(lum_epoch):
    """
    Bin the normalized luminance values in the input DataFrame and return the binned data. This is useful for plotting data (bin+take means).
    The function first defines the grouping columns to be used for the binning: subject, eyetracker, lum, and block.
    It then uses the `normalize_lum_bin()` to bin the luminance data for each group, passing the original `lum_epoch` DataFrame as a parameter.

    Parameters:
        lum_epoch (pd.DataFrame): A DataFrame containing the luminance data, with columns for subject, block, eyetracker, time (td), and normalized luminance (pa_norm).

    Returns:
        lum_epoch_binned (pd.DataFrame): A DataFrame containing the binned and averaged luminance data, with columns for subject, block, eyetracker, time (td), normalized luminance (pa_norm), and the original luminance (lum).
    """
    grouping_cols = ["subject", "eyetracker", "lum", "block"]
    lum_epoch_binned = lum_epoch.groupby(grouping_cols, as_index=False, observed=False).apply(lambda rows: normalize_lum_bin(rows, lum_epoch))    
    lum_epoch_binned = lum_epoch_binned.reset_index()
    return(lum_epoch_binned)


def plot_time_all(df):
    """
    For all subjects, create a plot of the average normalized luminance values over time, with error bars representing the 95% confidence interval.
    The function first groups the `df` DataFrame by the relevant columns and aggregates the data using the `winmean` function from et_helper.
    It then creates a new column `plot_grouping` that combines the `eyetracker` and `lum` columns, which will be used to group the data in the plot.
    Finally, it created a ggplot object that can be further customized.

    Parameters:
        df (pd.DataFrame): A DataFrame containing the binned and averaged luminance data, with columns for time (td), eye-tracker (eyetracker), luminance type (lum), and normalized luminance (pa_norm). It's likely called `all_lum_binned`

    Returns:
        plot (ggplot): A ggplot object representing the plot.
    """
    grouping_cols = ["td", "eyetracker", "subject", "lum"]
    all_lum_binned_noblock = df.groupby(grouping_cols, as_index=False).agg(agg_catcont(winmean))
    all_lum_binned_noblock.loc[:,'plot_grouping'] = all_lum_binned_noblock.eyetracker + all_lum_binned_noblock.lum.map(str)
    plot = (ggplot(all_lum_binned_noblock.query('lum>0'), aes(x='td',y='pa_norm', group="plot_grouping", color="lum", shape="eyetracker"))
                +stat_summary(fun_data=winmean_cl_boot, position=position_dodge(width=0.06), size=0.2) 
                +geom_vline(xintercept=[0,3,10] )
                +scale_color_gradient(low='black',high='lightgray')+xlim((-1,6))
                +scale_shape_manual(values=[">","<"])
    )
    return plot


def plot_time_diff(all_lum_binned, subject="sub-001"):
    """
    Create a plot of the difference in normalized luminance values over time between EyeLink and TrackPixx for a single subject.
    The function first groups the `all_lum_binned` DataFrame by the columns `td`, `lum`, `block`, and `subject`, and calculates 
    the difference in normalized luminance values (`pa_norm`) between the two eye-tracker modalities for each group. The result 
    is stored in a new DataFrame `all_lum_diff`.
    It then creates a new column `plot_grouping` that combines the `block` and `lum` columns, which will be used to group the data 
    in the plot. Next, it filters data for only one subject.
    Finally, it creates a plot.

    Parameters:
        all_lum_binned (pd.DataFrame): A DataFrame containing the binned and averaged luminance data, with columns for time (td), eye-tracker (eyetracker), luminance type (lum), block, subject, and normalized luminance (pa_norm).
        subject (str, optional): The subject for which to plot the difference. Default is "sub-001".

    Returns:
        plot (ggplot): A ggplot object
    """
    grouping_cols = ["td","lum","block","subject"]
    all_lum_diff = all_lum_binned.groupby(grouping_cols, as_index=False).pa_norm.agg(np.diff)
    all_lum_diff.loc[:,'pa_norm'] = pd.to_numeric(all_lum_diff.loc[:,'pa_norm'])
    all_lum_diff.loc[:,'plot_grouping'] = all_lum_diff.block.map(str) + all_lum_diff.lum.map(str)
    plot_df = all_lum_diff.query("subject==@subject")
    
    plot = (ggplot(plot_df, aes(x='td', y='pa_norm', color="lum", group="plot_grouping"))
                +geom_line()
                +geom_vline(xintercept=[0,3,10] )
                +scale_color_gradient(low='black',high='lightgray')
                +xlim((-1,6))
                +ylab("Eyetracker difference in pupilsize")
                +scale_shape_manual(values=[">","<"])
    )
    return plot


def calc_mean(df, t_from=2, t_to=3):
    """
    Calculate the mean normalized luminance values for a given time window (f_from to to_to).

    Parameters:
        df (pd.DataFrame): A DataFrame containing the luminance data, with columns for time (td), luminance type (lum), block, subject, eye-tracker (eyetracker), and normalized luminance (pa_norm). Probably called `all_lum`.
        t_from (float, optional): The start time of the time window, in seconds. Default is 2.
        t_to (float, optional): The end time of the time window, in seconds. Default is 3.

    Returns:
    pandas.DataFrame: A DataFrame containing the mean normalized luminance values for each luminance type, block, subject, and eye-tracker, within the specified time window.
    """
    grouping_cols = ["lum","block","subject","eyetracker","msg_time"]
    mean_lum = df.query("td>@t_from & td<=@t_to").groupby(grouping_cols, as_index=False).pa_norm.agg(winmean)
    return mean_lum


def plot_mean(df):
    """
    Create a plot of the mean normalized luminance values for each luminance type and eye-tracker modality.

    Parameters:
        df (pd.DataFrame): A DataFrame containing the luminance data, with columns for luminance type (lum), subject, eye-tracker (eyetracker), and normalized luminance (pa_norm). Probably called `all_lum`.

    Returns:
        plot (ggplot): A ggplot object for further customization.
    """
    mean_lum = calc_mean(df)
    grouping_cols = ["lum","subject","eyetracker"]
    plot_df = mean_lum.query("lum>0").groupby(grouping_cols, as_index=False).pa_norm.agg(winmean)
    plot = (ggplot(plot_df, aes(x="lum", y="pa_norm", shape="eyetracker", color="lum"))
     +stat_summary(fun_data=winmean_cl_boot,position=position_dodge(width=15))
     +geom_point(alpha=0.1)
     +scale_color_gradient(low='black',high='lightgray')
     +scale_shape_manual(values=[">","<"])
    )
    return plot


def plot_diff(df):
    """
    Create a plot of the difference in mean normalized luminance values between EyeLink and TrackPixx for each luminance type and subject.

    Parameters:
        df (pd.DataFrame): A DataFrame containing the luminance data, with columns for luminance type (lum), block, subject, and normalized luminance (pa_norm). Probably called `all_lum`.

    Returns:
        plot (ggplot): A ggplot object for further customization
    """
    mean_lum = calc_mean(df)
    diff_lum = mean_lum.query("lum>0").groupby(["lum","block","subject"], as_index=False).pa_norm.agg(np.diff)
    diff_lum.loc[:,'pa_norm'] = pd.to_numeric(diff_lum.loc[:,'pa_norm'])
    
    plot = (ggplot(diff_lum, aes(x="subject", y="pa_norm", color="lum", group="lum"))
     +stat_summary(fun_data=winmean_cl_boot, position=position_dodge(width=0.5))
     +scale_color_gradient(low='black', high='lightgray')
     +ylab('pupil area difference (Eyelink-TrackPixx)[a.u.]')
    )
    return plot