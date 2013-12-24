VERSION=2.0.0
BUILDDIR='~build'
DJANGO_SETTINGS_MODULE:=demoproject.settings
PYTHONPATH := ${PWD}/demo/:${PWD}
DJANGO_14=django==1.4.10
DJANGO_15=django==1.5.5
DJANGO_16=django==1.6.1
DJANGO_DEV=git+git://github.com/django/django.git


mkbuilddir:
	mkdir -p ${BUILDDIR}

make-cache:
	pip install --no-install --download ${PIP_DOWNLOAD_CACHE}/raw/ \
	    Sphinx==1.1.3 \
	    "setuptools>=2.0.1" \
	    -r demo/demoproject/requirements.pip \
	    -r requirements.pip python-coveralls coverage

install-deps:
	pip install  Sphinx==1.1.3 \
	        "setuptools>=2.0.1" \
	        -r demo/demoproject/requirements.pip \
	        -r requirements.pip python-coveralls coverage


locale:
	cd concurrency && django-admin.py makemessages -l en
	export PYTHONPATH=${PYTHONPATH}
	cd concurrency && django-admin.py compilemessages --settings=${DJANGO_SETTINGS_MODULE}

docs: mkbuilddir
	sphinx-build -aE docs ${BUILDDIR}/docs
	firefox ${BUILDDIR}/docs/index.html

test:
	demo/manage.py test concurrency --settings=${DJANGO_SETTINGS_MODULE} -v2


init-db:
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -e 'DROP DATABASE IF EXISTS concurrency;'; fi"
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then pip install  MySQL-python; fi"
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -e 'CREATE DATABASE IF NOT EXISTS concurrency;'; fi"

	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -c 'DROP DATABASE IF EXISTS concurrency;' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -c 'DROP DATABASE IF EXISTS test_concurrency;' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then psql -c 'CREATE DATABASE concurrency;' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then pip install -q psycopg2; fi"

ci:
	sh -c "if [ '${DJANGO}' = '1.4.x' ]; then pip install ${DJANGO_14}; fi"
	@sh -c "if [ '${DJANGO}' = '1.5.x' ]; then pip install ${DJANGO_15}; fi"
	@sh -c "if [ '${DJANGO}' = '1.6.x' ]; then pip install ${DJANGO_16}; fi"
	@sh -c "if [ '${DJANGO}' = 'dev' ]; then pip install ${DJANGO_DEV}; fi"
	@pip install coverage
	@python -c "from __future__ import print_function;import django;print('Django version:', django.get_version())"
	@echo "Database:" ${DBENGINE}

	$(MAKE) coverage


coverage: mkbuilddir
	py.test --cov=concurrency --cov-report=html --cov-report=term --cov-config=.coveragerc -vvv

clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage
	find . -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find concurrency/locale -name django.mo | xargs rm -f

clonedigger: mkbuilddir
	-clonedigger concurrency -l python -o ${BUILDDIR}/clonedigger.html --fast

.PHONY: docs test
