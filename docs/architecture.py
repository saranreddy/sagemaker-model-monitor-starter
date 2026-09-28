"""Architecture diagram for saranreddy/sagemaker-model-monitor-starter.

Verified against main @ 551dd9c. Every node maps to infra/*.tf or scripts/*.py.

Render:  pip install diagrams   (also needs Graphviz: apt install graphviz / brew install graphviz)
         python docs/architecture.py   ->  docs/architecture.png (written next to this script)
"""
import os

from diagrams import Cluster, Diagram, Edge, getdiagram
from diagrams.aws.compute import EC2ContainerRegistryImage
from diagrams.aws.general import User, Users
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Sagemaker
from diagrams.aws.security import IAMRole
from diagrams.aws.storage import SimpleStorageServiceS3Bucket, SimpleStorageServiceS3BucketWithObjects
from diagrams.onprem.iac import Terraform
from diagrams.programming.language import Python

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "architecture")  # -> architecture.png next to this script

FONT = "DejaVu Sans"
GRAPH = {
    "fontname": FONT, "fontsize": "34", "labelloc": "t", "pad": "0.4",
    "nodesep": "0.4", "ranksep": "1.0", "splines": "spline", "newrank": "true",
    "compound": "true",
}
NODE = {"fontname": FONT, "fontsize": "21", "imagepos": "tc"}
EDGE = {"fontname": FONT, "fontsize": "19", "color": "#555555",
        # enter/leave icons at mid-height so arrowheads never land on label text
        "tailport": "e", "headport": "w"}

# diagrams.Edge hard-codes a 13pt label font on every edge; raise it so edge labels stay
# readable when the PNG is scaled down to README width.
Edge._default_edge_attrs = {"fontcolor": "#2D3436", "fontname": FONT, "fontsize": "19"}


def box(bg, pen, style="rounded"):
    return {"bgcolor": bg, "pencolor": pen, "fontname": FONT, "fontsize": "21",
            "style": style, "labeljust": "l", "margin": "24"}


TF_BOX = box("#fff4e0", "#e66100")                  # deployed by Terraform
SUB_BOX = box("#fffaf2", "#e66100")                 # sub-group inside a Terraform box
RUN_BOX = box("#e8f1fb", "#1a5fb4")                 # created by scripts / CLI
EXEC_BOX = box("#f3eefa", "#613583")                # per execution / runtime
MANAGED_BOX = box("#f6f5f4", "#9a9996", "dashed")   # not created by this repo
ACCOUNT_BOX = box("#ffffff", "#232f3e")

FLOW = dict(color="#1a5fb4", fontcolor="#1a5fb4", penwidth="2.2")
IO = dict(color="#26a269", fontcolor="#1e7d4f", penwidth="1.8")
IAM = dict(color="#c01c28", fontcolor="#c01c28", style="dashed", penwidth="1.6", constraint="false")
AUX = dict(color="#8a8a8a", fontcolor="#5e5c64", style="dotted", penwidth="1.8")
SETUP = dict(color="#e66100", fontcolor="#c64600", style="dashed", penwidth="1.8")
MANUAL = dict(color="#26a269", fontcolor="#1e7d4f", style="dashed", penwidth="2.2")
FAIL = dict(color="#c01c28", fontcolor="#c01c28", penwidth="2.2")
OPT = dict(color="#b5835a", fontcolor="#8f5f3a", style="dashed", penwidth="1.8")
HIDDEN = dict(style="invis")
DOWN = dict(tailport="s", headport="n")
UP = dict(tailport="n", headport="s")


def same_rank(*nodes):
    getdiagram().dot.body.append("{rank=same; " + " ".join(f'"{n._id}";' for n in nodes) + "}")


GRAPH["ranksep"] = "0.7"
GRAPH["pad"] = "0.8"

with Diagram(
    "sagemaker-model-monitor-starter",
    filename=OUT, outformat="png", show=False, direction="LR",
    graph_attr=GRAPH, node_attr=NODE, edge_attr=EDGE,
):
    eng = User("ML engineer")
    tf = Terraform("terraform apply\n(infra/)")
    base_py = Python("create_baseline.py")
    mon_py = Python("enable_monitoring.py\n(checks endpoint\nis InService)")

    with Cluster("AWS account  (default us-east-1)", graph_attr=ACCOUNT_BOX):
        with Cluster("Deployed by Terraform", graph_attr=TF_BOX):
            bucket = SimpleStorageServiceS3Bucket("Monitor bucket\n(holds the\nprefixes below)")
            role = IAMRole("SageMaker\nexecution role")

        with Cluster("Existing endpoint (not created by this repo)", graph_attr=MANAGED_BOX):
            client = Users("Inference\nclients")
            endpoint = Sagemaker("SageMaker\nendpoint")
            capture = SimpleStorageServiceS3BucketWithObjects("Captured data\n(S3 path set in the\nendpoint config;\nenabled manually)")

        with Cluster("Created by create_baseline.py", graph_attr=RUN_BOX):
            base_csv = SimpleStorageServiceS3BucketWithObjects("baseline/\nbaseline.csv")
            base_job = Sagemaker("Baseline job\nsuggest_baseline")
            base_res = SimpleStorageServiceS3BucketWithObjects("baseline-results/\nstatistics +\nconstraints")

        with Cluster("Created by enable_monitoring.py", graph_attr=EXEC_BOX):
            schedule = Sagemaker("Monitoring schedule\nhousing-data-\nquality-monitor\nhourly")
            mon_job = Sagemaker("Monitoring job\n(each run)")
            results = SimpleStorageServiceS3BucketWithObjects("monitoring-results/\nviolations")

        with Cluster("AWS-managed", graph_attr=MANAGED_BOX):
            ecr = EC2ContainerRegistryImage("Model Monitor\nanalyzer image\n(both jobs)")
            cw = Cloudwatch("CloudWatch\nlogs + metrics")

    check_py = Python("check_violations\n.py (prints report)")
    reviewer = User("ML engineer\n(review)")

    eng >> Edge(label="deploy", **SETUP) >> tf
    tf >> Edge(**SETUP) >> role
    tf >> Edge(**SETUP) >> bucket
    eng >> Edge(label="1. run", **FLOW) >> base_py
    eng >> Edge(label="2. run", **FLOW) >> mon_py

    base_py >> Edge(label="upload", weight="5", **IO) >> base_csv
    base_csv >> Edge(weight="5", **IO) >> base_job
    base_job >> Edge(label="writes", weight="5", **IO) >> base_res

    mon_py >> Edge(label="create", weight="5", **FLOW) >> schedule
    schedule >> Edge(label="starts", weight="5", **FLOW) >> mon_job
    mon_job >> Edge(label="writes", weight="5", **IO) >> results
    base_res >> Edge(label="baseline", **IO) >> mon_job

    client >> Edge(label="requests", weight="5", **FLOW) >> endpoint
    endpoint >> Edge(label="captures", weight="5", **IO) >> capture
    capture >> Edge(label="input", **IO) >> mon_job

    results >> Edge(label="reads", **FLOW) >> check_py
    reviewer >> Edge(label="3. run", **DOWN, **MANUAL) >> check_py
    same_rank(check_py, reviewer)

    # keep the two script nodes stacked in lane order (baseline above monitoring)
    same_rank(base_py, mon_py)
    base_py >> Edge(**HIDDEN) >> mon_py
    role >> Edge(label="assumed by jobs", headport="n", **IAM) >> base_job
    schedule >> Edge(**HIDDEN) >> ecr
    mon_job >> Edge(tailport="s", headport="n", **AUX) >> cw
