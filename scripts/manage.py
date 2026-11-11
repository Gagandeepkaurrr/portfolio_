#!/usr/bin/env python3
"""Repository-root command entry points with inherited, private environment."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PNPM = ['npx', '--yes', 'pnpm@12.18.0']

def environment():
    values = {}
    path = ROOT / '.env'
    if path.exists():
        for line in path.read_text().splitlines():
            if line and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('\"', "'"):
                    value = value[1:-1]
                values[key.strip()] = value
    values.update(os.environ)
    return values

def run(args, cwd=ROOT, env=None):
    subprocess.run(args, cwd=cwd, env=env or environment(), check=True)

def api(*args):
    run(['uv', 'run', '--frozen', *args], ROOT / 'apps/api')

def dev():
    run(['docker', 'compose', 'up', '-d', '--wait', 'db'])
    api('alembic', 'upgrade', 'head')
    api('python', '-m', 'app.cli', 'seed')
    env = environment()
    entries = [(['uv', 'run', '--frozen', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', env.get('API_DEV_PORT','8100'), '--reload'], ROOT / 'apps/api'),
               ([*PNPM, '--filter', '@portfolio/web', 'dev'], ROOT)]
    processes = []
    def stop_requested(*_):
        raise KeyboardInterrupt
    previous_term = signal.signal(signal.SIGTERM, stop_requested)
    registry = ROOT / '.data/dev-processes.json'
    registry.parent.mkdir(exist_ok=True)
    try:
        for args, cwd in entries:
            process = subprocess.Popen(args, cwd=cwd, env=env, start_new_session=True)
            processes.append(process)
        registry.write_text(json.dumps({'manager': os.getpid(), 'groups': [p.pid for p in processes]}))
        registry.chmod(0o600)
        print('Portfolio running at http://localhost:3000. Ctrl+C stops the app; database volume remains.', flush=True)
        while all(p.poll() is None for p in processes):
            time.sleep(0.5)
        failed = [p.returncode for p in processes if p.returncode is not None]
        if any(failed):
            raise SystemExit(next(code for code in failed if code))
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
        registry.unlink(missing_ok=True)
        signal.signal(signal.SIGTERM, previous_term)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['install','dev','migrate','seed','import-resume','admin-create','admin-reset','revoke-sessions','test','e2e','build','verify','up','down','cleanup-dry-run','cleanup','export-openapi'])
    parser.add_argument('extra', nargs='*')
    args = parser.parse_args()
    command = args.command
    if command == 'install':
        run([*PNPM, 'install', '--frozen-lockfile'])
        run(['uv', 'sync', '--frozen', '--project', 'apps/api'])
    elif command == 'dev':
        dev()
    elif command == 'migrate':
        api('alembic', 'upgrade', 'head')
    elif command in ('seed','admin-create','admin-reset','revoke-sessions','export-openapi'):
        api('python', '-m', 'app.cli', command, *args.extra)
    elif command == 'import-resume':
        if len(args.extra) != 1 or not Path(args.extra[0]).is_file():
            parser.error('import-resume requires one existing PDF path; use make import-resume RESUME_PATH=/absolute/path.pdf')
        api('python', '-m', 'app.cli', 'import-resume', str(Path(args.extra[0]).resolve()))
    elif command == 'test':
        api('pytest')
        run([*PNPM, 'test'])
    elif command == 'e2e':
        api('python', str(ROOT/'scripts/e2e_stack.py'))
    elif command == 'build':
        run([*PNPM, 'build'])
        api('python', '-m', 'compileall', '-q', 'app')
    elif command == 'verify':
        api('ruff', 'check', 'app', 'tests')
        api('mypy', 'app')
        run(['python3','-m','unittest','discover','-s','tests/ops','-v'])
        run([*PNPM, 'lint'])
        run([*PNPM, 'typecheck'])
        run([*PNPM, 'contracts:check'])
        api('pytest')
        run([*PNPM, 'test'])
        run([*PNPM, 'build'])
    elif command == 'up':
        run(['docker','compose','-f','compose.production.yaml','up','-d','--build','--wait'])
    elif command == 'down':
        run(['docker','compose','stop'])
        run(['docker','compose','-f','compose.production.yaml','stop'])
    elif command.startswith('cleanup'):
        api('python','-m','app.cli','cleanup', *(['--apply'] if command == 'cleanup' else []))

if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None
