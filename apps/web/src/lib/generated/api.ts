// Generated from FastAPI OpenAPI. Run pnpm contracts; do not edit.
export interface paths {
    "/api/v1/admin/auth/change-password": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Change Password */
        post: operations["change_password_api_v1_admin_auth_change_password_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Login */
        post: operations["login_api_v1_admin_auth_login_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/auth/logout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Logout */
        post: operations["logout_api_v1_admin_auth_logout_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/auth/session": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Session Info */
        get: operations["session_info_api_v1_admin_auth_session_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/contact": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Inbox */
        get: operations["inbox_api_v1_admin_contact_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/contact/{contact_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Detail */
        get: operations["detail_api_v1_admin_contact__contact_id__get"];
        put?: never;
        post?: never;
        /** Delete */
        delete: operations["delete_api_v1_admin_contact__contact_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/contact/{contact_id}/status": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Status */
        patch: operations["update_status_api_v1_admin_contact__contact_id__status_patch"];
        trace?: never;
    };
    "/api/v1/admin/draft": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Draft */
        get: operations["draft_api_v1_admin_draft_get"];
        /** Save */
        put: operations["save_api_v1_admin_draft_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/media": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Media List */
        get: operations["media_list_api_v1_admin_media_get"];
        put?: never;
        /** Upload */
        post: operations["upload_api_v1_admin_media_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/media/{asset_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /** Delete */
        delete: operations["delete_api_v1_admin_media__asset_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/media/{asset_id}/crop": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Crop */
        post: operations["crop_api_v1_admin_media__asset_id__crop_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/media/{asset_id}/{variant}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Private Media */
        get: operations["private_media_api_v1_admin_media__asset_id___variant__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/preview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Preview */
        get: operations["preview_api_v1_admin_preview_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/preview/projects/{project_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Preview Project */
        get: operations["preview_project_api_v1_admin_preview_projects__project_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/publish": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Publish */
        post: operations["publish_api_v1_admin_publish_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/releases": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Releases */
        get: operations["releases_api_v1_admin_releases_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/releases/{release_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Release Detail */
        get: operations["release_detail_api_v1_admin_releases__release_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/admin/releases/{release_id}/restore": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Restore */
        post: operations["restore_api_v1_admin_releases__release_id__restore_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/contact": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Send Message */
        post: operations["send_message_api_v1_contact_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/health/live": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Live */
        get: operations["live_api_v1_health_live_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/health/ready": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Ready */
        get: operations["ready_api_v1_health_ready_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/media/{asset_id}/{variant}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Public Media */
        get: operations["public_media_api_v1_media__asset_id___variant__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/projects/{slug}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Project */
        get: operations["project_api_v1_projects__slug__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/resume": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Resume */
        get: operations["resume_api_v1_resume_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/site": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Public Site */
        get: operations["public_site_api_v1_site_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** Body_upload_api_v1_admin_media_post */
        Body_upload_api_v1_admin_media_post: {
            /** File */
            file: string;
        };
        /** CertificationContent */
        CertificationContent: {
            /** Credential Id */
            credential_id?: string | null;
            /** Credential Url */
            credential_url?: string | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Is Visible
             * @default true
             */
            is_visible: boolean;
            issued_on?: components["schemas"]["PartialDate"] | null;
            /** Issuers */
            issuers: string[];
            /** Position */
            position: number;
            /** Title */
            title: string;
        };
        /** ContactDetail */
        ContactDetail: {
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Email */
            email: string;
            /** Excerpt */
            excerpt: string;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Is Archived */
            is_archived: boolean;
            /** Is Read */
            is_read: boolean;
            /** Message */
            message: string;
            /** Name */
            name: string;
            /**
             * Notification Status
             * @enum {string}
             */
            notification_status: "not_configured" | "pending" | "processing" | "sent" | "failed";
            /** Subject */
            subject: string;
        };
        /** ContactListItem */
        ContactListItem: {
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /** Email */
            email: string;
            /** Excerpt */
            excerpt: string;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Is Archived */
            is_archived: boolean;
            /** Is Read */
            is_read: boolean;
            /** Name */
            name: string;
            /**
             * Notification Status
             * @enum {string}
             */
            notification_status: "not_configured" | "pending" | "processing" | "sent" | "failed";
            /** Subject */
            subject: string;
        };
        /** ContactPage */
        ContactPage: {
            /** Has More */
            has_more: boolean;
            /** Items */
            items: components["schemas"]["ContactListItem"][];
            /** Next Cursor */
            next_cursor: string | null;
            /** Unread Count */
            unread_count: number;
        };
        /** ContactReceipt */
        ContactReceipt: {
            /**
             * Receipt Id
             * Format: uuid
             */
            receipt_id: string;
            /**
             * Status
             * @constant
             */
            status: "received";
        };
        /** ContactRequest */
        ContactRequest: {
            /**
             * Email
             * Format: email
             */
            email: string;
            /** Message */
            message: string;
            /** Name */
            name: string;
            /**
             * Subject
             * @default
             */
            subject: string;
            /**
             * Website
             * @default
             */
            website: string;
        };
        /** ContactStatus */
        ContactStatus: {
            /** Is Archived */
            is_archived?: boolean | null;
            /** Is Read */
            is_read?: boolean | null;
        };
        /** CropRequest */
        CropRequest: {
            /** Height */
            height: number;
            /** Width */
            width: number;
            /** X */
            x: number;
            /** Y */
            y: number;
        };
        /** DraftEnvelope */
        DraftEnvelope: {
            content: components["schemas"]["SiteContent"];
            live_release: components["schemas"]["ReleaseSummary"] | null;
            /** Revision */
            revision: number;
            /**
             * Updated At
             * Format: date-time
             */
            updated_at: string;
        };
        /** EducationContent */
        EducationContent: {
            /** Completion Year */
            completion_year?: number | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Institution */
            institution: string;
            /**
             * Is Current
             * @default false
             */
            is_current: boolean;
            /**
             * Is Visible
             * @default true
             */
            is_visible: boolean;
            /** Position */
            position: number;
            /** Qualification */
            qualification: string;
            /**
             * Result Label
             * @default
             */
            result_label: string;
            /** Result Note */
            result_note?: string | null;
            /**
             * Result Value
             * @default
             */
            result_value: string;
            /** Start Year */
            start_year?: number | null;
        };
        /** ExperienceContent */
        ExperienceContent: {
            /** Bullets */
            bullets?: string[];
            /**
             * Description
             * @default
             */
            description: string;
            end?: components["schemas"]["PartialDate"] | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Is Current
             * @default false
             */
            is_current: boolean;
            /**
             * Is Visible
             * @default true
             */
            is_visible: boolean;
            /** Organization */
            organization: string;
            /** Position */
            position: number;
            /** Role */
            role: string;
            start: components["schemas"]["PartialDate"];
            /** Technologies */
            technologies?: string[];
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** LeadershipContent */
        LeadershipContent: {
            /** Bullets */
            bullets?: string[];
            /**
             * Description
             * @default
             */
            description: string;
            end?: components["schemas"]["PartialDate"] | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Is Current
             * @default false
             */
            is_current: boolean;
            /**
             * Is Visible
             * @default true
             */
            is_visible: boolean;
            /** Metrics */
            metrics?: components["schemas"]["Metric"][];
            /** Organization */
            organization: string;
            /** Position */
            position: number;
            /** Role */
            role: string;
            start: components["schemas"]["PartialDate"];
        };
        /** LoginRequest */
        LoginRequest: {
            /**
             * Email
             * Format: email
             */
            email: string;
            /** Password */
            password: string;
        };
        /** MediaMetadata */
        MediaMetadata: {
            /** Byte Size */
            byte_size: number;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            crop: components["schemas"]["CropRequest"] | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "image" | "pdf";
            /** Original Display Name */
            original_display_name: string;
            /** Page Count */
            page_count: number | null;
            /** Parent Asset Id */
            parent_asset_id: string | null;
            /** Quality Warning */
            quality_warning: string | null;
            /** Source Height */
            source_height: number | null;
            /** Source Width */
            source_width: number | null;
            /** Status */
            status: string;
            /** Url */
            url: string | null;
            /** Usage */
            usage: components["schemas"]["MediaUsage"][];
            /** Variants */
            variants: {
                [key: string]: components["schemas"]["MediaVariant"];
            };
            /** Verified Mime */
            verified_mime: string;
        };
        /** MediaPage */
        MediaPage: {
            /** Has More */
            has_more: boolean;
            /** Items */
            items: components["schemas"]["MediaMetadata"][];
            /** Next Cursor */
            next_cursor: string | null;
        };
        /** MediaRef */
        MediaRef: {
            /** Alt */
            alt: string;
            /**
             * Asset Id
             * Format: uuid
             */
            asset_id: string;
            /** Caption */
            caption?: string | null;
        };
        /** MediaUsage */
        MediaUsage: {
            /** Id */
            id?: string | null;
            /** Revision */
            revision?: number | null;
            /**
             * Type
             * @enum {string}
             */
            type: "draft" | "release" | "derived_asset";
        };
        /** MediaVariant */
        MediaVariant: {
            /** Byte Size */
            byte_size: number;
            /** Height */
            height?: number | null;
            /** Mime */
            mime: string;
            /** Url */
            url: string;
            /** Width */
            width?: number | null;
        };
        /** Metric */
        Metric: {
            /** Context */
            context: string;
            /** Label */
            label: string;
            /** Value */
            value: string;
        };
        /** NarrativeBlock */
        NarrativeBlock: {
            /** Heading */
            heading?: string | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Items */
            items?: string[];
            /**
             * Kind
             * @enum {string}
             */
            kind: "paragraph" | "bullet_list";
            /** Text */
            text?: string | null;
        };
        /** OwnerInfo */
        OwnerInfo: {
            /** Email */
            email: string;
            /**
             * Id
             * Format: uuid
             */
            id: string;
        };
        /** PartialDate */
        PartialDate: {
            /**
             * Precision
             * @enum {string}
             */
            precision: "year" | "month";
            /** Value */
            value: string;
        };
        /** PasswordChange */
        PasswordChange: {
            /** Current Password */
            current_password: string;
            /** New Password */
            new_password: string;
        };
        /** PreviewEnvelope */
        PreviewEnvelope: {
            content: components["schemas"]["PublicSiteContent"];
            /** Draft Revision */
            draft_revision: number;
            /** Validation Warnings */
            validation_warnings: components["schemas"]["ValidationWarning"][];
        };
        /** ProfileContent */
        ProfileContent: {
            /**
             * Biography
             * @default
             */
            biography: string;
            /**
             * Email
             * Format: email
             */
            email: string;
            /** Full Name */
            full_name: string;
            /** Github Url */
            github_url?: string | null;
            /**
             * Hero Eyebrow
             * @default
             */
            hero_eyebrow: string;
            /**
             * Institution Context
             * @default
             */
            institution_context: string;
            /** Intro */
            intro: string;
            /** Linkedin Url */
            linkedin_url?: string | null;
            /** Phone Display */
            phone_display?: string | null;
            /** Phone E164 */
            phone_e164?: string | null;
            portrait?: components["schemas"]["MediaRef"] | null;
            /** Resume Asset Id */
            resume_asset_id?: string | null;
            /** Role Label */
            role_label: string;
        };
        /** ProjectContent */
        ProjectContent: {
            /**
             * Category
             * @default
             */
            category: string;
            cover?: components["schemas"]["MediaRef"] | null;
            /** Feature Bullets */
            feature_bullets?: string[];
            /** Gallery */
            gallery?: components["schemas"]["MediaRef"][];
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Is Visible
             * @default true
             */
            is_visible: boolean;
            /** Live Url */
            live_url?: string | null;
            /** Narrative Blocks */
            narrative_blocks?: components["schemas"]["NarrativeBlock"][];
            /**
             * Overview
             * @default
             */
            overview: string;
            /** Position */
            position: number;
            /** Repository Url */
            repository_url?: string | null;
            /** Seo Description */
            seo_description?: string | null;
            /** Seo Title */
            seo_title?: string | null;
            /**
             * Slug
             * @default
             */
            slug: string;
            /**
             * Summary
             * @default
             */
            summary: string;
            /** Technologies */
            technologies?: string[];
            /** Title */
            title: string;
        };
        /** ProjectEnvelope */
        ProjectEnvelope: {
            /** Canonical Slug */
            canonical_slug: string;
            project: components["schemas"]["PublicProject"];
            release: components["schemas"]["ReleaseSummary"];
            /** Requested Slug */
            requested_slug: string;
        };
        /** ProjectPreviewEnvelope */
        ProjectPreviewEnvelope: {
            /** Draft Revision */
            draft_revision: number;
            /** Is Hidden */
            is_hidden: boolean;
            project: components["schemas"]["PublicProject"];
            /** Validation Warnings */
            validation_warnings: components["schemas"]["ValidationWarning"][];
        };
        /** PublicMediaRef */
        PublicMediaRef: {
            /** Alt */
            alt: string;
            /**
             * Asset Id
             * Format: uuid
             */
            asset_id: string;
            /** Caption */
            caption?: string | null;
            /** Height */
            height?: number | null;
            /** Url */
            url: string;
            /** Variants */
            variants: {
                [key: string]: components["schemas"]["MediaVariant"];
            };
            /** Width */
            width?: number | null;
        };
        /** PublicProfile */
        PublicProfile: {
            /** Biography */
            biography: string;
            /** Email */
            email: string;
            /** Full Name */
            full_name: string;
            /** Github Url */
            github_url: string | null;
            /** Hero Eyebrow */
            hero_eyebrow: string;
            /** Institution Context */
            institution_context: string;
            /** Intro */
            intro: string;
            /** Linkedin Url */
            linkedin_url: string | null;
            /** Phone Display */
            phone_display?: string | null;
            /** Phone E164 */
            phone_e164?: string | null;
            portrait: components["schemas"]["PublicMediaRef"] | null;
            /** Resume Available */
            resume_available: boolean;
            /** Resume Url */
            resume_url?: string | null;
            /** Role Label */
            role_label: string;
        };
        /** PublicProject */
        PublicProject: {
            /**
             * Category
             * @default
             */
            category: string;
            cover?: components["schemas"]["PublicMediaRef"] | null;
            /** Feature Bullets */
            feature_bullets?: string[];
            /** Gallery */
            gallery?: components["schemas"]["PublicMediaRef"][];
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Is Visible
             * @default true
             */
            is_visible: boolean;
            /** Live Url */
            live_url?: string | null;
            /** Narrative Blocks */
            narrative_blocks?: components["schemas"]["NarrativeBlock"][];
            /**
             * Overview
             * @default
             */
            overview: string;
            /** Position */
            position: number;
            /** Repository Url */
            repository_url?: string | null;
            /** Seo Description */
            seo_description?: string | null;
            /** Seo Title */
            seo_title?: string | null;
            /**
             * Slug
             * @default
             */
            slug: string;
            /**
             * Summary
             * @default
             */
            summary: string;
            /** Technologies */
            technologies?: string[];
            /** Title */
            title: string;
        };
        /** PublicSiteContent */
        PublicSiteContent: {
            /** Certifications */
            certifications: components["schemas"]["CertificationContent"][];
            /** Contact Retention Days */
            contact_retention_days: number;
            /** Education */
            education: components["schemas"]["EducationContent"][];
            /** Experience */
            experience: components["schemas"]["ExperienceContent"][];
            /** Leadership */
            leadership: components["schemas"]["LeadershipContent"][];
            profile: components["schemas"]["PublicProfile"];
            /** Projects */
            projects: components["schemas"]["PublicProject"][];
            /** Recognition */
            recognition: components["schemas"]["RecognitionContent"][];
            /**
             * Schema Version
             * @constant
             */
            schema_version: 1;
            settings: components["schemas"]["SiteSettings"];
            /** Skill Groups */
            skill_groups: components["schemas"]["SkillGroupContent"][];
        };
        /** PublishEnvelope */
        PublishEnvelope: {
            release: components["schemas"]["ReleaseSummary"];
            /** Source Draft Revision */
            source_draft_revision: number;
        };
        /** PublishRequest */
        PublishRequest: {
            /** Expected Draft Revision */
            expected_draft_revision: number;
            /** Expected Live Release Id */
            expected_live_release_id: string | null;
            /**
             * Idempotency Key
             * Format: uuid
             */
            idempotency_key: string;
        };
        /** RecognitionContent */
        RecognitionContent: {
            /**
             * Description
             * @default
             */
            description: string;
            /**
             * Event Name
             * @default
             */
            event_name: string;
            /** Event Year */
            event_year?: number | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Is Visible
             * @default true
             */
            is_visible: boolean;
            /** Link */
            link?: string | null;
            metric?: components["schemas"]["Metric"] | null;
            /** Position */
            position: number;
            /** Result Label */
            result_label?: string | null;
            /** Title */
            title: string;
        };
        /** ReleaseDetail */
        ReleaseDetail: {
            content: components["schemas"]["SiteContent"];
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Published At
             * Format: date-time
             */
            published_at: string;
            /** Revision */
            revision: number;
            source_content: components["schemas"]["SiteContent"];
            /** Source Draft Revision */
            source_draft_revision: number;
        };
        /** ReleaseListItem */
        ReleaseListItem: {
            /** Content Hash */
            content_hash: string;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Published At
             * Format: date-time
             */
            published_at: string;
            /** Revision */
            revision: number;
            /** Source Draft Revision */
            source_draft_revision: number;
        };
        /** ReleasePage */
        ReleasePage: {
            /** Has More */
            has_more: boolean;
            /** Items */
            items: components["schemas"]["ReleaseListItem"][];
            /** Next Cursor */
            next_cursor: string | null;
        };
        /** ReleaseSummary */
        ReleaseSummary: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Published At
             * Format: date-time
             */
            published_at: string;
            /** Revision */
            revision: number;
        };
        /** SectionIntro */
        SectionIntro: {
            /**
             * Description
             * @default
             */
            description: string;
            /** Heading */
            heading: string;
        };
        /** SessionEnvelope */
        SessionEnvelope: {
            /** Csrf Token */
            csrf_token: string;
            /**
             * Expires At
             * Format: date-time
             */
            expires_at: string;
            owner: components["schemas"]["OwnerInfo"];
        };
        /** SiteContent */
        SiteContent: {
            /** Certifications */
            certifications: components["schemas"]["CertificationContent"][];
            /** Education */
            education: components["schemas"]["EducationContent"][];
            /** Experience */
            experience: components["schemas"]["ExperienceContent"][];
            /** Leadership */
            leadership: components["schemas"]["LeadershipContent"][];
            profile: components["schemas"]["ProfileContent"];
            /** Projects */
            projects: components["schemas"]["ProjectContent"][];
            /** Recognition */
            recognition: components["schemas"]["RecognitionContent"][];
            /**
             * Schema Version
             * @default 1
             * @constant
             */
            schema_version: 1;
            settings: components["schemas"]["SiteSettings"];
            /** Skill Groups */
            skill_groups: components["schemas"]["SkillGroupContent"][];
        };
        /** SiteEnvelope */
        SiteEnvelope: {
            content: components["schemas"]["PublicSiteContent"];
            release: components["schemas"]["ReleaseSummary"];
        };
        /** SiteSettings */
        SiteSettings: {
            /**
             * Availability Enabled
             * @default false
             */
            availability_enabled: boolean;
            /** Availability Text */
            availability_text?: string | null;
            /** Default Seo Description */
            default_seo_description: string;
            /** Default Seo Title */
            default_seo_title: string;
            /** Featured Project Ids */
            featured_project_ids?: string[];
            /** Featured Recognition Id */
            featured_recognition_id?: string | null;
            /** Section Intros */
            section_intros: {
                [key: string]: components["schemas"]["SectionIntro"];
            };
            /** Section Labels */
            section_labels: {
                [key: string]: string;
            };
            /**
             * Show Phone
             * @default false
             */
            show_phone: boolean;
            /**
             * Show Resume
             * @default true
             */
            show_resume: boolean;
            /** Site Url */
            site_url: string;
            /** Visible Sections */
            visible_sections: ("work" | "experience" | "community" | "about" | "contact")[];
        };
        /** SkillGroupContent */
        SkillGroupContent: {
            /** Group Name */
            group_name: string;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Is Visible
             * @default true
             */
            is_visible: boolean;
            /** Items */
            items: string[];
            /** Position */
            position: number;
        };
        /** ValidationError */
        ValidationError: {
            /** Context */
            ctx?: Record<string, never>;
            /** Input */
            input?: unknown;
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
        };
        /** ValidationWarning */
        ValidationWarning: {
            /** Message */
            message: string;
            /** Path */
            path: string;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    change_password_api_v1_admin_auth_change_password_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PasswordChange"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SessionEnvelope"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    login_api_v1_admin_auth_login_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LoginRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SessionEnvelope"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    logout_api_v1_admin_auth_logout_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    session_info_api_v1_admin_auth_session_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SessionEnvelope"];
                };
            };
        };
    };
    inbox_api_v1_admin_contact_get: {
        parameters: {
            query?: {
                status?: string;
                cursor?: string | null;
                limit?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ContactPage"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    detail_api_v1_admin_contact__contact_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                contact_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ContactDetail"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_api_v1_admin_contact__contact_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                contact_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_status_api_v1_admin_contact__contact_id__status_patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                contact_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ContactStatus"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ContactDetail"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    draft_api_v1_admin_draft_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DraftEnvelope"];
                };
            };
        };
    };
    save_api_v1_admin_draft_put: {
        parameters: {
            query?: never;
            header?: {
                "if-match"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SiteContent"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DraftEnvelope"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    media_list_api_v1_admin_media_get: {
        parameters: {
            query?: {
                kind?: string | null;
                search?: string | null;
                cursor?: string | null;
                limit?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MediaPage"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    upload_api_v1_admin_media_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_upload_api_v1_admin_media_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MediaMetadata"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_api_v1_admin_media__asset_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                asset_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    crop_api_v1_admin_media__asset_id__crop_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                asset_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CropRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MediaMetadata"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    private_media_api_v1_admin_media__asset_id___variant__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                asset_id: string;
                variant: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    preview_api_v1_admin_preview_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PreviewEnvelope"];
                };
            };
        };
    };
    preview_project_api_v1_admin_preview_projects__project_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                project_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProjectPreviewEnvelope"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    publish_api_v1_admin_publish_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PublishRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PublishEnvelope"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    releases_api_v1_admin_releases_get: {
        parameters: {
            query?: {
                cursor?: string | null;
                limit?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReleasePage"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    release_detail_api_v1_admin_releases__release_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                release_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReleaseDetail"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    restore_api_v1_admin_releases__release_id__restore_post: {
        parameters: {
            query?: never;
            header?: {
                "if-match"?: string | null;
            };
            path: {
                release_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DraftEnvelope"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    send_message_api_v1_contact_post: {
        parameters: {
            query?: never;
            header: {
                "idempotency-key": string;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ContactRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ContactReceipt"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    live_api_v1_health_live_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    ready_api_v1_health_ready_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    public_media_api_v1_media__asset_id___variant__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                asset_id: string;
                variant: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    project_api_v1_projects__slug__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                slug: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProjectEnvelope"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    resume_api_v1_resume_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    public_site_api_v1_site_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SiteEnvelope"];
                };
            };
        };
    };
}
