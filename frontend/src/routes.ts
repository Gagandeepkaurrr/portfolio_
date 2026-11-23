import { index, route, type RouteConfig } from '@react-router/dev/routes';

export default [
  index('routes/home.tsx'),
  route('privacy', 'routes/privacy.tsx'),
  route('projects/:slug', 'routes/project.tsx'),
  route('admin', 'routes/admin-layout.tsx', [
    index('routes/admin-index.tsx'),
    route('login', 'routes/login.tsx'),
    route('*', 'routes/admin-page.tsx'),
  ]),
  route('sitemap.xml', 'routes/sitemap.ts'),
  route('robots.txt', 'routes/robots.ts'),
  route('api/v1/*', 'routes/api.ts'),
  route('*', 'routes/not-found.tsx'),
] satisfies RouteConfig;
