import { useLocation } from 'react-router';
import { AdminShell } from './AdminShell';
import { AboutEditor, CommunityEditor, ExperienceEditor, ProfileEditor, ProjectEditor, ProjectsEditor, SettingsEditor } from './ContentEditors';
import { History } from './History';
import { Inbox, InboxDetail } from './Inbox';
import { MediaBrowser } from './MediaManager';
import { Overview } from './Overview';
import { Preview, PreviewFrame } from './Preview';
import { Link } from 'react-router';
export function AdminRouter() {
  const pathname = useLocation().pathname; const route = pathname.replace(/^\/admin\/?/, '').split('/').filter(Boolean); let content;
  if (route[0] === 'preview' && route[1] === 'frame') return <PreviewFrame projectId={route[2] === 'projects' ? route[3] : undefined} />;
  if (!route.length) content = <Overview />;
  else if (route[0] === 'content') {
    if (route[1] === 'profile') content = <ProfileEditor />;
    else if (route[1] === 'projects') content = route[2] ? <ProjectEditor id={route[2]} /> : <ProjectsEditor />;
    else if (route[1] === 'experience') content = <ExperienceEditor />;
    else if (route[1] === 'community') content = <CommunityEditor />;
    else if (route[1] === 'about') content = <AboutEditor />;
    else if (route[1] === 'settings') content = <SettingsEditor />;
  } else if (route[0] === 'media') content = <><h1>Your media library</h1><MediaBrowser /></>;
  else if (route[0] === 'inbox') content = route[1] ? <InboxDetail id={route[1]} /> : <Inbox />;
  else if (route[0] === 'history') content = <History />;
  else if (route[0] === 'preview') content = <Preview projectId={route[1] === 'projects' ? route[2] : undefined} />;
  return <AdminShell preview={route[0] === 'preview'}>{content ?? <div className="admin-empty"><h1>This studio page doesn’t exist.</h1><Link to="/admin">Return to overview</Link></div>}</AdminShell>;
}
