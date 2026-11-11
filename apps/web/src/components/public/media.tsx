"use client";
import { useState } from "react";
import type { PublicMediaRef } from "@/lib/types";
import { Asterisk } from "./icons";
export function PortraitFrame({ media }: { media: PublicMediaRef | null }) {
  const [failed, setFailed] = useState(false);
  return (
    <div className="portrait-wrap">
      <div className="portrait-frame">
        {media && !failed ? (
          <img
            src={media.url}
            alt={media.alt}
            width={media.width || 800}
            height={media.height || 1000}
            fetchPriority="high"
            onError={() => setFailed(true)}
          />
        ) : (
          <div
            className="portrait-placeholder"
            role="img"
            aria-label="GK portrait placeholder. Portrait coming soon."
          >
            <div className="portrait-orbit orbit-one" />
            <div className="portrait-orbit orbit-two" />
            <span className="portrait-initials" aria-hidden="true">
              GK<span>·</span>
            </span>
            <span className="portrait-caption" aria-hidden="true">
              PORTRAIT COMING SOON
            </span>
            <span className="portrait-corner" aria-hidden="true">
              A WORK IN PROGRESS,
              <br />
              ALWAYS.
            </span>
          </div>
        )}
      </div>
      <div className="portrait-stamp">
        <Asterisk />
      </div>
      <div className="portrait-footnote">
        <span>CODE. CURIOSITY. COMMUNITY.</span>
        <span>© {new Date().getFullYear()}</span>
      </div>
    </div>
  );
}
export function ProjectMedia({
  media,
  title,
  index = 0,
  large = false,
}: {
  media: PublicMediaRef | null;
  title: string;
  index?: number;
  large?: boolean;
}) {
  const [failed, setFailed] = useState(false);
  if (media && !failed)
    return (
      <figure className={`project-media ${large ? "media-large" : ""}`}>
        <img
          src={media.url}
          alt={media.alt}
          width={media.width || 1200}
          height={media.height || 800}
          loading="lazy"
          onError={() => setFailed(true)}
        />
        {media.caption && <figcaption>{media.caption}</figcaption>}
      </figure>
    );
  return (
    <div
      className={`project-artwork art-${index % 2} ${large ? "media-large" : ""}`}
      role="img"
      aria-label={`${title}. Project screenshot to be added.`}
    >
      <div className="artwork-grid" />
      {index % 2 === 0 ? (
        <div className="weather-art" aria-hidden="true">
          <span className="weather-sun" />
          <span className="weather-ring" />
          <span className="weather-line line-one" />
          <span className="weather-line line-two" />
          <span className="weather-line line-three" />
        </div>
      ) : (
        <div className="portfolio-art" aria-hidden="true">
          <span className="art-sheet sheet-back" />
          <span className="art-sheet sheet-front">
            <span>
              Gagandeep
              <br />
              <i>Kaur.</i>
            </span>
            <span className="sheet-line" />
            <small>THE EARLIER CHAPTER</small>
          </span>
        </div>
      )}
      <span className="artwork-index" aria-hidden="true">
        STUDY / 0{index + 1}
      </span>
      <span className="artwork-label">Project screenshot to be added</span>
    </div>
  );
}
