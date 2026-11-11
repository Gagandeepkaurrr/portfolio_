import { redirect, useLoaderData, type LoaderFunctionArgs, type MetaFunction } from 'react-router';
import { getSite, getProject } from '@/lib/api/public.server';
import { ProjectDetail, PublicShell } from '@/components/public';

export async function loader({ params }: LoaderFunctionArgs) {
  const { content } = await getSite();
  const slug = params.slug || '';
  let project = content.projects.find(item => item.slug === slug);
  if (!project) {
    const alias = await getProject(slug);
    project = content.projects.find(item => item.id === alias.project.id);
  }
  if (!project) throw new Response('Not found', { status: 404 });
  if (project.slug !== slug) throw redirect(`/projects/${project.slug}`, { status: 308, headers: { 'Cache-Control': 'no-store' } });
  return { content, project };
}
export const meta: MetaFunction<typeof loader> = ({ data }) => data ? [
  { title: data.project.seo_title || `${data.project.title} — ${data.content.profile.full_name}` },
  { name: 'description', content: data.project.seo_description || data.project.summary },
  { tagName: 'link', rel: 'canonical', href: `${data.content.settings.site_url.replace(/\/$/, '')}/projects/${data.project.slug}` },
  { property: 'og:title', content: data.project.title }, { property: 'og:description', content: data.project.summary }, { property: 'og:type', content: 'article' },
] : [{ title: 'Project — Gagandeep Kaur' }];
export default function Project() { const { content, project } = useLoaderData<typeof loader>(); return <PublicShell content={content}><ProjectDetail project={project} projects={content.projects} /></PublicShell>; }
