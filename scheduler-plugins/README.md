# Scheduler-Plugins con EnergyScore

Este directorio contiene el **plugin EnergyScore** y los parches necesarios para integrarlo en el proyecto oficial de Kubernetes Scheduler-Plugins.

## Uso

1. Clonar el repo oficial:
   ```bash
   git clone https://github.com/kubernetes-sigs/scheduler-plugins.git
   cd scheduler-plugins
2. Copiar el plugin de energy score en el nuevo pkg:
   ```bash
   cp -r ../Research-Project-Energy-Consumption/scheduler-plugins/pkg/energyscore pkg/
4. Aplicar los parches:
   ```bash
   git apply ../Research-Project-Energy-Consumption/scheduler-plugins/patches/*.patch
6. Copiar las configuraciones:
   ```bash
   cp ../Research-Project-Energy-Consumption/scheduler-plugins/configs/*.yaml ./config/
8. Compilar:
   ```bash
   make build
