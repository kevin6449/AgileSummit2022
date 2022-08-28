# Credentials
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
# Machine Learning Workspace
from azure.ai.ml import MLClient
# Compute Target
from azure.ai.ml.entities import AmlCompute
# Command and Arguments
from azure.ai.ml import command, Input

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
    subscription_id="630fbb67-7809-49f9-af9c-55704307b953",
    resource_group_name="RG_MachineLearning",
    workspace_name="mlaiws"
)
print(ml_client)

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
command_job = command(
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

# Submit the command
returned_job = ml_client.jobs.create_or_update(command_job)
# Get a URL for the status of the job
print(returned_job.services["Studio"].endpoint)
