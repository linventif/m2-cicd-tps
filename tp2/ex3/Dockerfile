FROM node:latest
WORKDIR /app
COPY . /app
RUN npm install
EXPOSE 3000
ENV NODE_ENV=development
USER root
CMD ["node", "server.js"]
