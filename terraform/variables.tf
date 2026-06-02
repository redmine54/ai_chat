variable "resource_group_name" {
  type        = string
  default     = "chatapp-resources"
  description = "すべてのリソースを配置するAzureリソースグループの名前"
}

variable "location" {
  type        = string
  default     = "japaneast"
  description = "リソースを物理的に配置するAzureの地域（東日本）"
}

variable "acr_name" {
  type        = string
  default     = "chatappregistry2026"
  description = "Dockerイメージを保存するAzureコンテナレジストリの名前"
}

variable "key_vault_name" {
  type        = string
  default     = "chatapp-kv-2026"
  description = "シークレット情報を管理するAzure Key Vaultの名前"
}

variable "aks_cluster_name" {
  type        = string
  default     = "chatapp-aks-cluster"
  description = "Azure Kubernetes Service クラスターの名前"
}

variable "aks_vm_size" {
  type        = string
  default     = "Standard_D2s_v5"
  description = "AKSノードに使用する仮想マシンのサイズ"
}

variable "aks_node_count" {
  type        = number
  default     = 2
  description = "AKSクラスター起動時の初期ノード（サーバー）台数"
}
