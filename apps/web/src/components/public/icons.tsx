import type { SVGProps } from "react";
export function Arrow({
  diagonal = false,
  ...props
}: SVGProps<SVGSVGElement> & { diagonal?: boolean }) {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      {...props}
    >
      {diagonal ? (
        <path
          d="M6 18 18 6M6 6h12v12"
          stroke="currentColor"
          strokeWidth="1.5"
        />
      ) : (
        <path
          d="M4 12h15m-6-6 6 6-6 6"
          stroke="currentColor"
          strokeWidth="1.5"
        />
      )}
    </svg>
  );
}
export function Asterisk() {
  return (
    <svg
      className="asterisk"
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M32 2v60M2 32h60M10.8 10.8l42.4 42.4M10.8 53.2l42.4-42.4"
        stroke="currentColor"
        strokeWidth="2"
      />
    </svg>
  );
}
