# Stage 1 : installation des dépendances de production
FROM node:26.13.0-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Stage 2 : image d'exécution, Alpine + binaire node seul (sans npm ni en-têtes)
FROM alpine:3.24.4
RUN apk add --no-cache libstdc++ libgcc libatomic \
    && addgroup -g 1000 node \
    && adduser -u 1000 -G node -s /bin/sh -D node
COPY --from=deps /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY server.js ./
EXPOSE 3000
USER node
CMD ["node", "server.js"]
