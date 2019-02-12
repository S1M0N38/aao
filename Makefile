pipenv:
	pip install pipenv --upgrade
	pipenv install --dev

chromedriver:
	wget -N https://chromedriver.storage.googleapis.com/2.38/chromedriver_linux64.zip -P ~/
	unzip ~/chromedriver_linux64.zip -d ~/
	rm ~/chromedriver_linux64.zip
	sudo mv -f ~/chromedriver /usr/local/share/
	sudo chmod +x /usr/local/share/chromedriver
	sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver

test:
	pytest -m eight88sport --proxy ${PROXY}
	pytest -m bet365
	pytest -m bwin
	pytest -m williamhill
	pytest --ignore=aao/test/spiders/bookmakers

coverage:
	pipenv run python-codacy-coverage -r coverage.xml

lint:
	pipenv run flake8 --ignore=E501,W391

dist:
	pipenv install twine
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg requests.egg-info
