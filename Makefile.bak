# shape=shapes.ttl
# data=data.ttl
shape=shapes/plot-description/slope/shapes.ttl
data=shapes/plot-description/slope/invalid.ttl

pyshacl-af:
	pyshacl -s ${shape} ${data} -a

pyshacl:
	pyshacl -s ${shape} ${data}

validate:
	docker run --rm -it -v $(PWD):/mnt/data shacl -datafile ${data} -shapesfile ${shape}

validate-meta:
	docker run --rm -it -v $(PWD):/mnt/data shacl -datafile ${data} -shapesfile ${shape} -validateShapes

build:
	docker build -t shacl .