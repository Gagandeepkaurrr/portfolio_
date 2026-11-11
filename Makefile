.DEFAULT_GOAL := help
.PHONY: help configure install dev db migrate seed import-resume admin-create admin-reset revoke-sessions test e2e build verify up down backup restore cleanup-dry-run cleanup contracts
help:
	@python3 -c "print('Portfolio commands: configure install db migrate seed dev admin-create admin-reset import-resume test e2e build verify up down backup restore cleanup-dry-run cleanup contracts')"
configure:
	@python3 scripts/configure.py
install:
	@python3 scripts/manage.py install
db:
	@docker compose up -d --wait db
dev:
	@python3 scripts/manage.py dev
migrate:
	@python3 scripts/manage.py migrate
seed:
	@python3 scripts/manage.py seed
import-resume:
	@python3 scripts/manage.py import-resume "$(RESUME_PATH)"
admin-create:
	@python3 scripts/manage.py admin-create
admin-reset:
	@python3 scripts/manage.py admin-reset
revoke-sessions:
	@python3 scripts/manage.py revoke-sessions
test:
	@python3 scripts/manage.py test
e2e:
	@python3 scripts/manage.py e2e
build:
	@python3 scripts/manage.py build
verify:
	@python3 scripts/manage.py verify
up:
	@python3 scripts/manage.py up
down:
	@python3 scripts/manage.py down
backup:
	@python3 scripts/backup.py --mode "$(or $(MODE),development)"
restore:
	@python3 scripts/restore.py --backup "$(BACKUP)" --name "$(RESTORE_NAME)"
cleanup-dry-run:
	@python3 scripts/manage.py cleanup-dry-run
cleanup:
	@python3 scripts/manage.py cleanup
contracts:
	@npx --yes pnpm@12.18.0 contracts
