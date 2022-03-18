# shape=shapes.ttl
# data=data.ttl
shape=shapes/plot-description/slope/shapes.ttl
data=shapes/plot-description/slope/invalid.ttl
SOURCES := $(shell find shapes -name "*.ttl")

pyshacl-af:
	pyshacl -s ${shape} ${data} -a

pyshacl:
	pyshacl -s ${shape} ${data}

validate:
	shaclvalidate.sh -datafile ${data} -shapesfile ${shape}

validate-meta:
	shaclvalidate.sh -datafile ${data} -shapesfile ${shape} -validateShapes

normalize:
	for file in $(SOURCES) ; do \
		ontotools file normalize $$file ; \
	done