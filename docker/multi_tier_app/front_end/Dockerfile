FROM node:alpine

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY app/package.json /usr/src/app
# COPY app/.env.development /usr/src/app

RUN npm install

ADD app/public /usr/src/app/public
ADD app/src /usr/src/app/src

RUN npm build

EXPOSE 3000

CMD ["npm","start"]