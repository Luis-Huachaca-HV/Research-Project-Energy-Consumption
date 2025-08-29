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


### 1. Instala Go (si no lo tienes actualizado)

```bash
sudo apt update
sudo apt install golang-go -y
```

(O mejor descarga desde [https://go.dev/dl/](https://go.dev/dl/) para tener la última versión).

---

### 2. Limpia dependencias y descarga módulos

Desde la raíz de `scheduler-plugins`:

```bash
go mod tidy
```

---

### 3. Compila el scheduler

```bash
make build
```

Esto generará el binario del scheduler en:

```
_bin/kube-scheduler
```

---

### 4. Ejecuta tu scheduler modificado

Puedes probarlo en tu cluster (por ejemplo, kind o minikube).
Ejemplo de ejecución:

```bash
_bin/kube-scheduler --config energy-score-config.yaml --v=4
```

---

Notas importantes:

* Tus cambios en `apis/config/v1/...` y en `pkg/energyscore/` agregan **nuevos tipos y lógica de plugin** → asegúrate de que el `energy-score-config.yaml` que creaste apunte a tu plugin dentro de `pkg/energyscore/`.
* Si falla el `make build` por falta de herramientas de código generado (como deepcopy, conversion, defaults), se suele regenerar con:

  ```bash
  make update
  ```

  (esto corre `hack/update-codegen.sh` para que los `zz_generated.*.go` queden bien).

---


2. Compila tu scheduler modificado
```
cd scheduler-plugins
make build
```

Esto generará el binario en _bin/kube-scheduler.

3. Lanza el scheduler con tu config

Ejecuta (en una terminal separada):
```
_bin/kube-scheduler --config /ruta/a/energy-score-config.yaml --v=4
```

Notas:

--config debe apuntar a tu YAML.

--v=4 te da logs de depuración (útil para ver si carga EnergyScore).

Este scheduler correrá en tu host conectado al cluster, y usará el nombre energy-scheduler.

4. Usa tu scheduler en Pods

Crea un pod de prueba (test-pod.yaml) con:

Aplica:

kubectl apply -f energy_test.yaml
