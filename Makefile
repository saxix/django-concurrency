VERSION=2.0.0
BUILDDIR='~build'
DJANGO_SETTINGS_MODULE:=demoproject.settings
PYTHONPATH := ${PWD}/demo/:${PWD}

locale:
	cd concurrency && django-admin.py makemessages -l en
	export PYTHONPATH=${PYTHONPATH}
	cd concurrency && django-admin.py compilemessages --settings=${DJANGO_SETTINGS_MODULE}

docs:
	mkdir -p ${BUILDDIR}/
	sphinx-build -aE docs ${BUILDDIR}/docs
	firefox ${BUILDDIR}/docs/index.html

test:
	export PYTHONPATH=${PYTHONPATH}
	coverage run demo/manage.py test concurrency --settings=${DJANGO_SETTINGS_MODULE}

coverage:
	export PYTHONPATH=${PYTHONPATH}
	coverage run demo/manage.py test concurrency --settings=${DJANGO_SETTINGS_MODULE}
	coverage report

clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage
	find concurrency/locale -name django.mo | xargs rm -f

.PHONY: docs
