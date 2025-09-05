
# DeathStarBench - Experimentos de Consumo Energético

Este repositorio contiene el despliegue y experimentación de **DeathStarBench**, con el microservicio **HotelReservation**, sobre un clúster de Kubernetes.  
El objetivo es medir el **consumo energético** de las aplicaciones mediante la integración con la herramienta **Ecofloc**.

---

## 1. Requisitos previos

Antes de ejecutar los experimentos, es necesario contar con un **clúster Kubernetes** configurado.  
Se recomienda usar **3 máquinas** (1 master + 2 workers) conectadas a la **misma red local**.

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


## 2. Configuración de Ecofloc

Para la medición de energía se utiliza **Ecofloc**, en una versión específica previa a las últimas actualizaciones.
Debes clonar el repositorio y mantenerte en el **commit usado en este proyecto**.

### Versión utilizada

Este proyecto utiliza Ecofloc en el commit:

```

commit ebd2c7a2cf173e75286415919abbe99888e5e984
Author: Humberto [hhumberto.av@gmail.com](mailto:hhumberto.av@gmail.com)
Date:   Fri Nov 22 23:53:24 2024 +0100

```


Para asegurarte de estar en esta versión exacta, clona y haz checkout:

```bash
git clone https://github.com/hhumberto/ecofloc.git
cd ecofloc
git checkout ebd2c7a2cf173e75286415919abbe99888e5e984
```

### Archivos de configuración

* En cada archivo `features.conf` (`cpu`, `ram`, `nic`, `sd`), configura el **factor de potencia** y los parámetros de hardware de tu máquina.
* En cada archivo `settings.conf`, ajusta la **ruta donde se guardarán los CSV** generados por Ecofloc.

### Compilación

```bash
make
```

Antes de ejecutar los experimentos, valida que Ecofloc funciona ejecutando los ejemplos provistos en el README de esa versión del repositorio.

### Sincronización de versiones

Una vez validado, copia los archivos `.c` modificados de este proyecto hacia tu instalación de Ecofloc y recompila:

```bash
cp /ruta/proyecto/ecofloc-*.c /ruta/ecofloc-descargado/
make clean && make
```

reemplaza todos los .c con los .c de este repo.

```bash
# Copiar archivos modificados desde tu repo de investigación hacia tu instalación local de Ecofloc
cp -r <repo route>/ecofloc/ecofloc-cpu/* <your route>/ecofloc/ecofloc-cpu/
cp -r <repo route>/ecofloc/ecofloc-gpu/* <your route>/ecofloc/ecofloc-gpu/
cp -r <repo route>/ecofloc/ecofloc-nic/* <your route>/ecofloc/ecofloc-nic/
cp -r <repo route>/ecofloc/ecofloc-ram/* <your route>/ecofloc/ecofloc-ram/
cp -r <repo route>/ecofloc/ecofloc-sd/* <your route>/ecofloc/ecofloc-sd/
cp <repo route>/ecofloc/server_info.txt <your route>/ecofloc/

```


## 3. Configuración de hosts y comunicación entre nodos

En cada nodo del clúster, edita el archivo `/etc/hosts` para mapear correctamente los **hostnames** e **IP addresses** de todos los nodos.

Para reconocer el ip de la propia maquina se hace:
```
luish@luish-Nitro-AN515-57:~$ hostname -I
172.16.167.25 172.17.0.1 
#172.16.167.25 es el ip que colocare en mis hosts
```

Ejemplo en el nodo master:

```
 sudo nano /etc/hosts
 ```

```
127.0.0.1       localhost
127.0.1.1       luish-Nitro-AN515-57
192.168.18.35   luish-Nitro-AN515-57
192.168.18.30   luish-Aspire-A315-55G
192.168.18.29   luish-HP-Laptop-14-dq0xxx
```

Prueba la conexión con:

```bash
ssh usuario@hostname
```

---

## 4. Verificación del despliegue

Una vez configurado el cluster, desplegar el servicio **HotelReservation**:

Se puede seguir la documentacion de ejecucion del benchmark: https://github.com/delimitrou/DeathStarBench/tree/master/hotelReservation/kubernetes

```bash
kubectl apply -Rf /ruta/DeathStarBench/hotelReservation/kubernetes/
```

Espera \~10 segundos y verifica que los pods estén corriendo:

```bash
kubectl get pods
```

Ahora cerraremos para sacar los pids, se desplegara despues para el experimento.
```bash
kubectl delete -Rf /ruta/DeathStarBench/hotelReservation/kubernetes/
```

---

## 5. Configuración de Ecofloc con PIDs del cluster

Dentro de la carpeta `hotelReservation/kubernetes/` se encuentra el script `gepidsh.sh`.
Este script recolecta los **PIDs** de los procesos del cluster en cada nodo y los configura para Ecofloc.

Ejemplo de configuración dentro del script:

```bash
YAML_DIR="/home/luish/Documents/death/DeathStarBench/hotelReservation/kubernetes" (colocar tu ruta)

remote_computers_list=("luish@luish-Aspire-A315-55G" "luish@luish-HP-Laptop-14-dq0xxx") (indicar los usuario@name de tu nodo)
sudo_password="238244758" (indicar tu sudo password)

declare -A remote_computers_map
remote_computers_map["luish@luish-Aspire-A315-55G"]="/home/luish/Documents/p3/ecofloc" (indicar la direccion de ecofloc en tu nodo)
remote_computers_map["luish@luish-HP-Laptop-14-dq0xxx"]="/home/luish/Documents/p3/ecofloc" (indicar la direccion de ecofloc en tu nodo)
```

Ejecutar:

```bash
./gepidsh.sh
```

Verifica que en cada nodo el archivo `pids.txt` haya sido actualizado correctamente.

---

## 6. Ejecución del experimento

1. Desplegar la arquitectura:

   ```bash
   kubectl apply -Rf /ruta/DeathStarBench/hotelReservation/kubernetes/
   ```

2. Abrir tres terminales:

   Estos terminales nos sirven para desviar algunos puertos del sobrecargador, antes de esto deberiamos seguir la documentacion del repositorio para la carga de trabajo, si la documentacion falla, seguiriamos esta propuesta: https://github.com/delimitrou/DeathStarBench/tree/master/hotelReservation/kubernetes

   Considerar que debemos descargar "wrk", la herramienta de generador de cargas: https://nitikagarw.medium.com/getting-started-with-wrk-and-wrk2-benchmarking-6e3cdc76555f

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

   ⚠️ Si `wrk` falla, espera unos segundos más y vuelve a ejecutar.

3. Ejecutar el script de despliegue y medición:

   ```bash
   ./deploycomp.sh
   ```

   ✅ Nota: el `wrk` debe correr durante más tiempo que `deploycomp.sh`.

---

## 7. Resultados

Al finalizar, se generan archivos `.txt` con los resultados de consumo energético en la maquina principal.
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

En algunos casos el formato puede incluir caracteres extra. Corrige manualmente si es necesario.

---

## 8. Análisis y gráficos

Dentro de la carpeta `figures/scripts/` se incluyen varios scripts en Python para procesar los resultados y generar gráficos:

```bash
cd DeathStarBench/hotelReservation/kubernetes/figures/scripts/

python3 analisis.py
python3 comp.py
python3 graphics.py
python3 merge.py
python3 score.py
```

---

## 9. Flujo resumido

1. Instalar Docker + Kubernetes.
2. Configurar clúster (1 master + 2 workers).
3. Instalar y compilar versión específica de Ecofloc.
4. Ajustar `features.conf` y `settings.conf` en Ecofloc.
5. Editar `/etc/hosts` en todos los nodos para comunicación SSH.
6. Ejecutar `gepidsh.sh` para recolectar PIDs.
7. Desplegar **HotelReservation** en Kubernetes.
8. Lanzar Jaeger, Frontend y `wrk` en paralelo.
9. Ejecutar `deploycomp.sh` para medición.
10. Revisar resultados y graficar con scripts en `figures/scripts`.

---

## Créditos

* Benchmark: **DeathStarBench**
* Herramienta de medición: **Ecofloc**
* Experimentos realizados por: **Luis Huachaca Vargas**

```

---





# DeathStarBench

Open-source benchmark suite for cloud microservices. DeathStarBench includes five end-to-end services, four for cloud systems, and one for cloud-edge systems running on drone swarms. 

## End-to-end Services <img src="microservices_bundle4.png" alt="suite-icon" width="40"/>

* Social Network (released)
* Media Service (released)
* Hotel Reservation (released)
* E-commerce site (in progress)
* Banking System (in progress)
* Drone coordination system (in progress)

## License & Copyright 

DeathStarBench is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 2.

DeathStarBench is being developed by the [SAIL group](http://sail.ece.cornell.edu/) at Cornell University. 

## Publications

More details on the applications and a characterization of their behavior can be found at ["An Open-Source Benchmark Suite for Microservices and Their Hardware-Software Implications for Cloud and Edge Systems"](http://www.csl.cornell.edu/~delimitrou/papers/2019.asplos.microservices.pdf), Y. Gan et al., ASPLOS 2019. 

If you use this benchmark suite in your work, we ask that you please cite the paper above. 


## Beta-testing

If you are interested in joining the beta-testing group for DeathStarBench, send us an email at: <microservices-bench-L@list.cornell.edu>
