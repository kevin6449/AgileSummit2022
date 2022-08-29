# Import required classes and functions
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
# Machine Learning Workspace
from azure.ai.ml import MLClient
# Compute Target
from azure.ai.ml.entities import AmlCompute
# Command and Arguments
from azure.ai.ml import command, Input
# MLflow Support
import mlflow
# Model
from azure.ai.ml.entities import Model

# Get the credential
try:
    credential = DefaultAzureCredential()
    # Check if given credential can get token successfully.
    credential.get_token("https://management.azure.com/.default")
except Exception as ex:
    # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
    # This will open a browser page for
    credential = InteractiveBrowserCredential()

# Get a handle to the workspace
ml_client = MLClient(
    credential=credential,
    subscription_id="<<SUBSCRIPTION_ID>>",
    resource_group_name="RESOURCE_GROUP_NAME",
    workspace_name="MACHINE_LEARNING_WORKSPACE_NAME"
)
print(ml_client)

# Get the compute target
compute_target_name = "ComputeClusterDemo"

try:
    # Check if the compute target already exists
    compute_target = ml_client.compute.get(compute_target_name)
    print(f"{compute_target.name} of node size {compute_target.size} is reused.")
except Exception:
    compute_target = AmlCompute(
        name=compute_target_name,
        type="amlcompute",
        size="Standard_DS3_v2",
        min_instances=0,
        max_instances=1,
        idle_time_before_scale_down=120,
        tier="Dedicated"
    )
    compute_target = ml_client.begin_create_or_update(compute_target)
    print(f"{compute_target.name} of node size {compute_target.size} is created.")

# Define the command
experiment_name = "AgileSummit2022"

command_job = command(
    experiment_name=experiment_name,
    code="./src",
    command="python main.py --iris-csv ${{inputs.csv}} --learning-rate ${{inputs.rate}} --boosting ${{inputs.boost}}",
    environment="AzureML-lightgbm-3.2-ubuntu18.04-py37-cpu@latest",
    inputs={
        "csv": Input(
            type="uri_file",
            path="https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
        ),
        "rate": 0.9,
        "boost": "gbdt",
    },
    compute="ComputeClusterDemo",
)

# Enable logging
mlflow.autolog()

# Submit the command
returned_job = ml_client.jobs.create_or_update(command_job)
print("Job name:", returned_job.name)

# Get a URL for the status of the job
print("Job url:", returned_job.services["Studio"].endpoint)

# Find the model path
job_path = f"azureml://jobs/{returned_job.name}/outputs/artifacts/paths/model/"
print("Job path:", job_path) 

# Register the model
import time

while True: 
    status = mlflow.get_run(returned_job.name).info.status
    print("Job status:", status)
    if status == "FINISHED":
        break
    else:
        time.sleep(5)

run_model = Model(
    path=job_path,
    name="IrisModel",
    description=f"Model created from experiment {experiment_name} run {returned_job.name}.",
    type="mlflow_model"
)
ml_client.models.create_or_update(run_model) 
