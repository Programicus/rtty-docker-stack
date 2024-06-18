FROM nodered/node-red
RUN sed -i 's/\/\/tours/tours/' node_modules/node-red/settings.js
