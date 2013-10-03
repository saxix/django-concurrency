VERSION=2.0.0
BUILDDIR='~build'
DJANGO_SETTINGS_MODULE:=demoproject.settings
PYTHONPATH := ${PWD}/demo/:${PWD}
PIP=${VIRTUAL_ENV}/bin/pip

mkbuilddir:
	mkdir -p ${BUILDDIR}

install-deps:
	pip install -r demo/demoproject/requirements.pip -r requirements.pip python-coveralls coverage


locale:
	cd concurrency && django-admin.py makemessages -l en
	export PYTHONPATH=${PYTHONPATH}
	cd concurrency && django-admin.py compilemessages --settings=${DJANGO_SETTINGS_MODULE}

docs: mkbuilddir
	sphinx-build -aE docs ${BUILDDIR}/docs
	firefox ${BUILDDIR}/docs/index.html

test:
	demo/manage.py test concurrency --settings=${DJANGO_SETTINGS_MODULE}


ci:
	@[ "${DJANGO}" = "1.4.x" ] && pip install django==1.4.8 || :
	@[ "${DJANGO}" = "1.5.x" ] && pip install django==1.5.4 || :
	@[ "${DJANGO}" = "1.6.x" ] && pip install https://www.djangoproject.com/m/releases/1.6/Django-1.6b4.tar.gz || :
	@[ "${DJANGO}" = "dev" ] && pip install git+git://github.com/django/django.git || :

	@python -c "import django;print 'python version:', django.get_version();"

	@[ "${DBENGINE}" = "pg" ] && pip install -q psycopg2 || :
	@[ "${DBENGINE}" = "mysql" ] && pip install git+git@github.com:django/django.git || :
	@pip install coverage
	@python -c "from __future__ import print_function;import django;print('Django version:', django.get_version())"

	coverage run demo/manage.py test concurrency --settings=${DJANGO_SETTINGS_MODULE}
	coverage report

cov-html: coverage mkbuilddir
	coverage html

clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage
	find . -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find concurrency/locale -name django.mo | xargs rm -f

.PHONY: docs test
