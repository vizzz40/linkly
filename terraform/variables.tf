variable "prefix" {
  type        = string
  default     = "linkly"
  description = "Name prefix for all resources. Must be globally unique for ACR."
}

variable "location" {
  type        = string
  default     = "germanywestcentral"
  description = "Azure region to deploy into."
}

variable "node_count" {
  type        = number
  default     = 1
  description = "Number of nodes in the AKS default pool."
}

variable "node_size" {
  type        = string
  default     = "Standard_F2as_v6"
  description = "VM size for AKS nodes."
}

variable "kubernetes_version" {
  type        = string
  default     = null
  description = "AKS version. null lets Azure pick the default."
}
