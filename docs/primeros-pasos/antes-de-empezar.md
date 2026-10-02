# Antes de empezar

Esta página explica las ideas que están detrás de casi todo lo que hace la aplicación. Leerla primero te ahorra dudas después.

## Qué es la aplicación

Es la herramienta de trabajo en la calle del ejecutivo de ventas. Con ella:

- Empiezas la jornada con la lista de clientes que te toca visitar.
- Revisas cómo está el producto exhibido en cada comercio.
- Levantas pedidos.
- Cobras facturas pendientes.
- Reportas los problemas que aparecen en el camino.

Las cuotas mensuales y las promociones que ves en la aplicación las carga el personal administrativo desde un portal web aparte.

## Quién es el cliente

En esta aplicación, **cliente** es siempre el **comercio**: supermercados, licorerías, abastos, bodegones, hoteles, distribuidoras y tiendas libres de impuestos. Nunca es la persona que compra la botella en el anaquel.

## Tú solicitas, otras áreas aprueban

Esta es la idea más importante: **el vendedor no ejecuta, el vendedor solicita**.

Cuando levantas un pedido, das de alta un cliente o reportas una incidencia, eso no se aplica de inmediato. Se convierte en una **solicitud** que pasa por revisión de otras áreas de la empresa. Solo al final queda aprobada o rechazada.

Cada solicitud tiene un seguimiento con estos hitos:

1. **Solicitud creada.**
2. **En proceso de revisión**, por el área que corresponde.
3. **Solicitud cerrada.**

Puedes consultar en qué punto va cada solicitud en [Mis Solicitudes](../modulos/mis-solicitudes.md).

!!! warning "Si rechazan un pedido"
    Un pedido rechazado no se corrige. Se crea un pedido nuevo con las condiciones que sí pasan la revisión.

## Segmentos y listas de precio

La empresa maneja alrededor de **cuarenta listas de precio**. A cada cliente le corresponde una según su **grupo de precio** y su **segmento**.

- Los segmentos van desde el cliente estándar y el cliente en desarrollo hasta las categorías A, B y C, además de los distribuidores aliados.
- El segmento **Zanahoria** es el que obtiene el mejor precio. Un cliente llega a Zanahoria por su comportamiento: paga antes del vencimiento, pide volumen y rota el producto rápido.

!!! tip "Regla clave"
    El precio cambia **únicamente por segmento**. Ninguna otra variable lo modifica.

## Niveles de cliente

Cada cliente tiene un **nivel del 1 al 4**, que depende de cómo paga. El nivel define **qué formas de pago se le habilitan** en Cobranzas. Los niveles más altos tienen más opciones.

No confundas nivel con segmento:

| Concepto | Qué define |
|---|---|
| **Segmento** | A qué precio se le vende al cliente. |
| **Nivel** | De qué formas puede pagar el cliente. |

## Billetera y saldo a favor

Cada cliente tiene una **billetera virtual** con un **saldo a favor** que puede usar para pagar facturas. Ese saldo viene de dos lugares:

- **Notas de crédito** emitidas a favor del cliente.
- **Depósitos o sobrepagos**, es decir, dinero que el cliente entregó de más o abonó por adelantado.

La billetera se puede recargar desde [Cobranzas](../modulos/cobranzas.md#abonar-a-la-billetera-del-cliente).

## La tasa de cambio

Es la pieza más delicada de la aplicación, porque los montos se manejan en dólares y en bolívares.

- Cada factura guarda la **tasa BCV del día en que se emitió** y no la cambia después.
- La aplicación también muestra la **tasa BCV de hoy**.
- Al cobrar, la aplicación calcula el pago con la tasa que corresponde según el nivel del cliente.
- Cuando hay diferencia entre la tasa de emisión y la tasa del día del pago, la aplicación te avisa que **Santa Teresa emitirá una nota de débito** por ese diferencial. Comunícaselo al cliente.

## Trabajar sin conexión

La aplicación está pensada para la calle, donde la señal a veces se cae. Sin conexión puedes seguir usando:

- El Inicio completo: ventas del mes, cobros pendientes y clientes del día.
- El directorio de clientes con sus direcciones.
- El Punto de Venta completo, con el catálogo de productos.
- La cartera de cobranza.

La información que ves sin señal es la última que la aplicación descargó. Si el cliente hizo un pago hace poco, ese movimiento se verá cuando recuperes la conexión.

Lo que registres sin señal queda guardado en el teléfono y **se envía solo** cuando vuelve la conexión. No tienes que volver a llenar nada.

!!! warning "Esto sí necesita conexión"
    Para cerrar un cobro de facturas necesitas conexión, porque el cálculo usa la tasa del día y esa tasa viene del sistema.

### Cerrar la jornada con todo enviado

1. Trabaja con normalidad durante el día, tengas señal o no.
2. Al terminar, ubícate en un lugar con cobertura y abre la aplicación.
3. Déjala abierta unos segundos para que envíe lo que quedó guardado.
4. Entra a los módulos donde registraste algo y confirma que no quede nada pendiente de envío.
