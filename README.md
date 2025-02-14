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
# Schema (Tables List)
These tables are what the clock will use. These are the deliverables from awim.
- AstroPyData: For earth locations. Columns are body_az, body_art, body_distance (bodies x3 columns). Rows are moments. Quantity 1 of this table for clock where images are near each other. RA Dec easy but not needed. This is really just AstroPy data, so named as such. This should be the super-wide result of the astropy function.
- ImageAnimation: For images and time periods. Columns are body_inbounds, body_x, body_y, opacity?, moon_phase?, moon_brightsidedirection?. Rows are moments. Quantity = number images initially, then multiply by number of time periods to be animated. Add the moon to this or make a separate animation?
- ImageSelection: For moments, columns are body_inbounds, body_x, body_y, opacity. Rows are images. For selection of which image to display at a given time.
- AstroClockTimeStrings: For time periods. Single column is time_text. Rows are moments. Quantity one of these intially, then to add them for different animations like year-long time lapses, moon orbit lapses, etc. Already have several good functions for calculating events people might like to relate to.
# Done
- Overlayed a sun on an image using SVG that aligns to the image and stays there through scaling up and down.

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default tseslint.config({
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

- Replace `tseslint.configs.recommended` to `tseslint.configs.recommendedTypeChecked` or `tseslint.configs.strictTypeChecked`
- Optionally add `...tseslint.configs.stylisticTypeChecked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and update the config:

```js
// eslint.config.js
import react from 'eslint-plugin-react'

export default tseslint.config({
  // Set the react version
  settings: { react: { version: '18.3' } },
  plugins: {
    // Add the react plugin
    react,
  },
  rules: {
    // other rules...
    // Enable its recommended rules
    ...react.configs.recommended.rules,
    ...react.configs['jsx-runtime'].rules,
  },
})
```
