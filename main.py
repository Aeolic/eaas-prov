import datetime
import prov
from prov.dot import prov_to_dot

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

    d1 = prov.model.ProvDocument()
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

    d1.add_namespace('eaas', 'whatever')
    d1.add_namespace('foaf', 'http://www.w3.org/ns/prov#')
    d1.add_namespace("wf4ever", "http://purl.org/wf4ever/wf4ever#")
    d1.add_namespace("id", "stringIds")
    d1.add_namespace("cwlprov", "https://w3id.org/cwl/prov#")
    d1.add_namespace("wfdesc", "http://purl.org/wf4ever/wfdesc#")

    d1.agent("id:eeasUserId", {"foaf:mbox": "abc@def.com"})

    d1.entity("id:myEmulatedTool",
              {"prov:type": "wfdesc:Process", "wfdesc:hasInput": "id:inputs",
               "wfdesc:hasOutput": "id:outputs", "eaas:original": "originaltool.com"})

    d1.entity("id:eaas-server", {"eaas:version": "v1.0.0"})
    d1.entity("id:environment", {"eaas:envId": "eaasEnvironmentId", "eaas:os": "Linux Debian 9"})

    # TODO enable revision stuff

    d1.wasAttributedTo("id:myEmulatedTool", "id:eeasUserId")

    emulation_activity = d1.activity("id:myEmulatedToolStorage")
    d1.wasStartedBy("id:myEmulatedToolStorage", starter="id:eeasUserId",
                    time=datetime.datetime.now())

    emulation_activity.used("id:eaas-server")
    emulation_activity.used("id:environment")
    emulation_activity.used("id:inputs")
    emulation_activity.used("id:outputs")

    d1.wasGeneratedBy("id:myEmulatedTool", "id:myEmulatedToolStorage")

    inputs = d1.collection("id:inputs")
    inputs.hadMember("id:Input")

    input1 = d1.entity("id:Input",
                       [("prov:type", "wfprov:Artifact"), ("prov:type", "wf4ever:File")])

    input1.add_attributes({"cwlprov:basename": "input.txt",
                           "cwlprov:nameroot": "input",
                           "cwlprov:nameext": ".txt"})

    outputs = d1.collection("id:outputs")
    outputs.hadMember("id:Output")

    output1 = d1.entity("id:Output",
                        [("prov:type", "wfprov:Artifact"), ("prov:type", "wf4ever:File")])

    output1.add_attributes({"cwlprov:basename": "output.txt",
                            "cwlprov:nameroot": "output",
                            "cwlprov:nameext": ".txt"})

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
