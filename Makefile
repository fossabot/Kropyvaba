MANAGE=./manage.py

test:
	flake8 --statistics --exclude='.env*, *migrations, manage.py' .
	$(MANAGE) test

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

collect:
	$(MANAGE) collectstatic

.PHONY: test migrate
