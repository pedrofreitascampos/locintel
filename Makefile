all: deployment

clean:
	rm -rf build/ dist/ .eggs/ *.egg-info/ || true

deployment: clean
	python setup.py sdist bdist_wheel --universal

