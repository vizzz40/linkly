# terraform

Provisions the Azure side: a resource group, an ACR (Basic), and an AKS cluster,
plus the AcrPull role so AKS can pull from the registry. State lives in an Azure
storage account.

This costs money while it's running (~$2-3/day for one small node), so run
`terraform destroy` when you're done.

## setup

The remote state needs a storage account to exist first:

    az group create -n tfstate-rg -l germanywestcentral
    az storage account create -n linklytfstate1234 -g tfstate-rg --sku Standard_LRS
    az storage container create -n tfstate --account-name linklytfstate1234

Storage account names are global, so use your own and put it in backend.hcl.

## use

    cp backend.hcl.example backend.hcl
    cp terraform.tfvars.example terraform.tfvars
    terraform init -backend-config=backend.hcl
    terraform plan
    terraform apply

Then point kubectl at the cluster:

    az aks get-credentials -g linkly-rg -n linkly-aks

## teardown

    terraform destroy
