import datetime

import prov
from nidm.core.provone import *
from prov.constants import PROV_TYPE
from prov.dot import prov_to_dot
from prov.identifier import Namespace

from main import prefixedString, EAAS

d1 = ProvONEDocument()

WFDESC = Namespace("wfdesc", "http://purl.org/wf4ever/wfdesc#")
WFPROV = Namespace("wfprov", "http://purl.org/wf4ever/wfprov#")
WF4EVER = Namespace("wf4ever", "http://purl.org/wf4ever/wf4ever#")

d1.add_namespace('eaas', 'eaas#')
d1.add_namespace('prov', 'http://www.w3.org/ns/prov#')
d1.add_namespace("dcterms", "http://purl.org/dc/terms#")
d1.add_namespace("cwlprov", "https://w3id.org/cwl/prov#")
d1.add_namespace("wfprov", "http://purl.org/wf4ever/wfprov#")
d1.add_namespace("wfdesc", "http://purl.org/wf4ever/wfdesc#")
d1.add_namespace("wf4ever", "http://purl.org/wf4ever/wf4ever#")

tool = d1.process("eaas:tool", {"dcterms:title": "My emulated tool" })

author = d1.user("eaas:user")
tool.wasAttributedTo(author)

input_port = d1.input_port("eaas:input")
output_port = d1.output_port("eaas:output")

d1.has_in_ports(tool, input_port)
d1.has_out_ports(tool, output_port)

environment = d1.entity("eaas:environment",
                        {prefixedString(EAAS, "envId"): "90825a58-b795-4002-87e3-8c0b308fbcb2",
                         prefixedString(EAAS, "os"): "ubuntu",
                         prefixedString("dcterms", "date"): "2021-06-29"})

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

# d1.serialize("test-provone""-json.json", format="json")
d1.serialize("test-provone-ld.jsonld", format="rdf", rdf_format="json-ld")
d1.serialize('test-provone-rdf.ttl', format='rdf', rdf_format='ttl')

# dot.write_png('provone-example.png')
