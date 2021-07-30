import datetime
import json
import sys

from nidm.core.provone import *
from prov.constants import PROV_TYPE
from prov.identifier import Namespace
from main import prefixedString, EAAS

d1 = ProvONEDocument()

# namespaces
WFDESC = Namespace("wfdesc", "http://purl.org/wf4ever/wfdesc#")
WFPROV = Namespace("wfprov", "http://purl.org/wf4ever/wfprov#")
WF4EVER = Namespace("wf4ever", "http://purl.org/wf4ever/wf4ever#")

d1.add_namespace('eaas', 'eaas#')
d1.add_namespace("", "#")
d1.add_namespace('prov', 'http://www.w3.org/ns/prov#')
d1.add_namespace("dcterms", "http://purl.org/dc/terms#")
d1.add_namespace("cwlprov", "https://w3id.org/cwl/prov#")
d1.add_namespace("wfprov", "http://purl.org/wf4ever/wfprov#")
d1.add_namespace("wfdesc", "http://purl.org/wf4ever/wfdesc#")
d1.add_namespace("wf4ever", "http://purl.org/wf4ever/wf4ever#")
d1.add_namespace("foaf", "http://xmlns.com/foaf/0.1/#")

# base data
with open(sys.argv[1]) as orig_file:
    creation_data = json.load(orig_file)

env = creation_data["environment"]
creation = creation_data["creation"]
container = creation_data["container"]

environmentId = env["environmentId"]
os = env["os"]
title = env["title"]
description = env["description"]

author = creation["userId"]
createdAt = creation["createdAt"]

digest = container["digest"]
tag = container["tag"]
containerUrl = container["containerUrl"]

# execution data
for i in range(len(sys.argv) - 2):
    with open(sys.argv[i + 2]) as exec_file:
        execution_data = json.load(exec_file)

startedAt = execution_data["startedAt"]
endedAt = execution_data["endedAt"]
inputFolder = execution_data["inputFolder"]
outputFolder = execution_data["outputFolder"]

inputs = execution_data["inputs"]
outputs = execution_data["outputs"]
user = execution_data["user"]

# tool provenance

original = d1.process(":originalTool", {":digest": digest, ":url": containerUrl, ":tag": tag,
                                        prefixedString("dcterms", "date"): createdAt})

tool = d1.process("eaas:tool", {"dcterms:title": title, "dcterms:description": description})

author = d1.user(":author", {"foaf:givenName": author})
tool.wasAttributedTo(author)
tool.wasDerivedFrom(original)

environment = d1.entity("eaas:environment",
                        {prefixedString(EAAS, "envId"): environmentId,
                         prefixedString(EAAS, "os"): os,
                         prefixedString("dcterms", "date"): createdAt})
# execution provenance

input_port = d1.input_port("eaas:input")
output_port = d1.output_port("eaas:output")

d1.has_out_ports(tool, output_port)
d1.has_in_ports(tool, input_port)

tool_execution = d1.processExec("eaas:exec", startTime=datetime.datetime.now(),
                                endTime=datetime.datetime.now())

logged_in_user = d1.user("eaas:logged_in_user")

tool_execution.used(environment)
tool_execution.wasAssociatedWith(logged_in_user)
# asso = d1.association(tool_execution,)
# asso.add_attributes({"provone:hadPlan" : tool})


input1 = d1.data("eaas:input1", [(PROV_TYPE, WFPROV["Artifact"]), (PROV_TYPE, WF4EVER["File"])])

input1.add_attributes({"cwlprov:basename": "input1.txt",
                       "cwlprov:nameroot": "input1",
                       "cwlprov:nameext": "txt"})
tool_execution.used(input1)

input_usage = d1.usage(tool_execution, input1)
input_usage.add_attributes({"provone:hadInPort": input_port})

# TODO PRONOM PUIDS
output1 = d1.data("eaas:output1",
                  [(PROV_TYPE, WFPROV["Artifact"]), (PROV_TYPE, WF4EVER["File"])])
output1.add_attributes({"cwlprov:basename": "file_0.txt",
                        "cwlprov:nameroot": "file_0",
                        "cwlprov:nameext": "txt"})

output2 = d1.data("eaas:output2",
                  [(PROV_TYPE, WFPROV["Artifact"]), (PROV_TYPE, WF4EVER["File"])])
output2.add_attributes({"cwlprov:basename": "additionalFile.txt",
                        "cwlprov:nameroot": "additionalFile",
                        "cwlprov:nameext": "txt"})

output_log = d1.data("eaas:logfile",
                     [(PROV_TYPE, WFPROV["Artifact"]), (PROV_TYPE, WF4EVER["File"])])
output_log.add_attributes(
    {"cwlprov:basename": "container-log-f711ca19-ac31-44b7-b8eb-58bf705b79e8.log",
     "cwlprov:nameroot": "container-log-f711ca19-ac31-44b7-b8eb-58bf705b79e8",
     "cwlprov:nameext": "log"})

output_generation1 = d1.generation(output1, tool_execution)
output_generation1.add_attributes({"provone:hadOutport": output_port})
output_generation2 = d1.generation(output2, tool_execution)
output_generation2.add_attributes({"provone:hadOutport": output_port})

log_generation = d1.generation(output_log, tool_execution)

# d1.serialize("test-provone-json.json", format="json")
d1.serialize("test-provone-ld.jsonld", format="rdf", rdf_format="json-ld")
d1.serialize('test-provone-rdf.ttl', format='rdf', rdf_format='ttl')

# dot.write_png('provone-example.png')
