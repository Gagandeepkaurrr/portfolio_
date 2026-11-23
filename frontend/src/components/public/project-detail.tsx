import { Link } from 'react-router';
import type { PublicProject } from "@/lib/types";
import { ProjectMedia } from "./media";
import { ExternalLink } from "./shell";
import { Arrow } from "./icons";
export function ProjectDetail({
  project,
  projects,
}: {
  project: PublicProject;
  projects: PublicProject[];
}) {
  const index = projects.findIndex((p) => p.id === project.id);
  const other = projects.find((p) => p.id !== project.id);
  return (
    <main id="main" className="project-detail">
      <div className="container" id="top">
        <Link to="/#work" className="breadcrumb">
          ← Back to selected work
        </Link>
        <header className="project-detail-header">
          <span className="eyebrow">{project.category}</span>
          <h1>
            {project.title}
            <span className="name-dot">.</span>
          </h1>
          <p>{project.summary}</p>
          <ul className="technology-list">
            {project.technologies.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        </header>
        <ProjectMedia
          media={project.cover}
          title={project.title}
          index={Math.max(0, index)}
          large
        />
        <div className="project-content">
          <aside>
            <span className="chapter-label">THE PROJECT</span>
            <p>{project.category}</p>
            <div className="project-links">
              {project.live_url && (
                <ExternalLink href={project.live_url} className="text-link">
                  {project.slug === "previous-portfolio"
                    ? "Visit previous portfolio"
                    : "Visit live project"}{" "}
                  <Arrow diagonal />
                </ExternalLink>
              )}
              {project.repository_url && (
                <ExternalLink
                  href={project.repository_url}
                  className="text-link"
                >
                  Source code <Arrow diagonal />
                </ExternalLink>
              )}
            </div>
          </aside>
          <div>
            <section>
              <h2>Overview</h2>
              <p>{project.overview}</p>
            </section>
            {project.feature_bullets.length > 0 && (
              <section>
                <h2>What I built</h2>
                <ul className="project-features">
                  {project.feature_bullets.map((x) => (
                    <li key={x}>
                      <Arrow />
                      {x}
                    </li>
                  ))}
                </ul>
              </section>
            )}
            {project.narrative_blocks.map((block) => (
              <section key={block.id}>
                {block.heading && <h2>{block.heading}</h2>}
                {block.kind === "paragraph" ? (
                  <p>{block.text}</p>
                ) : (
                  <ul className="plain-bullets">
                    {block.items?.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                )}
              </section>
            ))}
          </div>
        </div>
        {project.gallery.length > 0 && (
          <section className="project-gallery" aria-label="Project gallery">
            {project.gallery.map((media) => (
              <ProjectMedia
                key={media.asset_id}
                media={media}
                title={media.alt}
              />
            ))}
          </section>
        )}
        <nav className="project-next" aria-label="More to explore">
          {other ? (
            <Link to={`/projects/${other.slug}`}>
              <span className="eyebrow">THE NEXT CHAPTER</span>
              <span className="next-title">
                {other.title}
                <Arrow diagonal />
              </span>
            </Link>
          ) : (
            <Link to="/#work">
              More selected work <Arrow />
            </Link>
          )}
          <Link to="/#contact" className="text-link">
            Start a conversation <Arrow diagonal />
          </Link>
        </nav>
      </div>
    </main>
  );
}
