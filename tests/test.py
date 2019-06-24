'''
    This script runs clusterside locally printing all output to the command
    line (instead of to the PlantIT server).

    It assumes irods is setup using iinit and the sample paths in the
    sample_file dictionary exist on the irods server.
'''

from clusterside.executors import SingleJobExecutor
from clusterside.data import Collection, Workflow
from clusterside.comms import STDOUTComms

process_file = '''
def process_sample(name,path,args):
    from pathlib import Path
    Path('a_really_awecsome_file.txt').touch()
    return {
        'key-val': {'name': name, 'path': path}
    }
'''

sample_file = '''
{
    "name": "TestCollection",
    "storage_type": "irods",
    "base_file_path": "/tempZone/home/rods/",
    "sample_set":{
    	"Sample1": {
    		"storage": "irods",
    		"path": "/tempZone/home/rods/24-74-2.png"
    	},
    	"Sample2": {
    		"storage": "irods",
    		"path": "/tempZone/home/rods/24-77-1.png"
    	},
    	"Sample3": {
    		"storage": "irods",
    		"path": "/tempZone/home/rods/24-9-2.png"
    	}
    }
}
'''

workflow_file = '''
{
	"server_url": "http://localhost/jobs/api/",
    "singularity_url": "shub://frederic-michaud/python3",
    "api_version": 0.1,
	"auth_token": "asdf",
	"job_pk": 2,
	"parameters": {},
    "pre_commands": ["singularity", "image.create", "{workdir}/file.img"],
    "singularity_flags": ["--overlay", "{workdir}/file.img"]
}
'''

with open("samples.json", "w") as fout:
    fout.write(sample_file)

with open("workflow.json", "w") as fout:
    fout.write(workflow_file)

with open("process.py", "w") as fout:
    fout.write(process_file)

collection = Collection("samples.json")
workflow = Workflow("workflow.json")
server = STDOUTComms()

executor = SingleJobExecutor(collection, workflow, server)
executor.process()
results_path = executor.reduce()

import os
from clusterside.data import upload_file

_, file_extension = os.path.splitext(results_path)
remote_results_path = os.path.join(collection.base_file_path,
                                   "results_job%d%s"%(workflow.job_pk,file_extension))
upload_file(results_path,remote_results_path)

server.update_job({'remote_results_path': remote_results_path})

server.task_complete(1)