# shape=shapes.ttl
# data=data.ttl
shape=shapes/plot-description/cover-class/shapes.ttl
data=shapes/plot-description/cover-class/invalid.ttl
SOURCES := $(shell find shapes -name "*.ttl")
SHAPES := $(shell find shapes -name "shapes.ttl")
SHAPE_FOLDER := shapes/condition-protocol-shapes
TARGET_FOLDER := shapes/condition-protocol-shapes

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

validate-shapes:
	for file in $(SHAPES) ; do \
		echo "Validating shapes in file $$file" ; \
		pyshacl -s shapes/_meta/meta.shapes.ttl -a $$file ; \
	done

update-controlled-shapes:
	for file in $(shell find $(SHAPE_FOLDER) -name "shapes.ttl") ; do \
		python update-controlled-shapes.py $$file ; \
	done

aggregate-protocol-shapes:
	python3 aggregate-protocol-shapes.py $(TARGET_FOLDER)

