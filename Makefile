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
	cp tools/dollchan/src/Dollchan_Extension_Tools.es6.user.js posts/static/dollchan.js
	$(MANAGE) collectstatic

.PHONY: test migrate
