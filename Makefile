.PHONY: clean virtualenv install test dist docs upload

VENV:=$(shell pwd)/env

clean:
	@if test -d $(VENV); then rm -rf $(VENV); fi

virtualenv:
	@if test ! -d $(VENV); then pyvenv $(VENV); fi

base-install: virtualenv
	. $(VENV)/bin/activate; pip install -r requirements/base.txt

tests-install: virtualenv
	. $(VENV)/bin/activate; pip install -r requirements/tests.txt

docs-install: virtualenv
	. $(VENV)/bin/actiave; pip install -r requirements/docs.txt

install: virtualenv base-install
	. $(VENV)/bin/activate; python setup.py install

test: virtualenv tests-install
	. $(VENV)/bin/activate; py.test --cov=yawf tests

docs: virtualenv docs-install
	. $(VENV)/bin/activate; cd docs; make html

dist: virtualenv
	. $(VENV)/bin/activate; python setup.py bdist_wheel; python setup.py sdist

upload: virtualenv dist
	. $(VENV)/bin/activate; python setup.py sdist bdist_wheel upload
