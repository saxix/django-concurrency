VERSION=2.0.0
BUILDDIR='~build'
PYTHONPATH := ${PWD}/tests/:${PWD}
DJANGO_14='django>=1.4,<1.5'
DJANGO_15='django>=1.5,<1.6'
DJANGO_16='django>=1.6,<1.7'
DJANGO_17='django>=1.7,<1.8'
DJANGO_18='django>=1.8,<1.9'
DJANGO_DEV=git+git://github.com/django/django.git
DBENGINE?=pg
DJANGO?='1.7.x'


mkbuilddir:
	mkdir -p ${BUILDDIR}

install-deps:
	@pip install "pip>=6.0.8"
	@pip install -qr requirements/tests.pip
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then pip install  MySQL-python; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then pip install -q psycopg2; fi"
	@sh -c "if [ '${DJANGO}' = '1.4.x' ]; then pip install ${DJANGO_14}; fi"
	@sh -c "if [ '${DJANGO}' = '1.5.x' ]; then pip install ${DJANGO_15}; fi"
	@sh -c "if [ '${DJANGO}' = '1.6.x' ]; then pip install ${DJANGO_16}; fi"
	@sh -c "if [ '${DJANGO}' = '1.7.x' ]; then pip install ${DJANGO_17}; fi"
	@sh -c "if [ '${DJANGO}' = '1.8.x' ]; then pip install ${DJANGO_18}; fi"
	@sh -c "if [ '${DJANGO}' = 'dev' ]; then pip install ${DJANGO_DEV}; fi"


init-db:
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -u root -e 'DROP DATABASE IF EXISTS concurrency;'; fi"
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -u root -e 'CREATE DATABASE IF NOT EXISTS concurrency;'; fi"

	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -c 'DROP DATABASE IF EXISTS concurrency;' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -c 'CREATE DATABASE concurrency;' -U postgres; fi"

test:
	py.test -vx --lf --pdb


coverage: mkbuilddir install-deps init-db
	echo $PYTHONPATH;
	py.test tests -vx --cov=concurrency --cov-report=html --cov-config=tests/.coveragerc -q


clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage
	find . -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find concurrency/locale -name django.mo | xargs rm -f


docs: mkbuilddir
	mkdir -p ${BUILDDIR}/docs
	sphinx-build -aE docs/ ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif

