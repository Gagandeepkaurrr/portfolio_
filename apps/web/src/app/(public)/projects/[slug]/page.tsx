import type { Metadata } from "next";
import { cache } from "react";
import { notFound, permanentRedirect } from "next/navigation";
import { getProject, getSite, PublicApiError } from "@/lib/api/public";
import { PublicShell, ProjectDetail } from "@/components/public";
export const dynamic = "force-dynamic";
const load = cache(async (slug: string) => {
  const { content } = await getSite();
  let project = content.projects.find((p) => p.slug === slug);
  if (!project) {
    try {
      const alias = await getProject(slug);
      project = content.projects.find((p) => p.id === alias.project.id);
    } catch (e) {
      if (e instanceof PublicApiError && e.status === 404) notFound();
      throw e;
    }
  }
  if (!project) notFound();
  return { content, project };
});
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const { project, content } = await load(slug);
  return {
    title:
      project.seo_title || `${project.title} — ${content.profile.full_name}`,
    description: project.seo_description || project.summary,
    alternates: {
      canonical: `${content.settings.site_url.replace(/\/$/, "")}/projects/${project.slug}`,
    },
    openGraph: {
      title: project.title,
      description: project.summary,
      type: "article",
    },
  };
}
export default async function ProjectPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const { content, project } = await load(slug);
  if (project.slug !== slug) permanentRedirect(`/projects/${project.slug}`);
  return (
    <PublicShell content={content}>
      <ProjectDetail project={project} projects={content.projects} />
    </PublicShell>
  );
}
