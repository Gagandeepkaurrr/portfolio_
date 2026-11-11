"use client";
export default function ErrorPage({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main id="main" className="standalone-state">
      <span className="eyebrow">A SHORT PAUSE</span>
      <h1>
        This page needs
        <br />
        <em>another moment.</em>
      </h1>
      <p>The portfolio couldn’t be loaded. Please try again shortly.</p>
      <button className="button button-primary" onClick={() => reset()}>
        Try again ↗
      </button>
    </main>
  );
}
