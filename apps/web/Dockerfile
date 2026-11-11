FROM node:26.13.0-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm install --global pnpm@12.18.0
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --frozen-lockfile
COPY apps/web/ apps/web/
RUN pnpm --filter @portfolio/web build

FROM node:26.13.0-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
RUN addgroup -g 10001 portfolio && adduser -D -u 10001 -G portfolio portfolio
COPY --from=build --chown=portfolio:portfolio /app/apps/web/.next/standalone ./
COPY --from=build --chown=portfolio:portfolio /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=build --chown=portfolio:portfolio /app/apps/web/public ./apps/web/public
USER portfolio
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
