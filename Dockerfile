FROM nodered/node-red
RUN sed -i 's/\/\/tours/tours/' node_modules/node-red/settings.js

RUN npm install @node-red-contrib-themes/theme-collection
RUN sed -i 's/\/\/theme: ""/theme: "tokyo-night-storm"/' node_modules/node-red/settings.js

RUN npm i node-red-node-email

USER root

RUN apk add py3-pip python3-dev libffi libffi-dev gfortran openblas openblas-dev musl-dev

USER node-red

ADD pyrtty /pyrtty
RUN pip install scipy --break-system-packages #Run as a seperate layer as this take forever, caching it is pretty good
RUN pip install --break-system-packages -r /pyrtty/requirements.txt
