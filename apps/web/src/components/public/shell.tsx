import { Link } from 'react-router';
import type { ReactNode } from "react";
import type { PublicSiteContent } from "@/lib/types";
import { SiteHeader } from "./header";
import { Arrow } from "./icons";
export function ExternalLink({
  href,
  children,
  className,
}: {
  href: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={className}
    >
      {children}
      <span className="sr-only"> (opens in a new tab)</span>
    </a>
  );
}
export function PublicShell({
  content,
  children,
}: {
  content: PublicSiteContent;
  children: ReactNode;
}) {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <SiteHeader content={content} />
      {children}
      <footer className="site-footer">
        <div className="container footer-top">
          <Link to="/" className="footer-name">
            {content.profile.full_name}
            <span>·</span>
          </Link>
          <p>
            Built with care,
            <br />
            continuously learning.
          </p>
          <a className="back-top" href="#top">
            Back to top <Arrow style={{ transform: "rotate(-90deg)" }} />
          </a>
        </div>
        <div className="container footer-bottom">
          <span>
            © {new Date().getFullYear()} {content.profile.full_name}
          </span>
          <div>
            {content.profile.github_url && (
              <ExternalLink href={content.profile.github_url}>
                GitHub ↗
              </ExternalLink>
            )}
            {content.profile.linkedin_url && (
              <ExternalLink href={content.profile.linkedin_url}>
                LinkedIn ↗
              </ExternalLink>
            )}
            <Link to="/privacy">Privacy</Link>
          </div>
        </div>
      </footer>
    </>
  );
}
