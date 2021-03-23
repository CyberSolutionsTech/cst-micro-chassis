.DEFAULT_GOAL := build
.PHONY: build test clean
SHELL := /bin/bash

ifndef pyversion
override pyversion = py39
endif

build:
	$(RM) -r ./build_venv ./dist/ ./build/
	python3 -m venv ./build_venv
	source ./build_venv/bin/activate \
&& pip install twine wheel --quiet --disable-pip-version-check \
&& python3 setup.py sdist bdist_wheel \
&& python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

test:
	$(RM) -r ./test_venv
	python3 -m venv ./test_venv
	source ./test_venv/bin/activate \
&& pip install tox  --quiet --disable-pip-version-check \
&& tox -e $(pyversion)

clean:
	@echo "Cleaning up . . ."
	$(RM) -r ./dist/ ./build/ ./test_venv ./build_venv
	@echo "Cleanup finished."
