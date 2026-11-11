import type { ActionFunctionArgs, LoaderFunctionArgs } from 'react-router';
import { proxyApiRequest } from '@/lib/api/proxy.server';
export const loader = ({ request }: LoaderFunctionArgs) => proxyApiRequest(request);
export const action = ({ request }: ActionFunctionArgs) => proxyApiRequest(request);
