FROM nodered/node-red
RUN sed -i 's/\/\/tours/tours/' node_modules/node-red/settings.js

RUN npm install @node-red-contrib-themes/theme-collection && sed -i 's/\/\/theme: ""/theme: "tokyo-night-storm"/' node_modules/node-red/settings.js

RUN npm i node-red-node-email node-red-contrib-postgresql
