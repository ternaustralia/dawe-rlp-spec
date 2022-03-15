watch:
	watchmedo shell-command \
		--patterns="*.adoc;*.css" \
		--ignore-directories \
		--recursive \
		--command='make build' \
		.

build:
	asciidoctor --trace -a stylesheet=styles.css -o ../build/index.html source/index.adoc

run:
	python3 -m http.server -d ../build
