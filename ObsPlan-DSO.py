import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
from astropy.coordinates import EarthLocation, get_sun, SkyCoord, AltAz, get_body
from astropy.time import Time
from astroplan import Observer, time_grid_from_range, moon_illumination
from astroplan.plots import plot_altitude
import astropy.units as u
from astroquery.simbad import Simbad
from datetime import datetime

# Input start and end dates in ISO format
start_date = "2025-03-01 12:00"
end_date = "2025-05-01 12:00"  # Changed to include two dates for demonstration
step_size = 7  # Days

# Input targets
targets_file = "targets.txt"

# Function to read targets from a file
def read_targets_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Function to get Simbad V magnitude
def get_magnitude(target_name):
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('flux(V)')
    result_table = custom_simbad.query_object(target_name)
    if result_table is not None and len(result_table) > 0:
        mag = result_table['FLUX_V'][0]
        return mag if mag != '--' else None
    return None

# Create output directory with current time
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"plots/{current_time}"
os.makedirs(output_dir, exist_ok=True)

def create_visibility_duration_plot(dates, all_visibility_hours, targets):
    plt.figure(figsize=(14, 8))
    
    # Define a set of distinct markers
    markers = ['>','o','.', 's', '^', 'D', 'v', '>', 'X', 'D', 'P','<']
    # Extend markers list if more targets than markers
    while len(markers) < len(targets):
        markers.extend(markers)
    
    # Generate color cycle matching the main plot
    colors = plt.cm.rainbow(np.linspace(0, 1, len(targets)))
    
    # Plot visibility hours for each target with different markers
    for target_name, color, marker in zip(targets, colors, markers):
        target_hours = [all_visibility_hours[date][target_name] for date in dates]
        plt.plot(dates, target_hours, linestyle='-', color=color, 
                label=target_name, linewidth=2, 
                marker=marker, markersize=10, markeredgewidth=2, 
                markeredgecolor='white', markerfacecolor=color)
    
    # Configure plot
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
    
    plt.title('Target Visibility Duration Over Time', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Hours Visible', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(f'{output_dir}'"/visibility_duration.png", bbox_inches='tight')
    plt.show()
    plt.close()

# Function to create and save visibility table
def create_visibility_table(night, visible_targets, visibility_hours, max_altitudes, apparent_magnitudes, min_lunar_separations):
    table_data = [['Target', 'Visible Hours', 'Max Alt.', 'App. Mag. (V)', 'Lunar Sep.']]
    for target_name in visible_targets:
        hours = visibility_hours.get(target_name, 0)
        max_alt = max_altitudes.get(target_name, 0)
        app_mag = apparent_magnitudes.get(target_name)
        min_sep, min_sep_time = min_lunar_separations.get(target_name, (0, night.datetime))
        table_data.append([
            target_name,
            f"{hours:.2f}",
            f"{max_alt:.1f}°",
            f"{app_mag:.1f}" if app_mag is not None else "N/A",
            f"{min_sep:.1f}°"
        ])

    # Calculate the height of the table based on the number of rows
    num_rows = len(table_data)
    row_height = 0.05  # Adjust this value to change the height of each row
    table_height = row_height * num_rows

    # Create a new figure for the table
    table_fig = plt.figure(figsize=(14, table_height * 14))  # Adjust the figure size as needed
    # Create the table
    table = table_fig.add_subplot(111).table(cellText=table_data[1:],  # Exclude header from cellText
                                             colLabels=table_data[0],  # Use first row as column labels
                                             cellLoc='center',
                                             colWidths=[0.2, 0.15, 0.15, 0.15, 0.35],
                                             bbox=[0, 0, 1, 1])
    # Remove axes
    table_fig.gca().set_axis_off()
    # Set font size and scale for the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    # Set fixed height for each cell in the table and make header bold
    for (row, col), cell in table.get_celld().items():
        cell.set_height(row_height)
        if row == 0:  # This is a header cell
            cell.set_text_props(weight='bold', fontsize='16')
        else:
            cell.set_text_props(fontsize='12')
    # Adjust layout
    table_fig.tight_layout()
    plt.savefig(f'{output_dir}'"/"f'{night.iso.split()[0]}_info.png', bbox_inches='tight')
    plt.show()
    plt.close(table_fig)

# Read targets from file
targets = read_targets_from_file(targets_file)

# Define observing site
observatory_name = "Bayfordbury"
obs_location = EarthLocation(lat=51.775 * u.deg, lon=-0.09 * u.deg, height=66 * u.m)
observer = Observer(location=obs_location, name=observatory_name, timezone="UTC")

# Convert dates to Julian Date
start_jd = Time(start_date, format='iso').jd
end_jd = Time(end_date, format='iso').jd

# Create array of Julian Dates
julian_dates = np.arange(start_jd, end_jd + 1, step_size)

# Initialize lists and dictionaries for storing data across all dates
plot_dates = []
visibility_data = {}

# Define a set of distinct markers for the altitude plots
altitude_markers = ['>','o','.', 's', '^', 'D', 'v', '>', 'X', 'D', 'P','<']
while len(altitude_markers) < len(targets):
    altitude_markers.extend(altitude_markers)

# Loop over each day
for jd in julian_dates:
    night = Time(jd, format='jd')
    current_date = Time(jd, format='jd').datetime
    plot_dates.append(current_date)  # Add current date to list

    # Calculate sunset and sunrise times
    sunset = observer.sun_set_time(night, which='nearest')
    sunrise = observer.sun_rise_time(night + 1 * u.day, which='nearest')

    # Calculate night's midpoint
    night_midpoint = sunset + (sunrise - sunset) / 2

    # Define time range
    start_time = night_midpoint - 7.5 * u.hour
    end_time = night_midpoint + 7.5 * u.hour

    # Create time grids
    time_grid = time_grid_from_range([start_time, end_time], time_resolution=20 * u.minute)
    time_grid_hires = time_grid_from_range([start_time, end_time], time_resolution=1 * u.minute)

    # Define frames
    frame = AltAz(obstime=time_grid, location=obs_location)
    frame_hires = AltAz(obstime=time_grid_hires, location=obs_location)

    # Calculate Sun's altitude
    sun_altaz = get_sun(time_grid_hires).transform_to(frame_hires)
    sun_alt = sun_altaz.alt.deg

    # Calculate Moon's position
    moon_altaz = get_body("moon", time_grid).transform_to(frame)
    moon_alt = moon_altaz.alt.deg
    moon_az = moon_altaz.az.deg
    
    # Set up main plot
    fig, ax1 = plt.subplots(figsize=(14, 10))
    
    # Generate color cycle
    colors = plt.cm.rainbow(np.linspace(0, 1, len(targets)))

    # Dictionaries to store data
    visibility_hours = {}
    min_lunar_separations = {}
    max_altitudes = {}
    apparent_magnitudes = {}
    visible_targets = []
    
    # Lists for legend
    legend_handles = []
    legend_labels = []

    # Process each target
    for target_name, color, marker in zip(targets, plt.cm.rainbow(np.linspace(0, 1, len(targets))), altitude_markers):
        target = SkyCoord.from_name(target_name)

        # Calculate target positions
        targ_altaz = target.transform_to(frame)
        targ_alt = targ_altaz.alt.deg
        targ_altaz_hires = target.transform_to(frame_hires)
        targ_alt_hires = targ_altaz_hires.alt.deg

        # Convert times to datetime
        targ_times = targ_altaz.obstime.datetime
        targ_times_hires = targ_altaz_hires.obstime.datetime

        # Calculate visibility
        visibility_mask = (targ_alt_hires >= 20) & (sun_alt <= -18)
        visible_times = targ_times_hires[visibility_mask]

        if len(visible_times) > 0:
            hours_visible = (visible_times[-1] - visible_times[0]).total_seconds() / 3600
            visibility_hours[target_name] = hours_visible
            visible_targets.append(target_name)
            
            # Plot altitude with markers
            line = ax1.plot(targ_times, targ_alt, color=color, linestyle='-',
                          marker=marker, markevery=1, markersize=8,
                          markerfacecolor=color, markeredgecolor='white',
                          markeredgewidth=0, linewidth=2)[0]
            ax1.set_ylim(0,90)
            legend_handles.append(line)
            legend_labels.append(target_name)
            
            # Calculate lunar separation
            moon_coord = SkyCoord(alt=moon_altaz.alt, az=moon_altaz.az, frame='altaz', 
                                obstime=time_grid, location=obs_location)
            target_coord = SkyCoord(alt=targ_altaz.alt, az=targ_altaz.az, frame='altaz', 
                                  obstime=time_grid, location=obs_location)
            angular_separation = moon_coord.separation(target_coord).deg
            
            min_separation = np.min(angular_separation)
            min_separation_time = targ_times[np.argmin(angular_separation)]
            min_lunar_separations[target_name] = (min_separation, min_separation_time)
            
            max_altitudes[target_name] = np.max(targ_alt)
            apparent_magnitudes[target_name] = get_magnitude(target_name)
        else:
            visibility_hours[target_name] = 0

    # Store visibility hours for this date
    visibility_data[current_date] = visibility_hours.copy()
    
     # Skip if no targets are visible
    if not visible_targets:
        plt.close(fig)
        continue

    # Plot moon with distinctive dashed line
    moon_line = ax1.plot(targ_times, moon_alt, color='gray', ls="--", 
                        marker='o', markevery=5, markersize=0)[0]
    legend_handles.append(moon_line)
    legend_labels.append("Moon")

    # Add twilight shading
    ax1.fill_between(targ_times_hires, 0, 90, sun_alt > 0, color="yellow", zorder=0, alpha=0.4)
    ax1.fill_between(targ_times_hires, 0, 90, sun_alt < 0, color="cornflowerblue", zorder=0, alpha=0.4)
    ax1.fill_between(targ_times_hires, 0, 90, sun_alt < -6, color="blue", zorder=-1, alpha=0.4)
    ax1.fill_between(targ_times_hires, 0, 90, sun_alt < -12, color="navy", zorder=0, alpha=0.4)
    ax1.fill_between(targ_times_hires, 0, 90, sun_alt < -18, color="black", zorder=0, alpha=1)

    # Configure x-axis
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Add labels and title
    ax1.set_title(f"Target Visibility - {night.iso.split()[0]}", fontsize=16)
    ax1.set_ylabel("Altitude (deg)", fontsize=12)
    ax1.set_xlabel("Time (UTC)", fontsize=12)
    ax1.tick_params(labelbottom=True, top=True)

    # Add legend
    ax1.legend(legend_handles, legend_labels, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig(f'{output_dir}'"/"f'{night.iso.split()[0]}_airm.png', bbox_inches='tight')
    plt.show()
    plt.close(fig)


    # Create and save table for this date
    create_visibility_table(night, visible_targets, visibility_hours, max_altitudes, apparent_magnitudes, min_lunar_separations)

# Create visibility duration plot after processing all dates
create_visibility_duration_plot(plot_dates, visibility_data, targets)