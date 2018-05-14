init:
	pip install -r requirements.txt

test:
	py.test tests

clean:
	rm -f eedlab/*.pyc

.PHONY: init test
