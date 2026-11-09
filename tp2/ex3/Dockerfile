FROM node:26.13.0-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY server.js ./
EXPOSE 3000
USER root
CMD ["node", "server.js"]
