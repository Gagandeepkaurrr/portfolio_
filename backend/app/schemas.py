from datetime import datetime
import re
from typing import Annotated, Literal
from urllib.parse import urlsplit
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator, model_validator

Text100 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Text140 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=140)]
SectionKey = Literal['work', 'experience', 'community', 'about', 'contact']


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

    @field_validator('*', mode='after')
    @classmethod
    def reject_controls(cls, value):
        if isinstance(value, str) and re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', value):
            raise ValueError('Control characters are not permitted')
        return value


def safe_url(value: str | None):
    if value is None:
        return None
    if len(value) > 2048:
        raise ValueError('URL is too long')
    parts = urlsplit(value)
    if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password or any(c.isspace() for c in value):
        raise ValueError('Use a complete http or https URL without credentials')
    try:
        parts.port
    except ValueError:
        raise ValueError('Invalid URL port')
    return value


class ContentItem(StrictModel):
    id: UUID
    is_visible: bool = True
    position: int = Field(ge=0)


class MediaRef(StrictModel):
    asset_id: UUID
    alt: str = Field(min_length=1, max_length=180)
    caption: str | None = Field(default=None, max_length=500)


class PartialDate(StrictModel):
    value: str
    precision: Literal['year', 'month']

    @model_validator(mode='after')
    def valid_date(self):
        pattern = r'(19|20|21)\d{2}' if self.precision == 'year' else r'(19|20|21)\d{2}-(0[1-9]|1[0-2])'
        if not re.fullmatch(pattern, self.value):
            raise ValueError('Date must match the declared year or month precision')
        return self


class Metric(StrictModel):
    value: str = Field(min_length=1, max_length=40)
    label: str = Field(min_length=1, max_length=120)
    context: str = Field(min_length=1, max_length=300)


class NarrativeBlock(StrictModel):
    id: UUID
    kind: Literal['paragraph', 'bullet_list']
    heading: str | None = Field(default=None, max_length=160)
    text: str | None = Field(default=None, max_length=3000)
    items: list[Annotated[str, StringConstraints(max_length=500)]] = Field(default_factory=list, max_length=12)

    @model_validator(mode='after')
    def correct_payload(self):
        if self.kind == 'paragraph' and self.items:
            raise ValueError('Paragraph blocks use text')
        if self.kind == 'bullet_list' and self.text:
            raise ValueError('Bullet blocks use items')
        return self


class ProfileContent(StrictModel):
    full_name: Text100
    role_label: str = Field(min_length=1, max_length=120)
    hero_eyebrow: str = Field(default='', max_length=160)
    intro: str = Field(min_length=1, max_length=400)
    biography: str = Field(default='', max_length=2000)
    institution_context: str = Field(default='', max_length=180)
    email: EmailStr = Field(max_length=254)
    phone_display: str | None = Field(default=None, max_length=40)
    phone_e164: str | None = Field(default=None, pattern=r'^\+[1-9]\d{6,14}$')
    github_url: str | None = None
    linkedin_url: str | None = None
    portrait: MediaRef | None = None
    resume_asset_id: UUID | None = None
    _urls = field_validator('github_url', 'linkedin_url')(safe_url)


class ProjectFields(ContentItem):
    slug: str = Field(default='', max_length=80)
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(default='', max_length=80)
    summary: str = Field(default='', max_length=300)
    overview: str = Field(default='', max_length=3000)
    feature_bullets: list[Annotated[str, StringConstraints(max_length=300)]] = Field(default_factory=list, max_length=10)
    technologies: list[Annotated[str, StringConstraints(min_length=1, max_length=40)]] = Field(default_factory=list, max_length=20)
    narrative_blocks: list[NarrativeBlock] = Field(default_factory=list, max_length=12)
    live_url: str | None = None
    repository_url: str | None = None
    seo_title: str | None = Field(default=None, max_length=70)
    seo_description: str | None = Field(default=None, max_length=180)
    _urls = field_validator('live_url', 'repository_url')(safe_url)

    @field_validator('slug')
    @classmethod
    def slug_shape(cls, value):
        if value and not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
            raise ValueError('Use lowercase letters, digits and single hyphens')
        if value and len(value) < 3:
            raise ValueError('Slug must have at least three characters')
        return value

    @field_validator('narrative_blocks')
    @classmethod
    def unique_blocks(cls, value):
        if len({x.id for x in value}) != len(value):
            raise ValueError('Narrative block IDs must be unique')
        return value


class ProjectContent(ProjectFields):
    cover: MediaRef | None = None
    gallery: list[MediaRef] = Field(default_factory=list, max_length=12)


class DatedItem(ContentItem):
    start: PartialDate
    end: PartialDate | None = None
    is_current: bool = False

    @model_validator(mode='after')
    def check_range(self):
        if self.is_current and self.end is not None:
            raise ValueError('Current entries cannot have an end date')
        if not self.is_current and self.end is None:
            raise ValueError('Completed entries require an end date')
        if self.end and self.end.value < self.start.value[:len(self.end.value)]:
            raise ValueError('End cannot precede start')
        return self


class ExperienceContent(DatedItem):
    organization: Text140
    role: Text140
    description: str = Field(default='', max_length=2000)
    bullets: list[Annotated[str, StringConstraints(max_length=300)]] = Field(default_factory=list, max_length=10)
    technologies: list[Annotated[str, StringConstraints(max_length=40)]] = Field(default_factory=list, max_length=20)


class LeadershipContent(DatedItem):
    organization: Text140
    role: Text140
    description: str = Field(default='', max_length=2000)
    bullets: list[Annotated[str, StringConstraints(max_length=300)]] = Field(default_factory=list, max_length=10)
    metrics: list[Metric] = Field(default_factory=list, max_length=4)


class EducationContent(ContentItem):
    qualification: Text140
    institution: str = Field(min_length=1, max_length=200)
    start_year: int | None = Field(default=None, ge=1900, le=2199)
    completion_year: int | None = Field(default=None, ge=1900, le=2199)
    is_current: bool = False
    result_label: str = Field(default='', max_length=50)
    result_value: str = Field(default='', max_length=50)
    result_note: str | None = Field(default=None, max_length=180)

    @model_validator(mode='after')
    def years(self):
        if self.is_current and self.completion_year:
            raise ValueError('Current education has no completion year')
        if self.start_year and self.completion_year and self.completion_year < self.start_year:
            raise ValueError('Completion cannot precede start year')
        return self


class SkillGroupContent(ContentItem):
    group_name: Text100
    items: list[Annotated[str, StringConstraints(min_length=1, max_length=80)]] = Field(min_length=1, max_length=30)

    @field_validator('items')
    @classmethod
    def unique_items(cls, values):
        if len(set(values)) != len(values):
            raise ValueError('Skill names must be unique')
        return values


class RecognitionContent(ContentItem):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default='', max_length=1000)
    event_name: str = Field(default='', max_length=180)
    event_year: int | None = Field(default=None, ge=1900, le=2199)
    result_label: str | None = Field(default=None, max_length=100)
    metric: Metric | None = None
    link: str | None = None
    _urls = field_validator('link')(safe_url)


class CertificationContent(ContentItem):
    title: str = Field(min_length=1, max_length=180)
    issuers: list[Annotated[str, StringConstraints(min_length=1, max_length=180)]] = Field(min_length=1, max_length=4)
    issued_on: PartialDate | None = None
    credential_id: str | None = Field(default=None, max_length=180)
    credential_url: str | None = None
    _urls = field_validator('credential_url')(safe_url)


class SectionIntro(StrictModel):
    heading: str = Field(max_length=180)
    description: str = Field(default='', max_length=1000)


class SiteSettings(StrictModel):
    site_url: str
    default_seo_title: str = Field(min_length=1, max_length=70)
    default_seo_description: str = Field(min_length=1, max_length=180)
    section_labels: dict[SectionKey, Annotated[str, StringConstraints(min_length=1, max_length=30)]]
    section_intros: dict[SectionKey, SectionIntro]
    visible_sections: list[SectionKey] = Field(max_length=5)
    featured_project_ids: list[UUID] = Field(default_factory=list, max_length=30)
    featured_recognition_id: UUID | None = None
    show_phone: bool = False
    show_resume: bool = True
    availability_enabled: bool = False
    availability_text: str | None = Field(default=None, max_length=160)
    _urls = field_validator('site_url')(safe_url)

    @model_validator(mode='after')
    def sections(self):
        keys = {'work', 'experience', 'community', 'about', 'contact'}
        if set(self.section_labels) != keys or set(self.section_intros) != keys:
            raise ValueError('Provide labels and introductions for all five fixed sections')
        if len(set(self.visible_sections)) != len(self.visible_sections):
            raise ValueError('Visible sections must be unique')
        if len(set(self.featured_project_ids)) != len(self.featured_project_ids):
            raise ValueError('Featured projects must be unique')
        return self


class SiteContent(StrictModel):
    schema_version: Literal[1] = 1
    profile: ProfileContent
    projects: list[ProjectContent] = Field(max_length=30)
    experience: list[ExperienceContent] = Field(max_length=50)
    leadership: list[LeadershipContent] = Field(max_length=50)
    education: list[EducationContent] = Field(max_length=50)
    skill_groups: list[SkillGroupContent] = Field(max_length=50)
    recognition: list[RecognitionContent] = Field(max_length=50)
    certifications: list[CertificationContent] = Field(max_length=50)
    settings: SiteSettings

    @model_validator(mode='after')
    def unique_and_ordered(self):
        for name in ('projects', 'experience', 'leadership', 'education', 'skill_groups', 'recognition', 'certifications'):
            items = getattr(self, name)
            if len({x.id for x in items}) != len(items):
                raise ValueError(f'{name}: item IDs must be unique')
            items.sort(key=lambda x: x.position)
            for i, item in enumerate(items):
                item.position = i
        project_ids = {x.id for x in self.projects}
        if not set(self.settings.featured_project_ids).issubset(project_ids):
            raise ValueError('Featured projects must exist in the draft')
        if self.settings.featured_recognition_id and self.settings.featured_recognition_id not in {x.id for x in self.recognition}:
            raise ValueError('Featured recognition must exist in the draft')
        return self


class MediaVariant(StrictModel):
    url: str
    width: int | None = None
    height: int | None = None
    mime: str
    byte_size: int


class PublicMediaRef(MediaRef):
    url: str
    variants: dict[str, MediaVariant]
    width: int | None = None
    height: int | None = None


class PublicProfile(StrictModel):
    full_name: str
    role_label: str
    hero_eyebrow: str
    intro: str
    biography: str
    institution_context: str
    email: str
    github_url: str | None
    linkedin_url: str | None
    portrait: PublicMediaRef | None
    phone_display: str | None = Field(default=None, exclude_if=lambda x: x is None)
    phone_e164: str | None = Field(default=None, exclude_if=lambda x: x is None)
    resume_available: bool
    resume_url: str | None = None


class PublicProject(ProjectFields):
    cover: PublicMediaRef | None = None
    gallery: list[PublicMediaRef] = Field(default_factory=list, max_length=12)


class PublicSiteContent(StrictModel):
    schema_version: Literal[1]
    profile: PublicProfile
    projects: list[PublicProject]
    experience: list[ExperienceContent]
    leadership: list[LeadershipContent]
    education: list[EducationContent]
    skill_groups: list[SkillGroupContent]
    recognition: list[RecognitionContent]
    certifications: list[CertificationContent]
    settings: SiteSettings
    contact_retention_days: int


class LoginRequest(StrictModel):
    email: EmailStr = Field(max_length=254)
    password: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=1, max_length=256)


class PasswordChange(StrictModel):
    current_password: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=1, max_length=256)
    new_password: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=12, max_length=256)


class PublishRequest(StrictModel):
    expected_draft_revision: int = Field(ge=1)
    expected_live_release_id: UUID | None
    idempotency_key: UUID


class ContactRequest(StrictModel):
    name: Text100
    email: EmailStr = Field(max_length=254)
    subject: str = Field(default='', max_length=150)
    message: str = Field(min_length=10, max_length=5000)
    website: str = Field(default='', max_length=200)


class ContactStatus(StrictModel):
    is_read: bool | None = None
    is_archived: bool | None = None


class CropRequest(StrictModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    @model_validator(mode='after')
    def bounds(self):
        if self.x + self.width > 1.0000001 or self.y + self.height > 1.0000001:
            raise ValueError('Crop extends beyond the image')
        return self

# Explicit transport DTOs are separate from SQLAlchemy records and private snapshots.


class ReleaseSummary(StrictModel):
    id: UUID
    revision: int
    published_at: datetime


class SiteEnvelope(StrictModel):
    release: ReleaseSummary
    content: PublicSiteContent


class ProjectEnvelope(StrictModel):
    release: ReleaseSummary
    requested_slug: str
    canonical_slug: str
    project: PublicProject


class DraftEnvelope(StrictModel):
    revision: int
    content: SiteContent
    live_release: ReleaseSummary | None
    updated_at: datetime


class ValidationWarning(StrictModel):
    path: str
    message: str


class PreviewEnvelope(StrictModel):
    draft_revision: int
    content: PublicSiteContent
    validation_warnings: list[ValidationWarning]


class ProjectPreviewEnvelope(StrictModel):
    draft_revision: int
    project: PublicProject
    is_hidden: bool
    validation_warnings: list[ValidationWarning]


class PublishEnvelope(StrictModel):
    release: ReleaseSummary
    source_draft_revision: int


class ReleaseListItem(ReleaseSummary):
    source_draft_revision: int
    content_hash: str


class ReleasePage(StrictModel):
    items: list[ReleaseListItem]
    next_cursor: str | None
    has_more: bool


class ReleaseDetail(ReleaseSummary):
    source_draft_revision: int
    source_content: SiteContent
    content: SiteContent


class OwnerInfo(StrictModel):
    id: UUID
    email: str


class SessionEnvelope(StrictModel):
    owner: OwnerInfo
    csrf_token: str
    expires_at: datetime


class ContactReceipt(StrictModel):
    receipt_id: UUID
    status: Literal['received']


class ContactListItem(StrictModel):
    id: UUID
    name: str
    email: str
    subject: str
    excerpt: str
    created_at: datetime
    is_read: bool
    is_archived: bool
    notification_status: Literal['not_configured', 'pending', 'processing', 'sent', 'failed']


class ContactDetail(ContactListItem):
    message: str


class ContactPage(StrictModel):
    items: list[ContactListItem]
    unread_count: int
    next_cursor: str | None
    has_more: bool


class MediaUsage(StrictModel):
    type: Literal['draft', 'release', 'derived_asset']
    id: UUID | None = None
    revision: int | None = None


class MediaMetadata(StrictModel):
    id: UUID
    kind: Literal['image', 'pdf']
    status: str
    verified_mime: str
    original_display_name: str
    created_at: datetime
    source_width: int | None
    source_height: int | None
    page_count: int | None
    byte_size: int
    parent_asset_id: UUID | None
    crop: CropRequest | None
    variants: dict[str, MediaVariant]
    url: str | None
    usage: list[MediaUsage]
    quality_warning: str | None


class MediaPage(StrictModel):
    items: list[MediaMetadata]
    next_cursor: str | None
    has_more: bool
