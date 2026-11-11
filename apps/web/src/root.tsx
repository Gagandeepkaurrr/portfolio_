import { data, isRouteErrorResponse, Links, Meta, Outlet, Scripts, ScrollRestoration, useRouteError, useRouteLoaderData, type HeadersFunction, type LoaderFunctionArgs } from 'react-router';
import { documentNonce, pageHeaders } from '@/lib/security.server';
import { NotFoundView } from '@/components/public/not-found';
import '@fontsource/instrument-serif/400.css';
import '@fontsource/instrument-serif/400-italic.css';
import '@fontsource/manrope/400.css';
import '@fontsource/manrope/500.css';
import '@fontsource/manrope/600.css';
import '@fontsource/manrope/700.css';
import '@/styles/globals.css';

export function loader({ request }: LoaderFunctionArgs) {
  const nonce = documentNonce();
  return data({ nonce }, { headers: pageHeaders(new URL(request.url).pathname, nonce, process.env.NODE_ENV === 'development', process.env.APP_ENV === 'production') });
}
export const headers: HeadersFunction = ({ loaderHeaders }) => loaderHeaders;
// A CSP nonce belongs to the original document, not to client-side navigation requests.
export const shouldRevalidate = () => false;

export function Layout({ children }: { children: React.ReactNode }) {
  const root = useRouteLoaderData<typeof loader>('root');
  return <html lang="en" data-scroll-behavior="smooth"><head>
    <meta charSet="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="icon" href="/favicon.svg" /><Meta /><Links />
  </head><body>{children}<ScrollRestoration nonce={root?.nonce} /><Scripts nonce={root?.nonce} /></body></html>;
}
export default function App() { return <Outlet />; }
export function ErrorBoundary() {
  const error = useRouteError();
  if (isRouteErrorResponse(error) && error.status === 404) return <NotFoundView />;
  return <main id="main" className="standalone-state"><title>Temporarily unavailable — Gagandeep Kaur</title><span className="eyebrow">A SHORT PAUSE</span><h1>This page needs<br /><em>another moment.</em></h1><p>The portfolio couldn’t be loaded. Please try again shortly.</p><button className="button button-primary" onClick={() => window.location.reload()}>Try again ↗</button></main>;
}
