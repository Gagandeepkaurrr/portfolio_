import Link from "next/link";
export default function NotFound() {
  return (
    <main id="main" className="standalone-state">
      <Link href="/" className="brand-mark">
        GK<span>·</span>
      </Link>
      <span className="eyebrow">404 / AN UNWRITTEN PAGE</span>
      <h1>
        This chapter
        <br />
        <em>isn’t here.</em>
      </h1>
      <p>The page may have moved, or this story is still being written.</p>
      <div className="hero-actions">
        <Link href="/" className="button button-primary">
          Back to home ↗
        </Link>
        <Link href="/#work" className="text-link">
          Explore the work →
        </Link>
      </div>
    </main>
  );
}
