PYTHON ?= python
NPM ?= npm
GO ?= go

.PHONY: validate validate-legacy test conformance conformance-legacy repository-check typescript go all

validate:
	$(PYTHON) reference-validator/jep_validate_07.py validate test-vectors/0.7/valid/J-basic.json --keys test-vectors/0.7/keys.json

validate-legacy:
	$(PYTHON) reference-validator/jep_validate.py validate test-vectors/interop/control-J.json --keys test-vectors/interop/public-keys.json
	$(PYTHON) reference-validator/jep_validate.py validate-chain test-vectors/valid/delegation-verification-termination-chain.jsonl --keys test-vectors/valid/public-keys.json --trust-profile kid-prefix

conformance:
	$(PYTHON) reference-validator/jep_validate_07.py run-tests test-manifest-0.7.json

conformance-legacy:
	$(PYTHON) reference-validator/jep_validate.py run-tests test-manifest-0.6.json

repository-check:
	$(PYTHON) scripts/check_repository.py

test:
	$(PYTHON) -m pytest

typescript:
	cd typescript-validator && $(NPM) install && $(NPM) run check

go:
	cd go-validator && $(GO) test ./...

all: repository-check test conformance conformance-legacy go
