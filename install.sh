#!/bin/bash
pip uninstall azure-ai-ml --yes
pip install --pre azure-ai-ml
pip install mlflow azureml-mlflow