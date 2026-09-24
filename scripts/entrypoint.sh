#!/usr/bin/env bash
set -e

# Optional embedded PostgreSQL 16 startup when START_EMBEDDED_POSTGRES=true and ALLOYDB_HOST=127.0.0.1
if [ "${START_EMBEDDED_POSTGRES:-false}" = "true" ] && [ "${ALLOYDB_HOST:-127.0.0.1}" = "127.0.0.1" ]; then
    if command -v pg_ctlcluster >/dev/null 2>&1; then
        echo "Starting embedded PostgreSQL cluster for AlloyDB/PostgreSQL schema compatibility..."
        service postgresql start || true
        su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname = '${ALLOYDB_DATABASE:-brand_hitl_db}'\" | grep -q 1 || createdb ${ALLOYDB_DATABASE:-brand_hitl_db}" || true
        su - postgres -c "psql -d ${ALLOYDB_DATABASE:-brand_hitl_db} -c \"ALTER USER postgres WITH PASSWORD '${ALLOYDB_PASSWORD:-postgres}';\"" || true
    fi
fi

exec uvicorn "${APP_MODULE:-services.approval_ui.app:app}" --host 0.0.0.0 --port "${PORT:-8080}"
