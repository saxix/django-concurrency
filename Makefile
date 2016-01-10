VERSION=2.0.0
BUILDDIR='~build'
PYTHONPATH:=${PWD}/tests/:${PWD}
DBENGINE?=pg
DJANGO?='last'


.mkbuilddir:
	mkdir -p ${BUILDDIR}

develop:
	@pip install -U pip setuptools
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then pip install  MySQL-python; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then pip install -q psycopg2; fi"
#	@sh -c "if [ '${DJANGO}' = '1.4.x' ]; then pip install 'django>=1.4,<1.5'; fi"
#	@sh -c "if [ '${DJANGO}' = '1.5.x' ]; then pip install 'django>=1.5,<1.6'; fi"
#	@sh -c "if [ '${DJANGO}' = '1.6.x' ]; then pip install 'django>=1.6,<1.7'; fi"
#	@sh -c "if [ '${DJANGO}' = '1.7.x' ]; then pip install 'django>=1.7,<1.8'; fi"
#	@sh -c "if [ '${DJANGO}' = '1.8.x' ]; then pip install 'django>=1.8,<1.9'; fi"
#	@sh -c "if [ '${DJANGO}' = '1.9.x' ]; then pip install 'django>=1.9,<1.10'; fi"
#	@sh -c "if [ '${DJANGO}' = 'last' ]; then pip install django; fi"
#	@sh -c "if [ '${DJANGO}' = 'dev' ]; then pip install git+git://github.com/django/django.git; fi"
	@pip install -e .[dev]
	$(MAKE) .init-db


.init-db:
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -u root -e 'DROP DATABASE IF EXISTS concurrency;'; fi"
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -u root -e 'CREATE DATABASE IF NOT EXISTS concurrency;'; fi"

	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -c 'DROP DATABASE IF EXISTS concurrency;' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -c 'CREATE DATABASE concurrency;' -U postgres; fi"

test:
	py.test -v

qa:
	flake8 src/ tests/
	isort -rc src/ --check-only
	check-manifest


clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage coverage.xml
	find src -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find tests -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find src/concurrency/locale -name django.mo | xargs rm -f

fullclean:
	rm -fr .tox .cache
	$(MAKE) clean


docs: .mkbuilddir
	mkdir -p ${BUILDDIR}/docs
	sphinx-build -aE docs/ ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif
