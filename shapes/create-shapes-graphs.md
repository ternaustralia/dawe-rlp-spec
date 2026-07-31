For each of the direct child folders of shapes/, except for _meta, add a new pair of files to each called sg-metadata.ttl and sg-<folder-name>.ttl, where <folder-name> is the name of the containing folder.

For each sg-metadata.ttl file, add an RDF objects of type sh:ShapesGraph with the following attributes:

* IRI - the IRI of should be a URN which is derived from the folder name
    * for example, in the directory fauna-aerial-survey-protocol-shapes, the URN should be <urn:edes:shapes:fauna-aerial-survey-protocol>
    * for example, in the directory floristics, the URN should be <urn:edes:shapes:floristics>
* schema:name - should start with "EDES", then have a capital case version of the folder name, then end with "Shapes Graph"
    * for example, in the directory fauna-aerial-survey-protocol-shapes, the schema:name values should "Fauna Aerial Survey Protocol Shapes Graph" 
    * for example, in the directory floristics, the URN should be "Floristics Shapes Graph"
* schema:description - with the same value as schema:name
* schema:dateCreated - today's date as an xsd:date literal
* schema:dateModified - today's date as an xsd:date literal
* schema:creator - an IRI, <https://linked.data.gov.au/org/tern>
* schema:publisher - an IRI, <https://linked.data.gov.au/org/tern>
* schema:contributor - an IRI, <https://kurrawong.ai>


For each sg-<folder-name>.ttl, add all the elements within each directory's shapes.ttl and sg-metadata.ttl file but also add:

* to each sh:PropertyShape and sh:NodeShape
    * the predicated rdfs:isDefinedBy indicating the IRI of the Shapes Graph
        * for example, for the Node Shape in floristics/shapes.ttl <urn:shapes:invertebrate-fauna-active-sampling-protocol-shapes:air-temperature:simple-result>, add rdfs:isDefineDby <urn:shapes:floristics>

Serialize all files using RDFLib's longturtle format.
