import Link from "next/link";
import { getSite } from "@/lib/api/public";
import { PublicShell } from "@/components/public";
export const dynamic = "force-dynamic";
export const metadata = { title: "Privacy — Gagandeep Kaur" };
export default async function Privacy() {
  const { content } = await getSite();
  return (
    <PublicShell content={content}>
      <main id="main" className="container prose-page">
        <div id="top" />
        <Link className="breadcrumb" href="/">
          ← Back to the portfolio
        </Link>
        <span className="eyebrow">A NOTE ON YOUR INFORMATION</span>
        <h1>Privacy, in plain language.</h1>
        <p>
          When you send a message, this site stores your name, email address,
          optional subject, and message so Gagandeep can receive and respond to
          your inquiry.
        </p>
        <h2>Your messages</h2>
        <p>
          Messages are held in a private inbox accessible to the owner. They are
          retained for up to {content.contact_retention_days ?? 180} days,
          subject to the scheduled cleanup process, or deleted sooner by the
          owner. For a short retry window, a receipt and non-content fingerprint
          may remain after deletion to prevent duplicate messages.
        </p>
        <h2>Security and cookies</h2>
        <p>
          The public portfolio does not use advertising or analytics cookies. A
          session cookie is used when the owner signs in to administer the site.
          Temporary, hashed source identifiers help limit abusive submissions;
          raw IP addresses are not stored in contact messages.
        </p>
        <h2>External links</h2>
        <p>
          Project demos, GitHub, LinkedIn, and certificate links lead to other
          websites with their own privacy practices. They receive a visit only
          when you choose to open them.
        </p>
        <h2>Questions or deletion requests</h2>
        <p>
          Email{" "}
          <a href={`mailto:${content.profile.email}`}>
            {content.profile.email}
          </a>{" "}
          to ask about information you have submitted or request its deletion.
        </p>
      </main>
    </PublicShell>
  );
}
