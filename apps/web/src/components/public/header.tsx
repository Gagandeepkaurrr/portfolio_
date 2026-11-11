"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import type { PublicSiteContent, SectionKey } from "@/lib/types";
const sections: SectionKey[] = [
  "work",
  "experience",
  "community",
  "about",
  "contact",
];
export function SiteHeader({ content }: { content: PublicSiteContent }) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState("");
  const toggle = useRef<HTMLButtonElement>(null);
  const menu = useRef<HTMLElement>(null);
  useEffect(() => {
    if (open) menu.current?.querySelector<HTMLAnchorElement>("a")?.focus();
  }, [open]);
  useEffect(() => {
    const close = (e: KeyboardEvent) => {
      if (e.key === "Escape" && open) {
        setOpen(false);
        toggle.current?.focus();
      }
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [open]);
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries)
          if (entry.isIntersecting) setActive(entry.target.id);
      },
      { rootMargin: "-15% 0px -65% 0px" },
    );
    sections.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);
  return (
    <header className="site-header">
      <div className="header-inner">
        <Link
          href="/"
          className="brand"
          aria-label={`${content.profile.full_name} — home`}
        >
          <span className="brand-mark" aria-hidden="true">
            GK<span>·</span>
          </span>
          <span className="brand-name">{content.profile.full_name}</span>
        </Link>
        <span className="header-note">A PERSONAL JOURNAL OF BUILDING</span>
        <button
          ref={toggle}
          className="menu-toggle"
          aria-expanded={open}
          aria-controls="site-navigation"
          onClick={() => setOpen(!open)}
        >
          {open ? "Close" : "Menu"}
          <span aria-hidden="true">{open ? "−" : "+"}</span>
        </button>
        <nav
          ref={menu}
          id="site-navigation"
          className={`site-nav ${open ? "is-open" : ""}`}
          aria-label="Main navigation"
        >
          {sections
            .filter((s) => content.settings.visible_sections.includes(s))
            .map((s, i) => (
              <Link
                href={`/#${s}`}
                key={s}
                aria-current={active === s ? "location" : undefined}
                onClick={() => setOpen(false)}
              >
                <span className="nav-number">0{i + 1}</span>
                {content.settings.section_labels[s]}
              </Link>
            ))}
        </nav>
      </div>
    </header>
  );
}
