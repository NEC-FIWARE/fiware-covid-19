FROM node:10.23-alpine

ENV PROJECT_ROOTDIR /app/

RUN apk update && apk add git \
    && cd / \
    && git clone -b fiware --depth=1 https://github.com/NEC-FIWARE/covid19.git \
    && mv covid19 $PROJECT_ROOTDIR \
    && cd $PROJECT_ROOTDIR \
    && yarn install

WORKDIR $PROJECT_ROOTDIR

EXPOSE 3000
ENV HOST 0.0.0.0

CMD ["yarn", "dev"]
