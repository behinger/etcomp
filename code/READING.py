import functions.et_helper as  helper
from functions.et_helper import winmean_cl_boot, winmean, winmean_cl_boot, agg_catcont
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from plotnine import *
import functions.plotnine_theme as mythemes
from scipy.ndimage.filters import gaussian_filter


def plot_heatmap(reading_df, wordbounds):
    """
    Make a heatmap of the freeview fixation data.

    Parameters:
    - reading_df (DataFrame): DataFrame containing reading event data.
    - wordbounds (DataFrame): DataFrame containing fixation count data.

    Returns:
    - None

    Notes:
    - This function generates heatmaps and scatter plots for EyeLink and TrackPixx fixation data.
    - It calculates the mean fixation locations and displays them with specified smoothing.
    - The function can generate horizontal or 2x2 subplots based on the 'only_horizontal_heatmap' parameter.
    - Information about fixations and picture IDs is saved in a markdown file 'heatmap_info.md'.
    """

    # Calculate screenshot size in degrees (screen size 1920 x 1080 pixels)
    # they are centered  --> divide by 2
    pic_size_horizontal = helper.size_px2deg(1920) / 2
    pic_size_vertical = helper.size_px2deg(1200) / 2

    # Extract mean fixation location data for EyeLink and TrackPixx
    tpx_x_coords = list(reading_df.query('et == "TrackPixx"').mean_gx)
    tpx_y_coords = list(reading_df.query('et == "TrackPixx"').mean_gy)
    
    el_x_coords = list(reading_df.query('et == "EyeLink"').mean_gx)
    el_y_coords = list(reading_df.query('et == "EyeLink"').mean_gy)

    # Ensure equal number of x and y gaze fixation positions
    assert(len(tpx_x_coords) == len(tpx_y_coords))
    assert(len(el_x_coords) == len(el_y_coords))

    # Define sigmas for Kernel smoothing
    # 0 : no smoothing for the scatterplot
    # 300: we selected 300 std as we want 3 degrees visual angle and have bins of size 0.01
    sigmas = [0, 300, 0, 300]

    # Display horizontal heatmaps for EyeLink and TrackPixx (2 subplots)
    fig, axs = plt.subplots(1, 2)

    # Generate TrackPixx heatmap
    img, extent = make_heatmap(tpx_x_coords, tpx_y_coords, sigmas[1], pic_size_horizontal, pic_size_vertical)
    axs[0].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
    axs[0].set_aspect('equal')
    axs[0].set_title("TrackPixx Smoothing with 3 $^\circ$")

    # Generate EyeLink heatmap
    img, extent = make_heatmap(el_x_coords, el_y_coords, sigmas[3], pic_size_horizontal, pic_size_vertical)
    axs[1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
    axs[1].set_aspect('equal')
    axs[1].set_title("EyeLink Smoothing with 3 $^\circ$")

    fig.tight_layout(pad=3.0)  # Adjust padding between subplots and around the figure
    plt.subplots_adjust(wspace=0.4)  # Adjust the width space between subplots
    plt.savefig("freeview-heatmap.png", dpi=300)
    plt.show()

def make_heatmap(x_coords, y_coords, sigma, pic_size_horizontal, pic_size_vertical):
    """
    Generate a heatmap from the given x and y coordinates with specified smoothing.
    This function creates a 2D histogram from the provided x and y coordinates.
    The histogram is then smoothed using a Gaussian filter with the specified sigma value.
    The extent of the heatmap is calculated based on the picture size in degrees.
    The heatmap is transposed before returning to ensure correct orientation.

    Parameters:
        x_coords (list or array): List or array of x-coordinates.
        y_coords (list or array): List or array of y-coordinates.
        sigma (float): Standard deviation for Gaussian smoothing.
        pic_size_horizontal (float): Horizontal size of the picture in degrees.
        pic_size_vertical (float): Vertical size of the picture in degrees.

    Returns:
        heatmap (np.ndarray): 2D array representing the heatmap.
        extent (list): List containing the extent of the heatmap [xmin, xmax, ymin, ymax].
    """

    # Create bins for the 2D histogram
    # picturesize in degrees to picturesize in degrees with a stepsize of 0.01
    bins = [np.arange(-pic_size_horizontal, pic_size_horizontal, step=0.01),
            np.arange(-pic_size_vertical, pic_size_vertical, step=0.01)]

    # Generate the 2D histogram
    heatmap, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=bins)

    # Apply Gaussian smoothing to the heatmap
    heatmap = gaussian_filter(heatmap, sigma=sigma)

    # Calculate the extent of the heatmap
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    # Transpose the heatmap to ensure correct orientation
    return heatmap.T, extent


def plot_number_of_fixations(raw_fix_count_df):
    """
    investigate on the number of fixations
    """

    # mean number of fixations for each subject
    mean_fixcount_per_pic = raw_fix_count_df.groupby(['et', 'subject'],as_index=False).mean()
    
    # plotting mean number of detected fixation during freeview condition for each subject
    return (ggplot(mean_fixcount_per_pic, aes(x='et', y='fix_counts')) +
             geom_line(aes(group='subject'), color='lightblue') +
             geom_point(color='lightblue') +
             stat_summary(fun_data=winmean_cl_boot,color='black',size=0.8, position=position_nudge(x=0.05,y=0)) +
             xlab("Eye Trackers") + 
             ylab("Mean number of fixations per picture") +
             ggtitle('Mean number of fixations') +
             theme(plot_margin_top=0.05))
