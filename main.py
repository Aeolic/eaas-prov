import datetime
import json
import os
import sys

import prov
from prov.model import ProvDocument
# from prov.dot import prov_to_dot


def prefixedString(prefix, string):
    return prefix + ":" + string


def addFilesToCollection(collection, files):
    for file in files:
        filename = file["filename"]
        root, extension = os.path.splitext(filename)

        collection.hadMember(prefixedString(ID, filename))

        output1 = d1.entity(prefixedString(ID, filename),
                            [("prov:type", "wfprov:Artifact"), ("prov:type", "wf4ever:File")])

        output1.add_attributes({"cwlprov:basename": filename,
                                "cwlprov:nameroot": root,
                                "cwlprov:nameext": extension})



ID = "id"
EAAS = "eaas"

if __name__ == '__main__':
    # my_prov = prov.read(
    #     "E:\Thesis\CwlEnvironmentStarter\prov\metadata\provenance\primary.cwlprov.json")
    #
    # dot = prov_to_dot(my_prov)
    # dot.write_png('example-prov.png')

    #
    #
    # rdf = ProvRDFSerializer(my_prov)
    #
    # with open("test.ttl", mode ="w") as f:
    #     rdf.serialize(stream=f)

    # url = "E:\Thesis\workingProv\metadata\provenance\primary.cwlprov.ttl"

    d1 = ProvDocument()
    # d1.add_namespace('now', 'http://www.provbook.org/nownews/')
    # d1.add_namespace('nowpeople', 'http://www.provbook.org/nownews/people/')
    # d1.add_namespace('bk', 'http://www.provbook.org/ns/#')
    #
    # # Entity: now:employment-article-v1.html
    # e1 = d1.entity('now:employment-article-v1.html')
    # # Agent: nowpeople:Bob
    # d1.agent('nowpeople:Bob')
    #
    # d1.wasAttributedTo(e1, 'nowpeople:Bob')
    #
    # # add more namespace declarations
    # d1.add_namespace('govftp', 'ftp://ftp.bls.gov/pub/special.requests/oes/')
    # d1.add_namespace('void', 'http://vocab.deri.ie/void#')
    #
    # # 'now:employment-article-v1.html' was derived from at dataset at govftp
    # d1.entity('govftp:oesm11st.zip',
    #           {'prov:label': 'employment-stats-2011', 'prov:type': 'void:Dataset'})
    # d1.wasDerivedFrom('now:employment-article-v1.html', 'govftp:oesm11st.zip')
    #
    # # Adding an activity
    # d1.add_namespace('is', 'http://www.provbook.org/nownews/is/#')
    # d1.activity('is:writeArticle')
    #
    # # Usage and Generation
    # d1.used('is:writeArticle', 'govftp:oesm11st.zip')
    # d1.wasGeneratedBy('now:employment-article-v1.html', 'is:writeArticle')

    # print(d1.get_provn())

    #

    """
    eaas:
    
    version: version of eaas-backend running
    envId: the envId of an environement
    original: a link to the original tool (if exists)
    workflow: a link to one/multiple workflows where the tool is used
    os: operating system that is used in an environment
    """

    with open(sys.argv[1]) as json_file:
        fileFromBackend = json.load(json_file)
        print(fileFromBackend)

    file_environment = fileFromBackend["environment"]
    user = fileFromBackend["user"]
    file_input = fileFromBackend["input"]
    file_output = fileFromBackend["output"]
    metadata = fileFromBackend["metadata"]
    other = fileFromBackend["other"]

    d1.add_namespace('eaas', 'whatever')
    d1.add_namespace('foaf', 'http://www.w3.org/ns/prov#')
    d1.add_namespace("wf4ever", "http://purl.org/wf4ever/wf4ever#")
    d1.add_namespace("id", "stringIds")
    d1.add_namespace("cwlprov", "https://w3id.org/cwl/prov#")
    d1.add_namespace("wfdesc", "http://purl.org/wf4ever/wfdesc#")

    user = d1.agent(prefixedString(ID, user["userId"]), {"foaf:mbox": user["userMail"]})

    tool = d1.entity("id:myEmulatedTool",
                     {"prov:type": "wfdesc:Process", "wfdesc:hasInput": "id:inputs",
                      "wfdesc:hasOutput": "id:outputs", "eaas:original": metadata["original"]})

    eaas_server = d1.entity("id:eaas-server",
                            {prefixedString(EAAS, "version"): other["eaasVersion"]})
    environment = d1.entity("id:environment",
                            {prefixedString(EAAS, "envId"): file_environment["environmentId"],
                             prefixedString(EAAS, "os"): file_environment["os"]})

    # TODO enable revision stuff

    tool.wasAttributedTo(user)

    emulation_activity = d1.activity("id:myEmulatedToolStorage")
    emulation_activity.wasStartedBy(tool, starter=user, time=datetime.datetime.now())

    tool.wasGeneratedBy(emulation_activity)

    emulation_activity.used(eaas_server)
    emulation_activity.used(environment)
    emulation_activity.used("id:inputs")
    emulation_activity.used("id:outputs")

    inputs = d1.collection("id:inputs")
    outputs = d1.collection("id:outputs")

    addFilesToCollection(inputs, file_input)
    addFilesToCollection(outputs, file_output)

    # for inp_file in file_input:
    #     filename = inp_file["filename"]
    #     root, extension = os.path.splitext(filename)
    #     inputs.hadMember(prefixedString(ID, filename))
    #
    #     input1 = d1.entity(prefixedString(ID, filename),
    #                        [("prov:type", "wfprov:Artifact"), ("prov:type", "wf4ever:File")])
    #
    #     input1.add_attributes({"cwlprov:basename": filename,
    #                            "cwlprov:nameroot": root,
    #                            "cwlprov:nameext": inputs})
    #
    # outputs = d1.collection("id:outputs")
    #
    # for out_file in file_output:
    #     filename = out_file["filename"]
    #     root, extension = os.path.splitext(filename)
    #
    #     outputs.hadMember(prefixedString(ID, filename))
    #
    #     output1 = d1.entity(prefixedString(ID, filename),
    #                         [("prov:type", "wfprov:Artifact"), ("prov:type", "wf4ever:File")])
    #
    #     output1.add_attributes({"cwlprov:basename": filename,
    #                             "cwlprov:nameroot": root,
    #                             "cwlprov:nameext": extension})



    """
    Agent (Nutzer)
    Agent (SoftwareAgent) ?
    Time (Zeitpunkt des Speicherns der Umgebung)
    Input type(s)
    Output type(s)
    Betriebssystem + Architektur Details (insofern möglich)
    Abhängigkeiten (was genau sind Abhängigkeiten + wie komme ich daran?)
    Emulator Version
    EAAS Backend-Version
    Version der Environment
    Metadata: Tags etc, vom Nutzer angegeben
    
    Referenz zum "Original" wenn vorhanden
    Referenz zu etwaigen Workflows, die das Tool beinhalten
    
    + zusätzliche nützliche Infos, die ich vllt noch finde :)
    
    ---
    Eventuell: Beispiel Execution für genau dieses Tool:
    Agent, Time started, Time ended, input Artifacts, output Artifacts, etc.
    
    """

    # d1.serialize('article-prov.ttl', format='rdf', rdf_format='ttl')
    d1.serialize("test-prov.json", format="json");

    # dot = prov_to_dot(d1)
    # dot.write_png('article-prov.png')


