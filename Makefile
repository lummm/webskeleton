.PHONY: install
install:
	python -m pip install -r requirements.txt

.PHONY: install-dev
install-dev:
	python -m pip install --upgrade .

.PHONY: test
test: install-dev
	./test/run.sh
