.PHONY: build dist test dist-package server dev test clean

PACKAGE_VERSION=$(shell cat package.json | grep version | head -1 | awk -F: '{ print $$2 }' | sed 's/[ ",]//g')

build: clean test dist

dist:
	npm run build

dist-package: dist
	tar -czf spotboard-webapp-$(PACKAGE_VERSION).tar.gz --transform 's,^dist,spotboard-webapp-$(PACKAGE_VERSION),' dist
	echo spotboard-webapp-$(PACKAGE_VERSION).tar.gz

server:
	echo 'Launching Prod Server (dist/) ...'
	npm run server

dev:
	echo 'Launching Dev Server ...'
	npm start

test:
	npm test

clean:
	rm -rf src/js/contest.js
	rm -rf src/js/metadata.js
	rm -rf spotboard-*.tar.gz
	rm -rf dist/
	rm -rf cert/