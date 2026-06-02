# acr.tf:コンテナレジストリ
# プロジェクト共通のリソースグループを作成
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# コンテナレジストリの定義
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Standard"
  admin_enabled       = true
}
