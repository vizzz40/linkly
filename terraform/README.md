# Terraform - Azure infrastructure

Provisions the cloud side of the project:

- a resource group
- an Azure Container Registry (Basic)
- an AKS cluster (single small node pool)
- an `AcrPull` role assignment so AKS can pull images from the registry

State is kept in an Azure Storage account (remote backend) so it isn't sitting
on one laptop.

## Cost

This spends real money while it's up. With a single `Standard_B2s` node it's
roughly **$2-3/day**, which fits inside the $100 Azure free credit for a good
while. Always run `terraform destroy` when you're done demoing.

## One-time bootstrap (remote state)

The backend needs a storage account to exist *before* `terraform init`. Create
it once:

```bash
az group create --name tfstate-rg --location westeurope

az storage account create \
  --name linklytfstate1234 \
  --resource-group tfstate-rg \
  --sku Standard_LRS

az storage container create \
  --name tfstate \
  --account-name linklytfstate1234
```

Storage account names are globally unique, so change `linklytfstate1234` to
something of your own and update `backend.hcl` to match.

## Usage

```bash
cp backend.hcl.example backend.hcl          # edit the storage account name
cp terraform.tfvars.example terraform.tfvars # change prefix if "linklyacr" is taken

terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

Then point kubectl at the new cluster (the exact command is in the output):

```bash
$(terraform output -raw get_credentials_command)
```

## Teardown

```bash
terraform destroy
```
