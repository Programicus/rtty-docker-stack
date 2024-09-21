FROM nodered/node-red
RUN sed -i 's/\/\/tours/tours/' node_modules/node-red/settings.js

RUN npm install @node-red-contrib-themes/theme-collection && sed -i 's/\/\/theme: ""/theme: "tokyo-night-storm"/' node_modules/node-red/settings.js

RUN npm i node-red-node-email node-red-contrib-postgresql

USER root

COPY --from=hostetc group /tmp/group
RUN echo '#!/bin/sh' > /tmp/setup_audio_group.sh \
    && echo 'host_audio_gid=$(grep "^audio:" /tmp/group | cut -d: -f3)' >> /tmp/setup_audio_group.sh \
    && echo 'addgroup -g $host_audio_gid host_audio' >> /tmp/setup_audio_group.sh \
    && echo 'addgroup node-red host_audio' >> /tmp/setup_audio_group.sh \
    && chmod +x /tmp/setup_audio_group.sh \
    && /tmp/setup_audio_group.sh \
    && rm /tmp/group /tmp/setup_audio_group.sh

USER node-red
