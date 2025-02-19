# ObsPlan

ObsPlan is a batch tool for planning observations at Bayfordbury, designed to supplement the target checker on our website.

You can provide a list of targets, then specify a date range, and it will generate observability plots for all the requested targets and dates.

The current version has limited functionality, so it only works for deep sky objects. A future version will support Solar System objects (planets, asteroids & comets). 

You can download it from the [releases page.](https://github.com/bayfordbury-observatory/ObsPlan/releases) Please send us any feedback or suggestions!

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
Once you have created a target list, you must edit `ObsPlan-DSO.py` to specify the date range you want to generate plots for. Near the start of the file you should see:

```
start_date = "2025-03-01 12:00"
end_date = "2025-05-01 12:00" 
step_size = 7  # Days`
```

This will create an airmass plot and parameter table for every 7th night from 2025-03-01 to 2025-05-01. If you change it to `step_size = 1`, it will generate a plot for every night. This is OK for short date ranges, but for longer ranges (>1 month), it is sensible to increase the step size. Otherwise, the script will take a long time to run and you will have hundreds of plots to sort through. 

Edit `start_date` and `end_date`, changing the dates but keeping the time at 12:00. Once you have done this, you are ready to run the code.

### Running the code

Once you have updated `targets.txt` and updated the dates and step sizes, you can run the script (e.g.  `python ObsPlan-DSO.py`). Make sure you are running the script from the directory containing `targets.txt `, and be aware that your plots will appear in the same directory. 

Depending on the number of targets and dates, it may take a while to run (usually a few seconds per date). 

If you are running Python in an interactive environment (e.g. Jupyter), you will see the plots appearing as they generate. In any case, the plots will be saved within a folder named `plots`. Inside that folder, a new subfolder will be created every time you run ObsPlan. This is to prevent accidentally overwriting previous outputs, or getting mixed up between different sets of targets and dates. 

Please be aware that the `plots` folder can grow in size very quickly if you run ObsPlan over a large number of dates, or re-run the script many times. 

### Interpreting results


