pipenv:
	pip install pipenv --upgrade -q
	pipenv install --dev --skip-lock

chromedriver:
	wget -q -N https://chromedriver.storage.googleapis.com/2.38/chromedriver_linux64.zip -P ~/
	unzip -q ~/chromedriver_linux64.zip -d ~/
	rm ~/chromedriver_linux64.zip
	sudo mv -f ~/chromedriver /usr/local/share/
	sudo chmod +x /usr/local/share/chromedriver
	sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver

test:
	pytest -m eight88sport
	pytest -m bet365
	pytest -m bwin
	pytest -m williamhill
	pytest -m sports
	pytest --ignore=aao/test/spiders/bookmakers --ignore=aao/test/spiders/test_sports.py

coverage:
	pipenv run python-codacy-coverage -r coverage.xml

lint:
	pipenv run flake8 --ignore=E501,W391
