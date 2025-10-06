all: sort check_static_typing lint detect_cycles

sort:
	isort src/ezwrite

check_static_typing:
	mypy src --check-untyped-defs

lint:
	pylint src

detect_cycles:
	cd src/ezwrite; pycycle --here

run:
	cd src; ../.venv/bin/python3 -m main

.PHONY: all check_static_typing lint detect_cycles sort run
