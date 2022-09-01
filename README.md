# Agile Summit 2022

Sample code comes from [Azure Machine Learning Python SDK v2 (preview)](https://github.com/Azure/azureml-examples/blob/sdk-preview/sdk/jobs/single-step/lightgbm/iris/src/main.py).

Training data comes from [Iris in Azure Example Datasets](https://azuremlexamples.blob.core.windows.net/datasets/iris.csv). 

三個範例是在模擬一個情境：

- 第一階段先在 Local Machine 開發實作，所以不需要 Driver Program (就只是一行執行 Python 的指令)，在 Local Machine 建置 Environment，執行 Training Program 進行訓練。

- 第二階段是把整個實作搬到 Azure Machine Learning Workspace，但是假裝不熟 Python SDK v2 + MLflow，所以在 Compute Instance 建置 Python SDK v2 + MLflow 環境，用互動式的 Jupyter Notebook 撰寫 Driver Program，把 Training Program 送到 Curated Environment 進行訓練。

- 第三階段就是把整個實作放到 Azure DevOps，Source Code 用 Repository 控管，然後把 Jupyter Notebook 的內容分成兩半，前半段變成 Bash Task 建置跟剛剛 Compute Instance 一樣環境 (因為要跑 Driver Program)，後半段就變成新的 Driver Program 讓 Azure CLI Task 執行。

以後習慣了，就可以省掉第二階段，第一階段之後就是第三階段。 
