# Downloaded Libraries Documentation

This directory contains locally downloaded JavaScript/CSS libraries for offline use.

## Downloaded Libraries

All libraries are used under their respective open-source licenses:

### JavaScript Libraries
- **Vue.js 3.5.13** - MIT License
  - File: `vue.global.min.js`
  - Source: https://github.com/vuejs/core

- **Vuetify 3.7.4** - MIT License
  - Files: `vuetify.min.js`, `vuetify.min.css`
  - Source: https://github.com/vuetifyjs/vuetify

- **Plotly.js 2.35.2** - MIT License
  - File: `plotly.min.js`
  - Source: https://github.com/plotly/plotly.js

- **Socket.IO 4.5.4** - MIT License
  - File: `socket.io.min.js`
  - Source: https://github.com/socketio/socket.io-client

### CSS & Fonts
- **Material Design Icons 7.4.47** - Apache License 2.0
  - Files: `materialdesignicons.min.css`, `fonts/materialdesignicons-webfont.*`
  - Source: https://github.com/Templarian/MaterialDesign-Webfont

## Updating Libraries

To update to the latest versions, run:
```bash
python3 download_libs.py
```

This will download all libraries to `static/libs/`.

## Fallback Mechanism

The application uses a fallback mechanism:
1. First tries to load from local files
2. Falls back to CDN if local files are not available

This ensures the app works both offline and online.

## License Compliance

All libraries are used in compliance with their licenses:
- MIT License: Permits commercial use, modification, distribution, and private use
- Apache 2.0: Permits commercial use, modification, distribution, patent use, and private use

Full license texts are available in the respective library repositories.
