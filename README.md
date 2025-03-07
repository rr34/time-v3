# ToDo
- todo: parse bright star catalog (and send file to Aaron and Ahmed).
- todo: resurrect functions from the old clock and integrate into awim project as appropriate to be able to retrieve pixel positions.
- todo: animate the sun based on a series of times.
- todo: standardize the text representation of the time, starting with the representation I used in the previous version of this clock.
- todo: Expand sun to include moon, planets, stars, moon phase.
- todo: Standard glockenspiel animations.
- todo: connect this app to the back-end awim to position the sun in the correct position based on time.
- todo: front-end needs to be able to generate and work with transparency files to determine if objects are visible / above the horizon, etc. See awim_png_littleblur = awim_png.filter(filter=BoxBlur(pxs_per_minute*5)) and awim_png_bigblur = awim_png.filter(filter=BoxBlur(pxs_per_minute*17))
# Coordinate Types
- SkyCoords specific to object and moment for solar system objects. Once calculated, quickly convertable to RADec and AzArt. Can be created quickly for stars using known RADec.
- RADec specific to object only for stars, same for all moments and earth locations. Specific to moments and objects for solar system objects and when RA Dec is calculated, AzArt is easy.
- AzArt specific to moment and earth observation locations.
- Pixel positions specific to moments, locations, images. Always need AzArt to get pixel positions.
# Functions List
- calculate_astro_data -> rename to calculate_solarsystem_data(): With a list of moments and earth location, respond with solar system objects RA, Dec, Az, Art, (distances in AU for fun) (I think RA Dec is useful to save time when later calculate the AzArt from any Earth location at the same time for a clock using global images)
- RADec_to_AzArt(): Maybe combine with previous since the previous already making SkyCoord objects. With a list of moments, RADec coordinates (from stars data) and earth location respond with AzArt. Previously I omitted stars, but now that I'm going to include stars, the simple step of converting RADec to AzArt is necessary. This is also pure AstroPy. This might end up being an addition to the astropy data function where the ERFA step is simply skipped.
- Concatenate the solar system data to the stars data because from this point on, the calculations are the same for solar system / stars.
- astro_data_to_image(): With awim tag dictionary, moments, and AzArts, respond with ImageAnimations table.
- With a list of ImageAnimations tables and some method of selecting moments, create ImageSelection tables.
- Other per the schema below
# Object Dictionary
This is not by time nor by image, and contains what each object looks like. Moon will require supplemental data because it is the only one that changes over time.
- type: sun, planet, star, moon
- size
- color
# Other
- AstropyData: For earth locations. Columns are body_az, body_art, body_distance (bodies x3 columns). Rows are moments, 3-minute spread. Columns are lists. Quantity 1 of this table for clock where images are near each other. RA Dec easy but not needed since AzArt already produced. This is really just AstroPy data, so named as such. This should be the super-wide result of the astropy function.
- ImageAnimation: For images and time periods. Columns are body_in_bounds, body_x, body_y, opacity?, moon_phase?, moon_brightsidedirection?. Rows are moments, 3-minute spread. Columns are lists. Quantity = number images initially, then multiply by number of time periods to be animated. Add the moon to this or make a separate animation?
- ImageSelection: For moments, 5-minute spread? Columns are body_inbounds, body_x, body_y, opacity. Rows are images. Columns are lists. For selection of which image to display at a given time.

# Clock Data Retrieval and Management
- There will be 4 types of requests. Each has standard response columns and the rows are moments in time. Each response is valid for a single image and designed to streamline generation of SVG animation of the objects on the image.
- The only thing to cache is the AzArts of objects per location and time period because this skips a lot of calculation and will be used for each image as long as the images are close to each other.
- Data retrieval sequence:
  - App gets awim from json.
  - App sends request dictionary which is: awim from json file + moments array + maybe clockMSL? + data request list.
  - API responds with dictionary of the following
  1. sundata
    - pixel position x
    - pixel position y
    - Azimuth just for interesting information
    - Artifae for information and for the sky color animation
    - distance in AU
  2. moondata
    - pixel position x
    - pixel position y
    - Phase angle
    - bright side direction
    - Azimuth just for interesting information
    - Artifae for information and for the sky color animation
    - distance in AU
  3. planetsdata
    - pixel position x
    - pixel position y
    - distance in AU
  4. starsdata
    - pixel position x
    - pixel position y
    - distance in light years
- Javascript represents tables as arrays of arrays, which is really lists of lists. The standard is for each row to be a list, but I think in this case it's best to make each column a list because I'm always using the tables to tick through the values in each column (not know the parameters of each row).
- If the standard animation is to show 4 hours in a 16-second animation, then I want to retrieve 5 hours of data on a 1-hour schedule. 5 hours is 300 minutes, so 300 is the max number of points I will retrieve at once.
- There will be at least two clock state variables representing the time to be shown: 1. current_time and 2. animation_time. These time variables will store just the index to the associated time in the moments array generated by the clock at initialization. The time variables in the clock will be current_minutes_since_init and animation_minutes_since_init.
- In general, components that *do not* animate should know only their current value, with the array of values stored in the app and used to setState. Components that *do* animate should have their whole array and be able to update their appearance by updating a single variable.
# Clock Conventions
- Clock is always moving. Everything is an animation to show the passage of time.
- 'Ticking' is two things
  1. The standard speed of the animation of 15 minutes per second, which is 900x real-time speed. This is fast enough to see movement, slow enough to appreciate events as they occur.
  2. This means if the clock ticks at the pace of a mechanical movement, the 'little ticks' of 18000 beats per hour, which are 5 ticks per second, 3 minutes each at the animation speed.
- 900x real-time speed means you can show:
  - 2.5 hours in a 10-second animation.
  - 3.75 hours in a 15-second animation.
  - 15 hours in a 1-minute animation.
  - 2 hours in an 8-second animation.
  - 4 hours in a 16-second animation. **Let's use this one because it's minus 1 hour to plus 3 hours.**
  - 6 hours in a 24-second animation.
  - full 24-hour day in a 96-second animation (certainly too long of an animation to show all the time).

# Done
- Overlayed a sun on an image using SVG that aligns to the image and stays there through scaling up and down.
- time string ticks