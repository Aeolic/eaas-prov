import datetime
import json
import sys
import tarfile
from os import listdir

import requests
from nidm.core.provone import *
from prov.constants import PROV_TYPE
from prov.identifier import Namespace
from main import prefixedString, EAAS


def download_blob(blobstore_url, ):
    print("Downloading inputs from", blobstore_url)
    blobstore_response = requests.get(blobstore_url)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tar_path = "input_files_prov.tgz"
        with open(tar_path, "wb") as f:
            f.write(blobstore_response.content)

        with tarfile.open(tar_path, "r:gz") as zip_ref:
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(zip_ref, path=tmp_dir)

        f = []
        for root, dirs, files in os.walk(tmp_dir):
            f.extend(files)
        print("Input:", f)
        return f


def handle_outputs(blobstore_url, work_dir="/"):
    print("Downloading outputs from", blobstore_url)
    blobstore_response = requests.get(blobstore_url)

    with tempfile.TemporaryDirectory() as tmp_dir2:
        tar_path = "output_files_prov.tgz"
        with open(tar_path, "wb") as f:
            f.write(blobstore_response.content)

        with tarfile.open(tar_path, "r:gz") as zip_ref:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(zip_ref, path=tmp_dir2)

        # TODO use CWL glob if provided?
        # TODO add work dir
        print("Handling outputs from:", tmp_dir2)
        files = [f for f in listdir(tmp_dir2) if os.path.isfile(os.path.join(tmp_dir2, f))]
        print("Output:", files)
        return files


def main():

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
    env_os = env["os"]
    title = env["title"]
    description = env["description"]

    author = creation["userId"]
    createdAt = creation["createdAt"]

    digest = container["digest"]
    tag = container["tag"]
    containerUrl = container["containerUrl"]

    # execution data
    # for i in range(len(sys.argv) - 2):
    #     with open(sys.argv[i + 2]) as exec_file:
    #         execution_data = json.load(exec_file)
    #
    with open((sys.argv[2])) as exec_file:
        execution_data = json.load(exec_file)

    output_dir = sys.argv[3]

    startedAt = execution_data["startedAt"]
    endedAt = datetime.datetime.now()
    # execution_data["endedAt"]
    # inputFolder = execution_data["inputFolder"]
    # outputFolder = execution_data["outputFolder"]

    inputBlobstoreURL = download_blob(execution_data["inputBlobstoreURL"])
    outPutDir = handle_outputs(output_dir)
    user = execution_data["user"]

    # tool provenance
    print("Validated input data, creating tool provenance")
    original = d1.process(":originalTool", {":digest": digest, ":url": containerUrl, ":tag": tag,
                                            prefixedString("dcterms", "date"): createdAt})

    tool = d1.process("eaas:tool", {"dcterms:title": title, "dcterms:description": description})

    author = d1.user(":author", {"foaf:givenName": author})
    tool.wasAttributedTo(author)
    tool.wasDerivedFrom(original)

    environment = d1.entity("eaas:environment",
                            {prefixedString(EAAS, "envId"): environmentId,
                             prefixedString(EAAS, "os"): env_os,
                             prefixedString("dcterms", "date"): createdAt})
    print("Creating execution provenance")

    # execution provenance

    input_port = d1.input_port("eaas:input")  # , {":inputFolder": inputFolder})
    output_port = d1.output_port("eaas:output")  # , {":outputFolder": outputFolder})

    d1.has_out_ports(tool, output_port)
    d1.has_in_ports(tool, input_port)

    tool_execution = d1.processExec("eaas:exec", startTime=startedAt, endTime=endedAt)

    logged_in_user = d1.user(":" + user)

    tool_execution.used(environment)
    tool_execution.wasAssociatedWith(logged_in_user)
    # asso = d1.association(tool_execution,)
    # asso.add_attributes({"provone:hadPlan" : tool})

    for i, inp_file in enumerate(inputBlobstoreURL):
        inp = d1.data(":input{0}".format(i + 1),
                      [(PROV_TYPE, WFPROV["Artifact"]), (PROV_TYPE, WF4EVER["File"])])

        root, extension = os.path.splitext(inp_file)
        inp.add_attributes({"cwlprov:basename": inp_file,
                            "cwlprov:nameroot": root,
                            "cwlprov:nameext": extension})
        tool_execution.used(inp)
        input_usage = d1.usage(tool_execution, inp)
        input_usage.add_attributes({"provone:hadInPort": input_port})

    for o, out_file in enumerate(outPutDir):
        out = d1.data(":output{0}".format(o + 1),
                      [(PROV_TYPE, WFPROV["Artifact"]), (PROV_TYPE, WF4EVER["File"])])

        root, extension = os.path.splitext(out_file)
        out.add_attributes({"cwlprov:basename": out_file,
                            "cwlprov:nameroot": root,
                            "cwlprov:nameext": extension})
        tool_execution.used(out)
        output_generation = d1.generation(out, tool_execution)
        output_generation.add_attributes({"provone:hadOutport": output_port})

    # TODO PRONOM
    print("Writing to file:", "{0}_provone.jsonld".format(environmentId))
    # d1.serialize("test-provone-json.json", format="json")
    d1.serialize("{0}_provone.jsonld".format(environmentId), format="rdf", rdf_format="json-ld")
    d1.serialize("{0}_provone.ttl".format(environmentId), format='rdf', rdf_format='ttl')


    # dot.write_png('provone-example.png')





if __name__ == '__main__':
    # download_blob(
    #     'https://historic-builds.emulation.cloud:443/blobstore/api/v1/blobs/user-upload/a606bf91-38f8-4456-bd88-0137136b8bd7?access_token=default')
    # handle_outputs("test")
    main()