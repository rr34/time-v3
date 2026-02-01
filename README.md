# TODOnext, to deploy to a raspberry pi in Razor's Edge
- enable dummy locations in DB for clock strings only around the world - today!
- use the photo location for the clock location? done already?
- Label views with E, W, S, N and center azimuth / artifae.
- Text Clock and Images Clock, start with images clock instead of text. May delay some seconds, not minutes.
- make sure site reloads sufficiently to stay open indefinitely.
- permalink to all the clocks that have been made https://nathanruffing.com/timev3/
- Use the photo name from field in the DB.
- Cycle through quickly with the labels.
- Cycle through in a standard order.
- Show the development text only in a devmode setting.
- Distances of solar system objects.
- Above the the horizon after sunset / following the sun after sunset report.
- would be pretty easy to make a png overlay
- Standard glockenspiel animations by generating custom moment_arrays, possibly / probably one image at a time instead of animated, especially for the moon. ... Actually, maybe animated is possible by improving how the moon phase is shown with ChatGPT in VS Code now. See if it can figure it out.
- Glockenspiel: moon rising / setting each day for a moon cycle.

## todo eventually
- TODO: review data transfer size between awim / api / client (compression, paging, or streaming).
- generate high-res PNG overlays of photos for a single moment in time for nice astrophotography posters or for a sequence of photos for time lapse videos.
- Rising, peaking, setting objects like a current events for the user in clock strings.
- optimize for phones
- the progress indicator is out of sync from the animation. Fix.
- make a sequence feature in addition to the tags, probably integrated with the tags?
- reduce the size of the strings / gallery toggle. Make toggle instead of selector.
- make addhours a slider if there is an efficient way to do it?
- I think the app can save multiple SVG animations, but can it save multiple images? 20 images? or get PNG files from backend each time displayed?
- add equinoxes and solstices to clock strings.
- add distances to the display.
- maybe add possibility of a background layer L2? L3 is the svg L4 is the foreground. No, probably unnecessary complication.
- TODO: since awim tags are official source of duplicate information, clock could be able to regenerate the whole relevant portion of the DB with the awim tags from its files (not important for a while)
- parse bright star catalog (and send file to Aaron and Ahmed).
- Glockenspiel: follow a constellation?
- Glockenspiel: sunrise / sunset every day or week for a year?
- frontend needs to be able to generate and work with transparency files to determine if objects are visible / above the horizon, etc. See awim_png_littleblur = awim_png.filter(filter=BoxBlur(pxs_per_minute*5)) and awim_png_bigblur = awim_png.filter(filter=BoxBlur(pxs_per_minute*17))
# animation problems
- limit the distance off screen the celestial bodies can go to improve animation. Ensure the animation runs only on screen then the bodies stay close off-screen but transparent until they appear again.
- the problems are mostly with the beginning and end of an animation and they are not as bad with shorter step size, like 15 minutes. 
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
- The only thing to cache is the AzArts of objects per location and time period because AzArt includes a lot of calculation and is the same for each image as long as the images are close to each other.
- Data retrieval sequence:
  - App gets awim from json.
  - App sends request dictionary which is: awim from json file + moments array + maybe clockMSL? + data request list.
  - API responds with dictionary of the following: see comment in awimlib.py file in awim project.
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
