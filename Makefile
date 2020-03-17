# Check if running on CI
ifeq ($(CI),true)
  VENV_BIN=.venv/bin/
  PIP_COMMAND=pip
else
  VENV_BIN=.venv/bin/
  PIP_COMMAND=pip3
endif

# ********************
# Variable definitions
# ********************

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

.venv/.timestamp:
	python3 -m venv .venv
	$(VENV_BIN)$(PIP_COMMAND) install --upgrade pip setuptools
	touch $@

.venv/requirements.timestamp: .venv/.timestamp requirements.txt setup.py
	$(VENV_BIN)$(PIP_COMMAND) install -r requirements.txt --trusted-host www.geo.bl.ch
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

.PHONY: clean-doc
clean-doc:
	rm -rf $(BUILDDIR)

.PHONY: clean
clean: clean-doc
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
lint: .venv/requirements.timestamp setup.cfg $(SRC_PY)
	$(VENV_BIN)flake8

.PHONY: test
test: .venv/requirements.timestamp $(SRC_PY) $(CONFIG_FILE)
	$(VENV_BIN)python setup.py develop
	$(VENV_BIN)py.test -vv --cov-config .coveragerc --cov $(PKG) --cov-report term-missing:skip-covered test/py

.PHONY: tox
tox: .venv/requirements.timestamp tox.ini $(SRC_PY) $(CONFIG_FILE)
	$(VENV_BIN)tox --recreate --skip-missing-interpreters

.PHONY: check
check: git-attributes lint tox

.PHONY: build
build: $(BUILD_DEPS) .venv/requirements.timestamp
