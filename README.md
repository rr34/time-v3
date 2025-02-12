# Notes
- Overlayed a sun on an image using SVG that aligns to the image and stays there through scaling up and down.
- todonext: standardize awim tag to use the largest pixel dimensions, never change, and only check that aspect ratio matches. Get the dimensions directly from the camera awim tag and base all pixel measurements off that, including pixel angular sizes.
- This project will be based on image sizes of 4K = 3840 x 2160. That will be the SVG size I use. Rather than communicate the image size to awim API, the awim API will always respond with pixel positions based on the size in the tag, which will always be the underlying camera pixel tag dimensions. The answer can be adjusted by just about any software / language since simly scaling the image is linear. I'm not drawing directly on the image really anyway. I'm drawing with an SVG canvas that does not necessarily match the image size. It only matches aspect ratio and gets scaled to the same size. awim doesn't need to care about that or handle that scaling.
- todo: connect this app to the back-end awim to position the sun in the correct position based on time.
- todo: resurrect functions from the old clock and integrate into awim project as appropriate to be able to retrieve pixel positions.
- todo: animate the sun based on a series of times.
- todo: standardize the text representation of the time, starting with the representation I used in the previous version of this clock.
- todo: Expand sun to include moon, planets, stars, moon phase.
- todo: Standard glockenspiel animations.

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
