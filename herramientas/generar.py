"""Todas las imágenes del manual, módulo por módulo."""
from img import partes, paso, plano
FULL = (0, 100, 1080, 2436)      # pantalla completa sin barra de estado
SINBARRA = (0, 100, 1080, 2064)  # sin barra de estado ni barra inferior

# ---------- Inicio: detalle de promoción ----------
partes("promo.png", "inicio/promocion.png", (0, 480, 1080, 2436), [
    (1, (95, 1225, 1000, 1515)), (2, (50, 1600, 1030, 1895)), (3, (50, 1985, 1030, 2195)), (4, (50, 2225, 1030, 2386))])

# ---------- Ficha del cliente ----------
partes("ficha1b.png", "ficha/ficha-1.png", (0, 100, 1080, 1480), [
    (1, (45, 660, 1035, 965)), (2, (45, 975, 1035, 1465))])
partes("ficha2.png", "ficha/ficha-2.png", (0, 480, 1080, 1810), [
    (3, (35, 495, 1045, 1330)), (4, (35, 1385, 1045, 1800))])
partes("ficha3.png", "ficha/ficha-3.png", (0, 560, 1080, 1450), [
    (5, (590, 712, 1045, 778)), (6, (35, 792, 1045, 1015)), (7, (35, 1055, 1045, 1437))])
partes("ficha6.png", "ficha/ficha-4.png", (0, 840, 1080, 2000), [
    (8, (40, 865, 1040, 1088)), (9, (40, 1110, 1040, 1792)), (10, (40, 1825, 1040, 1986))])
plano("f_ped.png", "ficha/historico-pedidos.png", SINBARRA)
plano("ped_det.png", "ficha/detalle-pedido.png", SINBARRA)
plano("ped_det2.png", "ficha/detalle-pedido-dpp.png", (0, 420, 1080, 2064))
plano("f_fac.png", "ficha/historico-facturas.png", FULL)
partes("f_fac2.png", "ficha/historico-facturas-lista.png", (0, 1040, 1080, 2436), [
    (1, (40, 1060, 1040, 1222)), (2, (85, 1675, 532, 1786), 'e'), (3, (548, 1675, 995, 1786), 'e')])

# ---------- Punto de Venta ----------
paso("pdv1.png", "punto-de-venta/buscar-cliente.png", FULL, [(40, 565, 1040, 720), (40, 958, 1040, 2194)])
partes("pdv2.png", "punto-de-venta/tipo-formulario.png", SINBARRA, [
    (1, (40, 988, 1040, 1446)), (2, (40, 1480, 1040, 1938))])
paso("pdv3.png", "punto-de-venta/propios-competencia.png", (0, 100, 1080, 1700), [(40, 1035, 1040, 1311)])
partes("pdv4.png", "punto-de-venta/productos-propios.png", FULL, [
    (1, (40, 820, 1040, 1560)), (2, (40, 1900, 1040, 2050)), (3, (40, 2203, 1040, 2353))])
partes("pdv5.png", "punto-de-venta/producto.png", (0, 450, 1080, 2170), [
    (1, (40, 1074, 1040, 1352)), (2, (60, 1405, 1030, 1520)), (3, (60, 1555, 1030, 1770)), (4, (60, 1810, 1030, 2045))])
plano("pdv_comp.png", "punto-de-venta/competencia.png", FULL)
partes("pdv_stock.png", "punto-de-venta/almacen.png", FULL, [
    (1, (40, 618, 1040, 1195)), (2, (40, 1668, 1040, 1797)), (3, (40, 2203, 1040, 2353))])

# ---------- Pedidos ----------
partes("ped1.png", "pedidos/paso-1-inicio.png", FULL, [
    (1, (5, 390, 1075, 705)), (2, (40, 745, 1040, 1135)), (3, (5, 2200, 1075, 2380))])
partes("ped2.png", "pedidos/paso-1-cliente.png", (0, 100, 1080, 2200), [
    (1, (40, 955, 1040, 1160)), (2, (40, 1175, 1040, 1255)), (3, (85, 1675, 995, 1815))])
partes("ped4.png", "pedidos/paso-1-productos.png", (0, 380, 1080, 2436), [
    (4, (375, 1370, 960, 1760)), (5, (40, 1932, 1040, 2073)), (6, (5, 2200, 1075, 2380))])
partes("ped5.png", "pedidos/paso-2-detalle.png", FULL, [
    (1, (40, 742, 1040, 980)), (2, (40, 1012, 1040, 1380)), (3, (40, 1411, 1040, 2045)), (4, (540, 2228, 1016, 2348))])
plano("ped6.png", "pedidos/paso-2-dpp.png", (0, 1000, 1080, 2110))

# ---------- Cobranzas ----------
partes("cob1.png", "cobranzas/cartera-1.png", SINBARRA, [
    (1, (40, 340, 1040, 476)), (2, (40, 556, 1040, 987)), (3, (40, 1010, 1040, 1276)), (4, (40, 1299, 1040, 1652))])
partes("cob2.png", "cobranzas/cartera-2.png", (0, 480, 1080, 2064), [
    (5, (40, 575, 1040, 1146)), (6, (40, 1191, 1040, 2060))])
partes("cob_cli1.png", "cobranzas/registrar-pago.png", (0, 100, 1080, 2380), [
    (1, (62, 534, 1018, 924)), (2, (62, 969, 1018, 1234)), (3, (62, 1268, 1018, 1476)), (4, (62, 1543, 1018, 2155))])
plano("cob_cli2.png", "cobranzas/modalidades.png", (0, 100, 1080, 2380))
partes("cob_p1.png", "cobranzas/paso-1-elige.png", FULL, [
    (1, (5, 440, 1075, 680)), (2, (62, 750, 1018, 1520)), (3, (62, 1582, 1018, 2140)), (4, (5, 2160, 1075, 2380))])
partes("cob_p2.png", "cobranzas/paso-2-calculo.png", FULL, [
    (1, (45, 735, 1035, 1035)), (2, (45, 1065, 1035, 1325)), (3, (45, 1365, 1035, 2013)), (4, (62, 2052, 1018, 2183))])
plano("cob_p2b.png", "cobranzas/paso-2-total.png", (0, 700, 1080, 2020))
paso("cob_p3.png", "cobranzas/paso-3-comprobantes.png", FULL, [(540, 790, 990, 882)])
partes("cob_p3b.png", "cobranzas/paso-3-soporte.png", FULL, [
    (1, (98, 1557, 982, 1699)), (2, (50, 1801, 1030, 1943)), (3, (5, 2012, 1075, 2380))])
plano("bill1.png", "cobranzas/usar-saldo.png", (0, 1440, 1080, 2380))
partes("bill_abono.png", "cobranzas/billetera.png", FULL, [
    (1, (50, 413, 1030, 1091)), (2, (116, 878, 964, 1025), 'e'), (3, (50, 1147, 1030, 1377)), (4, (50, 1400, 1030, 2436))])
partes("bill_form.png", "cobranzas/abono-1.png", FULL, [
    (1, (50, 408, 1030, 649)), (2, (520, 1022, 948, 1110), 'e'), (3, (80, 1180, 1000, 1370)), (4, (80, 1430, 1000, 1652)), (5, (50, 2200, 1030, 2342))])
partes("bill_form2.png", "cobranzas/abono-2.png", (0, 380, 1080, 2436), [
    (6, (80, 1195, 1000, 1390)), (7, (108, 1724, 972, 1866)), (8, (50, 1958, 1030, 2111))])
plano("grupo1.png", "cobranzas/grupo-lista.png", (0, 100, 1080, 1100))
partes("grupo2.png", "cobranzas/grupo-facturas.png", FULL, [
    (1, (50, 745, 1030, 850)), (2, (50, 881, 1030, 1765)), (3, (5, 2160, 1075, 2380))])
partes("auto1.png", "cobranzas/abono-automatico.png", FULL, [
    (1, (5, 440, 1075, 680)), (2, (62, 2211, 1018, 2353))])

# ---------- Clientes ----------
partes("cli1.png", "clientes/directorio.png", SINBARRA, [
    (1, (40, 1015, 1040, 1160)), (2, (40, 1198, 1040, 1340)), (3, (40, 1385, 1040, 1932))])
partes("cli_new.png", "clientes/tipo-alta-1.png", FULL, [(1, (62, 892, 1018, 1724))])
partes("cli_new2.png", "clientes/tipo-alta-2.png", (0, 700, 1080, 2300), [
    (2, (62, 776, 1018, 1503)), (3, (62, 1559, 1018, 2265))])
plano("rap1.png", "clientes/rapido-1.png", FULL)
paso("rap2.png", "clientes/rapido-2.png", FULL, [(62, 1505, 1018, 2392)])
paso("rap3.png", "clientes/rapido-3.png", FULL, [(104, 1345, 976, 1465), (62, 2257, 1018, 2397)])
paso("comp1.png", "clientes/completo-1.png", FULL, [(810, 845, 1030, 900)])
plano("suc1.png", "clientes/sucursal-1.png", FULL)

# ---------- Mis Solicitudes ----------
partes("f_sol.png", "solicitudes/categorias.png", (0, 100, 1080, 2200), [
    (1, (62, 562, 1018, 1042)), (2, (62, 1087, 1018, 1567)), (3, (62, 1612, 1018, 2092))])
partes("sol_inc.png", "solicitudes/incidencias.png", FULL, [
    (1, (62, 713, 1018, 849)), (2, (62, 916, 1018, 1432)), (3, (62, 1499, 1018, 2224))])
partes("sol_det.png", "solicitudes/detalle.png", (0, 100, 1080, 1750), [
    (1, (62, 391, 1018, 566)), (2, (62, 611, 1018, 1031)), (3, (62, 1098, 1018, 1625))])
partes("sol_new.png", "solicitudes/nueva-incidencia.png", FULL, [
    (1, (62, 795, 1018, 1017)), (2, (62, 1062, 1018, 1284)), (3, (62, 1329, 1018, 1625)), (4, (62, 1662, 1018, 2135)), (5, (62, 2220, 1018, 2362))])
plano("sol_tipos.png", "solicitudes/tipos-reclamo.png", (0, 1100, 1080, 2100))
partes("comp_new.png", "solicitudes/nueva-compensacion.png", (0, 100, 1080, 2240), [
    (1, (62, 795, 1018, 1017)), (2, (62, 1062, 1018, 1284)), (3, (62, 1329, 1018, 1567)), (4, (62, 1600, 1018, 1850)), (5, (62, 1905, 1018, 2125))])
plano("sol_cli.png", "solicitudes/clientes.png", (0, 100, 1080, 2000))

# ---------- Mi Cuota ----------
partes("cuota1.png", "cuota/cuota-1.png", FULL, [
    (1, (15, 110, 900, 370)), (2, (935, 125, 1045, 235), 'e'), (3, (40, 415, 1040, 685)), (4, (40, 700, 1040, 958)),
    (5, (40, 995, 1040, 1518)), (6, (40, 1560, 1040, 1884)), (7, (40, 1915, 1040, 2436))])
partes("cuota2.png", "cuota/cuota-2.png", (0, 1300, 1080, 2230), [
    (8, (40, 1327, 1040, 1767)), (9, (40, 1810, 1040, 2150))])
partes("cuota4.png", "cuota/cuota-3.png", (0, 380, 1080, 2300), [
    (10, (40, 465, 1040, 1178)), (11, (40, 1222, 1040, 1992)), (12, (50, 2126, 1030, 2276))])
partes("cuota_marca.png", "cuota/por-marca.png", (0, 100, 1080, 1700), [
    (1, (40, 482, 1040, 988)), (2, (40, 1029, 1040, 1141)), (3, (40, 1180, 1040, 1625))])
partes("cuota_hist.png", "cuota/historico.png", FULL, [
    (1, (40, 325, 1040, 434)), (2, (40, 470, 1040, 860))])

# ---------- Menú lateral ----------
partes("menu.png", "menu/menu.png", FULL, [
    (1, (290, 145, 1070, 325)), (2, (244, 355, 1075, 1018)), (3, (244, 2225, 1075, 2364))])

# ---------- Lista de precios ----------
partes("lp1.png", "precios/listas.png", FULL, [
    (1, (60, 280, 460, 375)), (2, (48, 505, 1032, 881))])
partes("lp2.png", "precios/lista-detalle.png", (0, 100, 1080, 1700), [
    (1, (48, 468, 1032, 620)), (2, (48, 662, 1032, 879)), (3, (48, 880, 1032, 1088))])
partes("lp3.png", "precios/producto.png", FULL, [
    (1, (48, 468, 1032, 594)), (2, (48, 618, 1032, 1096)), (3, (48, 1142, 1032, 1289)), (4, (48, 1335, 1032, 2436))])

# ---------- Históricos ----------
plano("hf.png", "historicos/facturas.png", (0, 100, 1080, 1900))
partes("hp.png", "historicos/pedidos.png", FULL, [
    (1, (50, 530, 1045, 690)), (2, (50, 710, 512, 827)), (3, (5, 850, 1075, 959)), (4, (50, 1010, 1030, 1666))])
partes("hc.png", "historicos/cobranzas.png", (0, 100, 1080, 2250), [
    (1, (40, 535, 1040, 690)), (2, (40, 798, 1040, 1520))])

# ---------- Configuración ----------
partes("conf.png", "configuracion/configuracion.png", SINBARRA, [
    (1, (100, 290, 980, 800)), (2, (50, 850, 1030, 1200)), (3, (50, 1282, 1030, 1628)), (4, (50, 1695, 1030, 2040))])

# ---------- Tracking ----------
partes("track.png", "tracking/tracking.png", SINBARRA, [(1, (50, 496, 1030, 613))])

# ---------- Inicio de sesión ----------
partes("login-vacio.png", "inicio-de-sesion/pantalla-inicio-sesion.png", FULL, [
    (1, (115, 1030, 965, 1320)), (2, (115, 1350, 965, 1632)), (3, (830, 1490, 935, 1592), 'e'),
    (4, (120, 1700, 783, 1860)), (5, (800, 1700, 955, 1860), 'e'), (6, (230, 1885, 850, 1965))])
paso("login-vacio.png", "inicio-de-sesion/paso-2-usuario.png", FULL, [(120, 1135, 960, 1318)])
paso("login-lleno.png", "inicio-de-sesion/paso-3-contrasena.png", FULL, [(120, 1447, 960, 1631)])
paso("login-lleno.png", "inicio-de-sesion/paso-4-entrar.png", FULL, [(120, 1700, 783, 1860)])
paso("login-vacio.png", "inicio-de-sesion/olvido-paso-1.png", FULL, [(230, 1885, 850, 1965)])
partes("login-recuperar.png", "inicio-de-sesion/olvido-paso-2.png", FULL, [
    (1, (115, 1200, 965, 1475)), (2, (120, 1528, 960, 1690)), (3, (290, 1715, 790, 1790))])
