FROM openjdk:11

ARG version=1.4.2

RUN wget https://repo1.maven.org/maven2/org/topbraid/shacl/$version/shacl-$version-bin.zip
RUN unzip shacl-$version-bin.zip

WORKDIR /shacl-$version/bin

RUN chmod 744 shaclinfer.sh shaclvalidate.sh

ENV PATH=$PATH:/shacl-$version/bin

WORKDIR /mnt/data

ENTRYPOINT [ "shaclvalidate.sh" ]