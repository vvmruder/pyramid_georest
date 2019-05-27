# Check if running on CI
ifeq ($(CI),true)
  PIP_REQUIREMENTS=requirements.timestamp
  VENV_BIN=
else
  PIP_REQUIREMENTS=.venv/requirements.timestamp
  VENV_BIN=.venv/bin/
endif

# ********************
# Variable definitions
# ********************

# Set pip and setuptools versions
PIP_VERSION ?= pip>=7,<8
SETUPTOOL_VERSION ?= setuptools>=12

# Development switch
DEVELOPMENT ?= FALSE

# Package name
PKG = pyramid_georest

# Build dependencies
BUILD_DEPS +=

SPHINXOPTS =
SPHINXBUILD = $(VENV_BIN)sphinx-build$(PYTHON_BIN_POSTFIX)
SPHINXPROJ = pyramid_georest
SOURCEDIR = doc/source
BUILDDIR = doc/build

requirements.timestamp: requirements.txt
	pip install '$(PIP_VERSION)' '$(SETUPTOOL_VERSION)'
	pip install --upgrade -r requirements.txt
	touch $@

.venv/.timestamp:
	virtualenv .venv
	$(VENV_BIN)pip install '$(PIP_VERSION)' '$(SETUPTOOL_VERSION)'
	touch $@

.venv/requirements.timestamp: .venv/.timestamp requirements.txt setup.py
	$(VENV_BIN)pip install -r requirements.txt --trusted-host www.geo.bl.ch
	touch $@

# **************
# Common targets
# **************

$(SPHINXBUILD): .venv/requirements.timestamp
	$(VENV_BIN)pip$(PYTHON_BIN_POSTFIX) install "Sphinx<1.6" sphinx_rtd_theme

.PHONY: doc
doc: $(SPHINXBUILD)
	$(VENV_BIN)python setup.py develop
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: clean
clean:
	rm -rf build
	rm -rf dist
	rm -rf .tox
	rm -rf .cache
	rm -f .coverage

.PHONY: clean-all
clean-all: clean
	rm -rf .venv
	rm -rf $(PKG).egg-info

.PHONY: git-attributes
git-attributes:
	git --no-pager diff --check `git log --oneline | tail -1 | cut --fields=1 --delimiter=' '`

.PHONY: lint
lint: $(PIP_REQUIREMENTS) setup.cfg $(SRC_PY)
	$(VENV_BIN)flake8

.PHONY: test
test: $(PIP_REQUIREMENTS) $(SRC_PY) $(CONFIG_FILE)
	$(VENV_BIN)py.test -vv --cov-config .coveragerc --cov $(PKG) --cov-report term-missing:skip-covered test/py

.PHONY: tox
tox: $(PIP_REQUIREMENTS) tox.ini $(SRC_PY) $(CONFIG_FILE)
	$(VENV_BIN)tox --recreate --skip-missing-interpreters

.PHONY: check
check: git-attributes lint tox

.PHONY: build
build: $(BUILD_DEPS) $(PIP_REQUIREMENTS)
