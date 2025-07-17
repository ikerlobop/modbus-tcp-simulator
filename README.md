# Simulador de Servidor Modbus TCP

Este proyecto crea un **servidor Modbus TCP simulado** usando `pymodbus`, ideal para pruebas, desarrollo o demostraciones sin hardware industrial.

---

## Características

Los datos Modbus son de una documentación de un enfriador industrial Carrier.

- Simula sensores y setpoints con valores aleatorios.
- Expone registros Modbus reales: Holding Registers, Input Registers y Discrete Inputs.
- Simula temperaturas, alarmas, puntos de control y más.
- Escucha en IP y puerto configurables.
- Hilo de actualización de datos en segundo plano.

---

## Requisitos

- Python 3.10.8 (probado y desarrollado en esta versión)
- `pymodbus` 2.x o superior

Instalación de dependencias:
```bash
pip install pymodbus
```

---

## Cómo ejecutarlo

1. Clona el repositorio:
```bash
git clone https://github.com/tuusuario/modsim-py.git
cd modsim-py
```

2. Ejecuta el servidor:
```bash
python modbus_server.py
```

---

## ¿Qué simula?

Registros como:

- `Cooling Setpoint 1/2` (`float`)
- `Heating Setpoint 1/2` (`float`)
- `Outdoor Air Temp` (`float`)
- Alarmas, control points y flags (`bool`/`uint32`)

Los valores se actualizan cada 2 segundos con datos aleatorios en rangos predeterminados por la documentación del enfriador de Carrier.

---

## Estructura de registros

| Tipo              | Dirección inicial | Descripción simulada        |
|-------------------|-------------------|-----------------------------|
| Discrete Inputs   | 00001             | Alarmas binarias            |
| Holding Registers | 00900–04120       | Setpoints, flags, potencias |
| Input Registers   | 00004–09110       | Temperaturas, presiones     |

---

## Se puede probar con cliente Modbus

Yo utilizo [Radzio Modbus Master Simulator](https://en.radzio.dxp.pl/modbus-master-simulator/), pero puedes usar:

- [Modbus Poll](https://www.modbustools.com/modbus_poll.html)
- [QModMaster](https://sourceforge.net/projects/qmodmaster/)
- Node-RED + nodo `modbus`
- Otro script en Python con `pymodbus`

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente.

---

## Autor

Desarrollado por **Iker Lobo** · [LinkedIn](https://www.linkedin.com/in/ikerloboperez/)  
Contacto: [ikerlobop@gmail.com](mailto:ikerlobop@gmail.com)
