# ObsPlan

ObsPlan is a batch tool for planning observations at Bayfordbury, designed to supplement the target checker on our website.

You can provide a list of targets, and specify a date range, then it will generate airmass plots for all of the requested targets and dates.

The current version has limited functionality, so it only works for deep sky objects. A future version will support Solar System objects (planets, asteroids & comets).

You can download it from the [releases page.](https://github.com/bayfordbury-observatory/ObsPlan/releases)

## Using ObsPlan-DSO.py

### Requirements

You must install the following Python packages:
- numpy
- matplotlib
- astropy
- astroplan
- astroquery

### Targets

Firstly, you must provide a list of targets. These should be listed in `targets.txt`, which needs to be in the same directory as `ObsPlan-DSO.py`.

`targets.txt` should have one target name per line. An example file is provided with pre-filled targets. 

Target names should be resolvable by SIMBAD, for example:
- M31
- Vega
- BD+26 2245
- 2MASS J11404947+2530339
- Gaia DR3 4005347343309786112
- HD 48915

Raw coordinates (RA and dec) are not accepted.

### Dates
Once you have created a target list, you must edit `ObsPlan-DSO.py` to specify the date range you want to generate plots for. Specifically, we are editing lines 14, 15 and 16:

```
start_date = "2025-03-01 12:00"
end_date = "2025-05-01 12:00" 
step_size = 7  # Days`
```

This will create an airmass plot and parameter table for every 7th night from 2025-03-01 to 2025-05-01. If you change it to `step_size = 1`, it will generate a plot for every night. This is OK for short date ranges, but for longer ranges (>1 month), it is sensible to increase the step size. 

Edit `start_date` and `end_date`, changing the dates but keeping the time at 12:00. Once you have done this, you are ready to run the code.

### Running the code

(to be written)
