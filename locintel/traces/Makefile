all: deployment ship

clean:
	rm -rf build/ dist/ .eggs/ *.egg-info/ || true

deployment: clean
	python3 setup.py sdist bdist_wheel --universal

ship: deployment
	twine upload -u ${USERNAME} -p ${PASSWORD} --repository-url https://nexus.mobilityservices.io/repository/pypi-hosted/ dist/*

.PHONY: clean ship
