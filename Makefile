# SHELL:=/bin/bash
.DEFAULT_GOAL:=help

export ROOTDIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# activate the virtualenv
export VIRTUAL_ENV := $(ROOTDIR)/venv
export PATH        :=$(ROOTDIR)/venv/bin:$(PATH)

## Print this help
help:
	@awk -v skip=1 \
		'/^##/ { sub(/^[#[:blank:]]*/, "", $$0); doc_h=$$0; doc=""; skip=0; next } \
		 skip  { next } \
		 /^#/  { doc=doc "\n" substr($$0, 2); next } \
		 /:/   { sub(/:.*/, "", $$0); printf "\033[1m%-30s\033[0m\033[1m%s\033[0m %s\n\n", $$0, doc_h, doc; skip=1 }' \
		$(MAKEFILE_LIST)


## Install all dependencies
# Usage:
#  make deps
deps: deps-python

#/ activates virenv and installs deps
deps-python:
	@cd "$(ROOTDIR)"
	@if [ ! -d $(VIRTUAL_ENV)/bin ] ; \
	then \
		python3 -m venv "$(VIRTUAL_ENV)" ;\
	fi
	. $(VIRTUAL_ENV)/bin/activate ; \
	$(VIRTUAL_ENV)/bin/pip3 install -q --upgrade pip ; \
	$(VIRTUAL_ENV)/bin/pip3 install -q -r $(ROOTDIR)/requirements.txt


## Initiate a full test (of all tests)
# Usage:
#  make test CLUSTER=qahivol NAMESPACE=foo
test: test-generic

#/ generic test
test-generic: deps
	./example.py --cluster $(CLUSTER) --namespace $(NAMESPACE)

#? clean up venv
clean:
	rm -rf $(VIRTUAL_ENV)

