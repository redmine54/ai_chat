# 1. Terraform本体と利用するプラグイン（Provider）のバージョンを指定
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0" # 安定版の3.x系を使用
    }
  }
}

# 2. Azureプロバイダーの動作設定（featuresは必須の空ブロックです）
provider "azurerm" {
  features {}
}
