# EJERCICIO - ATM
## Crear una aplicación de un cajero automático (ATM) con los siguientes requerimientos:
[ ] Código con modularidad (Funciones, Clases: ej. autenticar_usuario(), realizar_retiro())
[ ] Manejo de excepciones (La aplicación nunca debe cerrarse por un error del usuario. ej. si ingresa texto en lugar de un número al retirar dinero)
[ ] Validaciones (OPCIONAL)
[ ] Persistencia de datos (Diccionarios, listas, Postgresql - OPCIONAL)
[ ] Autenticación (Ingresar con numero de tarjeta, contraseña (encryptada))
[ ] Operaciones básicas (Consultar saldo, depósitos, retiros e historial de transacciones)
[ ] Algoritmos antigraude y seguridad operativa (Bloqueo por fallar 3 veces consecutivas en la contraseña, límite de retiro diario, detección de actividad sospechosa, algoritmo de luhn)
[ ] Logs (Guardar el historial de cada actividad en un seguridad_atm.log [FECHA Y HORA - TIPO DE EVENTO - CUENTA - DETALLE])