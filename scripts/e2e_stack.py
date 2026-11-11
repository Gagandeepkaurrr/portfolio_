#!/usr/bin/env python3
"""Run browser tests against an isolated real database, API, web and ephemeral owner."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import re
import secrets
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from manage import ROOT, PNPM, environment


def validate_database_name(name: str) -> str:
    if not re.fullmatch(r'portfolio_e2e_[a-f0-9]{16}', name):
        raise ValueError('Only a generated portfolio_e2e_<16 hex characters> database can be created or dropped.')
    return name


def require_free_port(port: int):
    with socket.socket() as listener:
        try:
            listener.bind(('127.0.0.1', port))
        except OSError:
            raise RuntimeError(f'Port {port} is already in use; stop that test stack or choose another E2E port.') from None


def wait_ready(url: str, processes: list[subprocess.Popen], timeout: float = 120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if any(process.poll() is not None for process in processes):
            raise RuntimeError('An E2E service exited before becoming ready; inspect .data/e2e-logs.')
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if 200 <= response.status < 300:
                    return
        except (OSError, urllib.error.HTTPError):
            pass
        time.sleep(0.4)
    raise RuntimeError(f'Timed out waiting for E2E service {url}; inspect .data/e2e-logs.')


def main():
    from sqlalchemy import create_engine
    from sqlalchemy.engine import make_url
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('playwright_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    env = environment()
    api_port = int(env.get('E2E_API_PORT', '8002'))
    web_port = int(env.get('E2E_WEB_PORT', '3002'))
    require_free_port(api_port)
    require_free_port(web_port)
    name = validate_database_name('portfolio_e2e_' + uuid.uuid4().hex[:16])
    base_url = make_url(env['DATABASE_URL'])
    operator = create_engine(base_url, isolation_level='AUTOCOMMIT')
    created = False
    processes = []
    logs = []
    log_dir = ROOT / '.data/e2e-logs' / name
    log_dir.mkdir(parents=True, mode=0o700)
    def stop_requested(*_):
        raise KeyboardInterrupt
    previous_term = signal.signal(signal.SIGTERM, stop_requested)
    with tempfile.TemporaryDirectory(prefix='portfolio-e2e-media-') as media:
        try:
            with operator.connect() as connection:
                connection.exec_driver_sql(f'CREATE DATABASE "{name}"')
                created = True
            env.update({
                'APP_ENV':'test',
                'DATABASE_URL':base_url.set(database=name).render_as_string(hide_password=False),
                'MEDIA_ROOT':media,
                'CSRF_SECRET':secrets.token_hex(32),
                'ABUSE_HMAC_SECRET':secrets.token_hex(32),
                'PUBLIC_ORIGIN':f'http://localhost:{web_port}',
                'API_INTERNAL_URL':f'http://127.0.0.1:{api_port}/api/v1',
                'NEXT_BUILD_DIR':'.next-e2e',
                'E2E_ORIGIN':f'http://localhost:{web_port}',
                'E2E_OWNER_EMAIL':'e2e-owner@example.com',
                'E2E_OWNER_PASSWORD':secrets.token_urlsafe(32),
                'SMTP_HOST':'',
                'CONTACT_NOTIFY_TO':'',
                'NEXT_TELEMETRY_DISABLED':'1',
            })
            def api(*parts):
                subprocess.run(['uv','run','--frozen',*parts],cwd=ROOT/'apps/api',env=env,check=True)
            api('alembic','upgrade','head')
            api('python','-m','app.cli','seed')
            api('python','-c',"import os; from app.cli import create_owner; from app.db import session_factory; db=session_factory()(); create_owner(db,os.environ['E2E_OWNER_EMAIL'],os.environ['E2E_OWNER_PASSWORD']); db.close()")
            commands = [
                (['uv','run','--frozen','uvicorn','app.main:app','--host','127.0.0.1','--port',str(api_port)],ROOT/'apps/api','api.log'),
                ([*PNPM,'--filter','@portfolio/web','exec','next','dev','--port',str(web_port)],ROOT,'web.log'),
            ]
            for command, cwd, filename in commands:
                output = (log_dir/filename).open('w')
                logs.append(output)
                processes.append(subprocess.Popen(command,cwd=cwd,env=env,stdout=output,stderr=subprocess.STDOUT,start_new_session=True))
            wait_ready(f'http://127.0.0.1:{api_port}/api/v1/health/ready',processes)
            wait_ready(f'http://localhost:{web_port}/',processes)
            print(f'Isolated E2E stack ready at http://localhost:{web_port}; owner credentials remain in process memory.',flush=True)
            result = subprocess.run([*PNPM,'exec','playwright','test',*args.playwright_args],cwd=ROOT,env=env)
            return result.returncode
        finally:
            for process in processes:
                if process.poll() is None:
                    os.killpg(process.pid,signal.SIGTERM)
            for process in processes:
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL)
                    process.wait(timeout=5)
            for output in logs:
                output.close()
            if created:
                validate_database_name(name)
                with operator.connect() as connection:
                    connection.exec_driver_sql(f'DROP DATABASE "{name}" WITH (FORCE)')
                print('Isolated E2E database and media removed. Development data is unchanged.',flush=True)
            operator.dispose()
            signal.signal(signal.SIGTERM,previous_term)

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except (RuntimeError,ValueError) as error:
        raise SystemExit(str(error)) from None
