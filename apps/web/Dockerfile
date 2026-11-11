FROM node:26.13.0-alpine AS dependencies
WORKDIR /app
RUN npm install --global pnpm@12.18.0
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/package.json

FROM dependencies AS production-dependencies
RUN pnpm install --frozen-lockfile --prod

FROM dependencies AS build
RUN pnpm install --frozen-lockfile
COPY apps/web/ apps/web/
RUN pnpm --filter @portfolio/web build

FROM node:26.13.0-alpine AS runtime
WORKDIR /app/apps/web
ENV NODE_ENV=production HOST=0.0.0.0 PORT=3000
RUN addgroup -g 10001 portfolio && adduser -D -u 10001 -G portfolio portfolio
COPY --from=production-dependencies --chown=portfolio:portfolio /app/node_modules /app/node_modules
COPY --from=production-dependencies --chown=portfolio:portfolio /app/apps/web/node_modules ./node_modules
COPY --from=build --chown=portfolio:portfolio /app/apps/web/package.json ./package.json
COPY --from=build --chown=portfolio:portfolio /app/apps/web/build ./build
USER portfolio
EXPOSE 3000
CMD ["./node_modules/.bin/react-router-serve", "build/server/index.js"]
