VERSION=2.0.0
BUILDDIR='~build'
PYTHONPATH:=${PWD}/tests/:${PWD}
DBENGINE?=pg
DJANGO?='last'


.mkbuilddir:
	mkdir -p ${BUILDDIR}

develop:
	@pip install pipenv
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then pip install  MySQL-python; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then pip install -q psycopg2; fi"
	$(MAKE) .init-db
	@pipenv install -d --skip-lock


.init-db:
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -h 127.0.0.1 -u root -e 'DROP DATABASE IF EXISTS concurrency;'; fi"
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -h 127.0.0.1 -u root -e 'CREATE DATABASE IF NOT EXISTS concurrency;'; fi"

	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -h localhost -c 'DROP DATABASE IF EXISTS concurrency;' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -h localhost -c 'CREATE DATABASE concurrency;' -U postgres; fi"

test:
	py.test -v --create-db

lint:
	pipenv run flake8 src/ tests/
	pipenv run isort -rc src/ --check-only
	pipenv run check-manifest


clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage coverage.xml .eggs
	find src -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find tests -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find src/concurrency/locale -name django.mo | xargs rm -f

fullclean:
	rm -fr .tox .cache
	$(MAKE) clean


docs: .mkbuilddir
	mkdir -p ${BUILDDIR}/docs
	pipenv run sphinx-build -aE docs/ ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif
