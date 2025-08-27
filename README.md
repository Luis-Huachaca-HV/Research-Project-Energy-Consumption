# Research-Project-Energy-Consumption
Perfecto 🚀, ya entendí todo el flujo de tu experimento. Te armo un `README.md` bien organizado, con secciones claras, comandos listos para copiar y pegar, y explicación del proceso de principio a fin.

Aquí tienes el **README.md** para tu carpeta `DeathStarBench`:

````markdown
# DeathStarBench - Experimentos de Consumo Energético

Este repositorio contiene el despliegue y experimentación de **DeathStarBench**, con el microservicio **HotelReservation**, sobre un clúster de Kubernetes. El objetivo es medir el consumo energético de las aplicaciones mediante la integración con la herramienta **Ecofloc**.

---

## 1. Requisitos previos

Antes de ejecutar los experimentos, es necesario contar con un clúster Kubernetes configurado. Se recomienda usar **3 máquinas** (1 master + 2 workers).

### Instalación de Docker
Puedes instalar Docker en Ubuntu 22.04 siguiendo una de estas opciones:

- Opción 1 (Docker Desktop):  
  [Instalar Docker Desktop en Ubuntu](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)

- Opción 2 (recomendada):  
  [Instalar Docker + Docker Compose en Ubuntu 22.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04)

### Instalación de Kubernetes (kubeadm)
Sigue la guía oficial de Kubernetes para instalar `kubeadm`:  
[Instalar kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)

### Configuración del cluster
Puedes seguir este tutorial:  
[How to set up a Kubernetes cluster on Ubuntu 22.04](https://medium.com/@kvihanga/how-to-set-up-a-kubernetes-cluster-on-ubuntu-22-04-lts-433548d9a7d0)

Cuando el clúster esté listo, asegúrate de que los nodos estén disponibles:

```bash
kubectl get nodes
````

---

## 2. Verificación del despliegue

Una vez configurado el cluster, desplegar el servicio **HotelReservation**:

```bash
kubectl apply -Rf /home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes/
```

Espera \~10 segundos y verifica que los pods estén corriendo:

```bash
kubectl get pods
```

---

## 3. Configuración de Ecofloc (medición de energía)

El script `gepidsh.sh` se encarga de recolectar los PIDs de los procesos del cluster en cada nodo y configurarlos para Ecofloc.
Ejemplo de configuración dentro del script:

```bash
YAML_DIR="/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes"

remote_computers_list=("luish@luish-Aspire-A315-55G" "luish@luish-HP-Laptop-14-dq0xxx")
sudo_password="238244758"

declare -A remote_computers_map
remote_computers_map["luish@luish-Aspire-A315-55G"]="/home/luish/Documents/p3/ecofloc2/ecofloc"
remote_computers_map["luish-HP-Laptop-14-dq0xxx"]="/home/luish/Documents/p3/ecofloc"
```

Ejecuta:

```bash
./gepidsh.sh
```

Verifica que cada nodo tenga un archivo `.txt` con los PIDs correctos.

---

## 4. Ejecución del experimento

1. Desplegar la arquitectura (si no lo hiciste ya):

   ```bash
   kubectl apply -Rf /home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes/
   ```

2. Esperar 10 segundos y abrir tres terminales diferentes:

   **Terminal 1** – Jaeger:

   ```bash
   kubectl port-forward svc/jaeger 16686:16686 -n default
   ```

   **Terminal 2** – Frontend:

   ```bash
   kubectl port-forward svc/frontend 5000:5000 -n default
   ```

   **Terminal 3** – Generación de carga:

   ```bash
   wrk -t 2 -c 2 -d 30 -L -s ./mixed-workload_type_1.lua http://localhost:5000 -R 2
   ```

   Si `wrk` falla, espera unos segundos más y vuelve a ejecutar.

3. Ejecutar el script de despliegue + medición:

   ```bash
   ./deploycomp.sh
   ```

   ⚠️ Nota: el `wrk` debe seguir corriendo durante más tiempo que `deploycomp.sh`.

---

## 5. Resultados

Al finalizar, se generan archivos `.txt` con los resultados de consumo energético en cada máquina.
El formato esperado es:

```
Experiment: CPU Request 1, CPU Limit 100m on 1 Nodes and Control Plane
Local Machine (luish-Nitro-AN515-57)
Average Power : 0.14 Watts
Total Energy : 2.77 Joules

Remote Machine (luish@luish-Aspire-A315-55G)
Average Power : 0.23 Watts
Total Energy : 4.34 Joules

Remote Machine (luish@luish-HP-Laptop-14-dq0xxx)
Average Power : 2.27 Watts
Total Energy : 45.44 Joules
```

En algunos casos el formato puede tener caracteres extra. Corrige manualmente si es necesario.

---

## 6. Análisis de resultados y gráficos

Dentro de la carpeta `figures/scripts/` se incluyen varios scripts en Python para procesar los resultados y generar gráficos:

```bash
cd DeathStarBench/hotelReservation/kubernetes/figures/scripts/

# Análisis y visualización
python3 analisis.py
python3 comp.py
python3 graphics.py
python3 merge.py
python3 score.py
```

Estos generan comparaciones visuales de energía, rendimiento y consumo.

---

## 7. Resumen del flujo completo

1. Instalar Docker + Kubernetes.
2. Configurar clúster (1 master + 2 workers).
3. Desplegar **HotelReservation** en Kubernetes.
4. Ejecutar `gepidsh.sh` para configurar Ecofloc.
5. Lanzar Jaeger, Frontend y `wrk` en paralelo.
6. Ejecutar `deploycomp.sh` para medir consumo energético.
7. Verificar resultados `.txt` y generar gráficos con scripts en `figures/scripts`.

---

## Créditos

Basado en el benchmark **DeathStarBench** y la herramienta de medición energética **Ecofloc**.
Trabajo experimental realizado por **Luis Huachaca Vargas**.

```

---
