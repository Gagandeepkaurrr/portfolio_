// Compile-time checks keep the editor/public models assignable to the authoritative API.
import type {components} from './api';
import type {SiteContent,PublicSiteContent,ProjectContent,PublicProject,ProfileContent,MediaRef} from '../types';
type Assert<T extends true> = T;
export type DraftMatchesApi = Assert<SiteContent extends components['schemas']['SiteContent'] ? true:false>;
export type PublicMatchesApi = Assert<PublicSiteContent extends components['schemas']['PublicSiteContent'] ? true:false>;
export type ProjectMatchesApi = Assert<ProjectContent extends components['schemas']['ProjectContent'] ? true:false>;
export type PublicProjectMatchesApi = Assert<PublicProject extends components['schemas']['PublicProject'] ? true:false>;
export type ProfileMatchesApi = Assert<ProfileContent extends components['schemas']['ProfileContent'] ? true:false>;
export type MediaMatchesApi = Assert<MediaRef extends components['schemas']['MediaRef'] ? true:false>;
