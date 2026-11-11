import { Link } from 'react-router';
import type { PublicSiteContent, PublicProject, SectionKey } from "@/lib/types";
import { dateRange } from "@/lib/format";
import { Arrow, Asterisk } from "./icons";
import { PortraitFrame, ProjectMedia } from "./media";
import { ExternalLink } from "./shell";
import { ContactForm } from "./contact-form";
export function ChapterHeading({
  number,
  label,
  heading,
  description,
}: {
  number: string;
  label: string;
  heading: string;
  description?: string;
}) {
  return (
    <div className="chapter-heading">
      <div className="chapter-label">
        <span>{number}</span>
        <span className="chapter-rule" />
        {label}
      </div>
      <h2>{heading}</h2>
      {description && <p>{description}</p>}
    </div>
  );
}
export function ProjectSpread({
  project,
  index,
}: {
  project: PublicProject;
  index: number;
}) {
  return (
    <article className={`project-spread ${index % 2 ? "reverse" : ""}`}>
      <div className="project-heading-mobile">
        <span className="eyebrow">
          0{index + 1} / {project.category}
        </span>
        <h3>
          <Link to={`/projects/${project.slug}`}>{project.title}</Link>
        </h3>
      </div>
      <ProjectMedia media={project.cover} title={project.title} index={index} />
      <div className="project-story">
        <span className="eyebrow">
          0{index + 1} / {project.category}
        </span>
        <h3>
          <Link to={`/projects/${project.slug}`}>{project.title}</Link>
        </h3>
        <p>{project.summary}</p>
        <ul className="technology-list" aria-label="Technologies">
          {project.technologies.map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
        <Link className="text-link" to={`/projects/${project.slug}`}>
          View project <Arrow diagonal />
        </Link>
      </div>
    </article>
  );
}
export function PortfolioHome({ content }: { content: PublicSiteContent }) {
  const { profile: p, settings: s } = content;
  const shown = (id: SectionKey) => s.visible_sections.includes(id);
  const intro = (id: SectionKey) => s.section_intros[id];
  const featured = content.recognition.find(
    (x) => x.id === s.featured_recognition_id,
  );
  const projects = s.featured_project_ids.length
    ? content.projects.filter((x) => s.featured_project_ids.includes(x.id))
    : content.projects;
  return (
    <main id="main">
      <section className="hero container" id="top" aria-labelledby="hero-title">
        <PortraitFrame media={p.portrait} />
        <div className="hero-copy">
          <div className="eyebrow hero-eyebrow">
            <span className="tiny-star">✳</span>
            {p.hero_eyebrow}
          </div>
          <h1 id="hero-title">
            {p.full_name.split(" ").slice(0, -1).join(" ")}
            <br />
            <em>{p.full_name.split(" ").slice(-1)}</em>
            <span className="name-dot">.</span>
          </h1>
          <p className="hero-role">{p.role_label}</p>
          <p className="hero-intro">{p.intro}</p>
          <div className="hero-actions">
            {shown("work") && (
              <Link to="#work" className="button button-primary">
                Explore my work <Arrow diagonal />
              </Link>
            )}
            {p.resume_available && s.show_resume && (
              <a
                href={p.resume_url || "/api/v1/resume"}
                className="resume-link"
              >
                View résumé <Arrow diagonal />
              </a>
            )}
          </div>
          <div className="hero-context">
            <span aria-hidden="true">↳</span>
            {p.institution_context}
          </div>
          {s.availability_enabled && s.availability_text && (
            <p>{s.availability_text}</p>
          )}
        </div>
      </section>
      <div className="container journal-divider">
        <span>THOUGHTFUL INTERFACES. MEANINGFUL CONNECTIONS.</span>
        <span>SCROLL TO EXPLORE ↓</span>
      </div>
      {shown("work") && (
        <section className="section container work-section" id="work">
          <div className="section-opening">
            <ChapterHeading
              number="01"
              label={s.section_labels.work}
              {...intro("work")}
            />
            <span className="section-aside">
              A SMALL SELECTION,
              <br />
              AN ONGOING PRACTICE.
            </span>
          </div>
          <div className="project-spreads">
            {projects.map((project, index) => (
              <ProjectSpread key={project.id} project={project} index={index} />
            ))}
          </div>
        </section>
      )}
      {shown("experience") && (
        <section
          className="section container experience-section"
          id="experience"
        >
          <ChapterHeading
            number="02"
            label={s.section_labels.experience}
            {...intro("experience")}
          />
          <div className="experience-list">
            {content.experience.map((item) => (
              <article key={item.id} className="experience-row">
                <div className="entry-date">
                  {dateRange(item.start, item.end, item.is_current)}
                </div>
                <div>
                  <span className="eyebrow">{item.organization}</span>
                  <h3>{item.role}</h3>
                  <p>{item.description}</p>
                  {item.bullets.length > 0 && (
                    <ul className="plain-bullets">
                      {item.bullets.map((x) => (
                        <li key={x}>{x}</li>
                      ))}
                    </ul>
                  )}
                  <ul className="technology-list">
                    {item.technologies.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                </div>
                <Arrow diagonal className="entry-arrow" />
              </article>
            ))}
          </div>
        </section>
      )}
      {shown("community") && (
        <section className="community-section section" id="community">
          <div className="container">
            <div className="community-intro">
              <ChapterHeading
                number="03"
                label={s.section_labels.community}
                {...intro("community")}
              />
              <Asterisk />
            </div>
            <div className="community-grid">
              <ol className="leadership-timeline">
                {content.leadership.map((item) => (
                  <li key={item.id}>
                    <div className="entry-date">
                      {dateRange(item.start, item.end, item.is_current)}
                    </div>
                    <h3>{item.role}</h3>
                    <span className="leadership-org">{item.organization}</span>
                    {item.description && <p>{item.description}</p>}
                    {item.bullets.length > 0 && (
                      <ul className="plain-bullets">
                        {item.bullets.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    )}
                    {item.metrics.length > 0 && (
                      <div className="role-metrics">
                        {item.metrics.map((m) => (
                          <div key={m.label}>
                            <strong>{m.value}</strong>
                            <span>{m.label}</span>
                            <small>{m.context}</small>
                          </div>
                        ))}
                      </div>
                    )}
                  </li>
                ))}
              </ol>
              {featured && (
                <aside className="event-callout">
                  <div className="eyebrow">A COMMUNITY MILESTONE</div>
                  <span className="event-year">
                    {featured.event_name}
                    {featured.event_year &&
                    !featured.event_name.includes(String(featured.event_year))
                      ? ` ${featured.event_year}`
                      : ""}
                  </span>
                  <div className="event-metric">
                    {featured.metric?.value}
                    <span>{featured.metric?.label}</span>
                  </div>
                  <div className="event-callout-bottom">
                    <h3>{featured.title}</h3>
                    <p>{featured.description}</p>
                  </div>
                  <span className="callout-flower" aria-hidden="true">
                    ✳
                  </span>
                </aside>
              )}
            </div>
          </div>
        </section>
      )}
      {shown("about") && (
        <section className="section container about-section" id="about">
          <ChapterHeading
            number="04"
            label={s.section_labels.about}
            {...intro("about")}
          />
          <div className="about-grid">
            <div className="about-biography">
              <p>{p.biography}</p>
              <span className="handwritten">
                Learning, one chapter at a time.
              </span>
            </div>
            <div className="education">
              <h3 className="subsection-title">
                Education <span>01—03</span>
              </h3>
              {content.education.map((item) => (
                <article key={item.id}>
                  <span className="entry-date">
                    {item.start_year && `${item.start_year} — `}
                    {item.is_current ? "Present" : item.completion_year}
                  </span>
                  <h4>{item.qualification}</h4>
                  <p>{item.institution}</p>
                  <span className="result">
                    {item.result_label}: {item.result_value}
                    {item.result_label.toLowerCase() === "percentage"
                      ? "%"
                      : ""}
                    {item.result_note && <small> · {item.result_note}</small>}
                  </span>
                </article>
              ))}
            </div>
          </div>
          <div className="skills-area">
            <h3 className="subsection-title">
              Tools & foundations <span>ALWAYS LEARNING</span>
            </h3>
            <div className="skill-groups">
              {content.skill_groups.map((item) => (
                <div key={item.id}>
                  <h4>{item.group_name}</h4>
                  <ul>
                    {item.items.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
          <div className="recognition-grid">
            <div>
              <h3 className="subsection-title">A few proud moments</h3>
              <div className="recognition-list">
                {content.recognition
                  .filter(
                    (x) =>
                      !shown("community") || x.id !== s.featured_recognition_id,
                  )
                  .map((item) => (
                    <article key={item.id}>
                      <span className="recognition-star" aria-hidden="true">
                        ✳
                      </span>
                      <div>
                        <h4>{item.title}</h4>
                        <p>{item.description}</p>
                        {item.link && (
                          <ExternalLink href={item.link}>
                            View recognition ↗
                          </ExternalLink>
                        )}
                      </div>
                    </article>
                  ))}
              </div>
            </div>
            <div>
              <h3 className="subsection-title">Beyond the classroom</h3>
              {content.certifications.map((item) => (
                <article className="certificate" key={item.id}>
                  <span className="eyebrow">CERTIFICATION</span>
                  <h4>{item.title}</h4>
                  <p>{item.issuers.join(" & ")}</p>
                  {item.credential_url && (
                    <ExternalLink
                      href={item.credential_url}
                      className="text-link"
                    >
                      View certificate <Arrow diagonal />
                    </ExternalLink>
                  )}
                </article>
              ))}
            </div>
          </div>
        </section>
      )}
      {shown("contact") && (
        <section className="contact-section section" id="contact">
          <div className="container contact-grid">
            <div>
              <ChapterHeading
                number="05"
                label={s.section_labels.contact}
                {...intro("contact")}
              />
              <a className="contact-email" href={`mailto:${p.email}`}>
                {p.email}
                <Arrow diagonal />
              </a>
              {p.phone_e164 && p.phone_display && (
                <a href={`tel:${p.phone_e164}`}>{p.phone_display}</a>
              )}
              <div className="contact-socials">
                {p.github_url && (
                  <ExternalLink href={p.github_url}>
                    GitHub <Arrow diagonal />
                  </ExternalLink>
                )}
                {p.linkedin_url && (
                  <ExternalLink href={p.linkedin_url}>
                    LinkedIn <Arrow diagonal />
                  </ExternalLink>
                )}
              </div>
              <Asterisk />
            </div>
            <ContactForm email={p.email} />
          </div>
        </section>
      )}
    </main>
  );
}
