
run:
	python -m sqlite2duckdb 
	
build:
	rm -Rf dist/ ; python -m build

test:
	python -m pytest

publish:
	python -m twine upload  dist/*
