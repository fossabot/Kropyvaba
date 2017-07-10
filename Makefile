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
	wget https://code.jquery.com/jquery-3.2.1.slim.min.js -O tools/jquery/jquery-3.2.1.slim.min.js
	cp tools/dollchan/src/Dollchan_Extension_Tools.es6.user.js posts/static/dollchan.js
	cp tools/jquery/jquery-3.2.1.slim.min.js posts/static/jquery.js
	yes yes | $(MANAGE) collectstatic

.PHONY: test migrate
