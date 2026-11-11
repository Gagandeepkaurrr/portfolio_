export function loader() { throw new Response('Not found', { status: 404 }); }
export { NotFoundView as default } from '@/components/public/not-found';
