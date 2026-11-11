export type SectionKey =
  "work" | "experience" | "community" | "about" | "contact";
export type ContentItem = { id: string; is_visible: boolean; position: number };
export type PartialDate = { value: string; precision: "year" | "month" };
export type MediaRef = {
  asset_id: string;
  alt: string;
  caption?: string | null;
};
export type MediaVariant = {
  url: string;
  width?: number | null;
  height?: number | null;
  mime: string;
  byte_size: number;
};
export type PublicMediaRef = MediaRef & {
  url: string;
  variants: Record<string, MediaVariant>;
  width?: number | null;
  height?: number | null;
};
export type Metric = { value: string; label: string; context: string };
export type NarrativeBlock = {
  id: string;
  kind: "paragraph" | "bullet_list";
  heading?: string | null;
  text?: string | null;
  items?: string[];
};
export interface ProfileContent {
  full_name: string;
  role_label: string;
  hero_eyebrow: string;
  intro: string;
  biography: string;
  institution_context: string;
  email: string;
  phone_display: string | null;
  phone_e164: string | null;
  github_url: string | null;
  linkedin_url: string | null;
  portrait: MediaRef | null;
  resume_asset_id: string | null;
}
export interface ProjectContent extends ContentItem {
  slug: string;
  title: string;
  category: string;
  summary: string;
  overview: string;
  feature_bullets: string[];
  technologies: string[];
  narrative_blocks: NarrativeBlock[];
  live_url: string | null;
  repository_url: string | null;
  cover: MediaRef | null;
  gallery: MediaRef[];
  seo_title: string | null;
  seo_description: string | null;
}
export interface ExperienceContent extends ContentItem {
  organization: string;
  role: string;
  start: PartialDate;
  end: PartialDate | null;
  is_current: boolean;
  description: string;
  bullets: string[];
  technologies: string[];
}
export interface LeadershipContent extends Omit<
  ExperienceContent,
  "technologies"
> {
  metrics: Metric[];
}
export interface EducationContent extends ContentItem {
  qualification: string;
  institution: string;
  start_year: number | null;
  completion_year: number | null;
  is_current: boolean;
  result_label: string;
  result_value: string;
  result_note: string | null;
}
export interface SkillGroupContent extends ContentItem {
  group_name: string;
  items: string[];
}
export interface RecognitionContent extends ContentItem {
  title: string;
  description: string;
  event_name: string;
  event_year: number | null;
  result_label: string | null;
  metric: Metric | null;
  link: string | null;
}
export interface CertificationContent extends ContentItem {
  title: string;
  issuers: string[];
  issued_on: PartialDate | null;
  credential_id: string | null;
  credential_url: string | null;
}
export interface SiteSettings {
  site_url: string;
  default_seo_title: string;
  default_seo_description: string;
  section_labels: Record<SectionKey, string>;
  section_intros: Record<SectionKey, { heading: string; description: string }>;
  visible_sections: SectionKey[];
  featured_project_ids: string[];
  featured_recognition_id: string | null;
  show_phone: boolean;
  show_resume: boolean;
  availability_enabled: boolean;
  availability_text: string | null;
}
export interface SiteContent {
  schema_version: 1;
  profile: ProfileContent;
  projects: ProjectContent[];
  experience: ExperienceContent[];
  leadership: LeadershipContent[];
  education: EducationContent[];
  skill_groups: SkillGroupContent[];
  recognition: RecognitionContent[];
  certifications: CertificationContent[];
  settings: SiteSettings;
}
export type PublicProfile = Omit<
  ProfileContent,
  "phone_display" | "phone_e164" | "resume_asset_id" | "portrait"
> & {
  phone_display?: string | null;
  phone_e164?: string | null;
  portrait: PublicMediaRef | null;
  resume_available: boolean;
  resume_url?: string | null;
};
export type PublicProject = Omit<ProjectContent, "cover" | "gallery"> & {
  cover: PublicMediaRef | null;
  gallery: PublicMediaRef[];
};
export type PublicSiteContent = Omit<SiteContent, "profile" | "projects"> & {
  profile: PublicProfile;
  projects: PublicProject[];
  contact_retention_days: number;
};
export type Release = {
  id: string;
  revision: number;
  published_at?: string;
  created_at?: string;
};
export type SiteEnvelope = { release: Release; content: PublicSiteContent };
export type DraftEnvelope = {
  revision: number;
  content: SiteContent;
  live_release: Release | null;
};
export type ApiErrorBody = {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    field_errors?: { path: string; message: string }[];
  };
  request_id: string;
};
export type Paginated<T> = {
  items: T[];
  next_cursor: string | null;
  has_more: boolean;
};
