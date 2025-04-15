@description('Localização dos recursos')
param location string = 'westeurope'

@description('Nome do Resource Group')
param resourceGroupName string = 'rg-my-aks'

@description('Nome do AKS cluster')
param aksName string = 'myAKSCluster'

@description('Nome do ACR')
param acrName string = 'myContainerRegistry'

resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

resource aks 'Microsoft.ContainerService/managedClusters@2023-01-01' = {
  name: aksName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: '${aksName}-dns'
    agentPoolProfiles: [
      {
        name: 'nodepool1'
        count: 2
        vmSize: 'Standard_DS2_v2'
        mode: 'System'
        osType: 'Linux'
        type: 'VirtualMachineScaleSets'
      }
    ]
    linuxProfile: {
      adminUsername: 'azureuser'
      ssh: {
        publicKeys: [
          {
            keyData: 'ssh-rsa AAAA... tua SSH key ...'
          }
        ]
      }
    }
    networkProfile: {
      networkPlugin: 'azure'
    }
    addonProfiles: {}
    enableRBAC: true
    aadProfile: {
      managed: true
    }
  }
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2020-10-01-preview' = {
  name: guid(aks.id, 'acrpull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: aks.identity.principalId
    principalType: 'ServicePrincipal'
  }
}
