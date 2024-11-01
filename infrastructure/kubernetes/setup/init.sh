#!/bin/bash

kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl apply -f "$(cd "$(dirname "${BASH_SOURCE[0]}")/../argo/application-set.yaml" && pwd)"
