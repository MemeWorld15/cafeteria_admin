from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import mysql.connector
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from datetime import datetime
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI()

# CORS para permitir conexión desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cafeteria-admin.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CONEXIÓN ----------------
def get_db_connection():
    return psycopg2.connect(
        host="dpg-d0nqf2juibrs738t3sbg-a.oregon-postgres.render.com",             # Ej: "dpg-xxxxxx.render.com"
        user="admin",          # Ej: "admin"
        password="5iaR0WvAkuDojeqiERfKwhcQgJ0TdlmO",     # Tu contraseña
        database="cafe_unach",
        port="5432"
    )

# ---------------- MODELOS ----------------
class ProductoOrden(BaseModel):
    nombre: str
    cantidad: int
    precio: float

class OrdenEntrada(BaseModel):
    cliente: str
    nota: str = ""
    usuario_id: Optional[int]
    productos: List[ProductoOrden]

# ---------------- RUTAS ----------------

@app.get("/")
def root():
    return {"message": "¡La API está funcionando correctamente!"}

@app.post("/")
def post_root():
    return {"message": "¡POST recibido correctamente en /"}

@app.post("/login")
def login(correo: str = Form(...), contrasena: str = Form(...)):  # <- CAMBIO
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE correo=%s AND contrasena=%s", (correo, contrasena))  # <- CAMBIO
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        return {
            "success": True,
            "rol": user["rol"],
            "usuario_id": user["id"],
            "nombre": user["nombre"]
        }
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

@app.post("/registro")
def register(
    nombre: str = Form(...),
    correo: str = Form(...),
    contrasena: str = Form(...),   # sin ñ
    grado: str = Form(...),
    carrera: str = Form(...)
):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contrasena, grado, carrera, rol) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, correo, contrasena, grado, carrera, 'cliente')  # contrasena variable aquí
        )
        db.commit()
        return {"success": True}
    except psycopg2.errors.UniqueViolation:
        db.rollback()
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error del servidor: " + str(e))
    finally:
        cursor.close()
        db.close()

# El resto de tu código...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)

@app.get("/menu")
def obtener_menu():
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    # Obtener todas las categorías
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    menu = {}
    for cat in categorias:
        cursor.execute("SELECT * FROM productos WHERE categoria_id = %s", (cat['id'],))
        productos = cursor.fetchall()
        menu[cat['nombre']] = productos

    cursor.close()
    db.close()
    return menu

# ---------------- EMPLEADOS ----------------
@app.post("/empleados")
def crear_empleado(
    nombre: str = Form(...),
    correo: str = Form(...),
    ocupacion: str = Form(...),
    rendimiento: str = Form(...),
    contrasena: str = Form(...),
    creado_por: int = Form(...)
):
    db = get_db_connection()
    cursor = db.cursor()
    foto = f"https://i.pravatar.cc/150?img={abs(hash(correo)) % 70 + 1}"
    try:
        cursor.execute("""
            INSERT INTO empleados (nombre, correo, ocupacion, rendimiento, contrasena, foto, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, correo, ocupacion, rendimiento, contrasena, foto, creado_por))

        if ocupacion.lower() == "chef":
            cursor.execute("""
                INSERT INTO usuarios (nombre, correo, contrasena, grado, carrera, rol)
                VALUES (%s, %s, %s, '-', '-', 'chef')
            """, (nombre, correo, contrasena))

        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        db.close()

@app.get("/empleados")
def listar_empleados():
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM empleados")
    empleados = cursor.fetchall()
    cursor.close()
    db.close()
    return empleados

# ---------------- CATEGORÍAS ----------------
@app.get("/categorias")
def listar_categorias():
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()
    db.close()
    return categorias

@app.post("/categorias")
def crear_categoria(nombre: str = Form(...)):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (nombre,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@app.put("/categorias/{categoria_id}")
def actualizar_categoria(categoria_id: int, nombre: str = Form(...)):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE categorias SET nombre = %s WHERE id = %s", (nombre, categoria_id))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(categoria_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM categorias WHERE id = %s", (categoria_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ---------------- PRODUCTOS ----------------
@app.post("/productos")
def crear_producto(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    precio: float = Form(...),
    categoria_id: int = Form(...)
):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, descripcion, precio, categoria_id)
        VALUES (%s, %s, %s, %s)
    """, (nombre, descripcion, precio, categoria_id))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@app.get("/productos")
def listar_productos():
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    db.close()
    return productos

@app.put("/productos/{producto_id}")
def editar_producto(
    producto_id: int,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    precio: float = Form(...),
    categoria_id: int = Form(...)
):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE productos
        SET nombre=%s, descripcion=%s, precio=%s, categoria_id=%s
        WHERE id=%s
    """, (nombre, descripcion, precio, categoria_id, producto_id))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@app.put("/productos/{producto_id}/toggle-disponible")
def toggle_disponibilidad(producto_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE productos SET disponible = NOT disponible WHERE id = %s", (producto_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ---------------- ÓRDENES ----------------
@app.post("/ordenar")
def crear_orden(data: OrdenEntrada):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO ordenes (cliente, nota, usuario_id, entregado)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (data.cliente, data.nota, data.usuario_id, False))
        orden_id = cursor.fetchone()[0]  # ✅ Ahora sí funciona

        for prod in data.productos:
            cursor.execute("""
                INSERT INTO orden_productos (orden_id, nombre_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (orden_id, prod.nombre, prod.cantidad, prod.precio))

        db.commit()
        return {"success": True, "orden_id": orden_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@app.get("/ordenes")
def listar_ordenes():
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM ordenes ORDER BY id DESC")
    ordenes = cursor.fetchall()

    for orden in ordenes:
        cursor.execute("SELECT * FROM orden_productos WHERE orden_id = %s", (orden["id"],))
        orden["productos"] = cursor.fetchall()
        orden["hora"] = orden["fecha"].strftime("%I:%M %p")
        orden["fecha"] = orden["fecha"].strftime("%d-%m-%Y")

    cursor.close()
    db.close()
    return ordenes

@app.delete("/ordenes/{orden_id}")
def cancelar_orden(orden_id: int):
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT fecha, entregado FROM ordenes WHERE id = %s", (orden_id,))
    orden = cursor.fetchone()

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if orden["entregado"]:
        raise HTTPException(status_code=400, detail="La orden ya fue entregada")
    if datetime.now() - orden["fecha"] > timedelta(minutes=2):
        raise HTTPException(status_code=403, detail="La orden ya no se puede cancelar")

    cursor.execute("DELETE FROM ordenes WHERE id = %s", (orden_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@app.get("/ordenes/cliente/{usuario_id}")
def obtener_ordenes_cliente(usuario_id: int):
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM ordenes WHERE usuario_id = %s ORDER BY id DESC", (usuario_id,))
    ordenes = cursor.fetchall()

    for orden in ordenes:
        cursor.execute("SELECT * FROM orden_productos WHERE orden_id = %s", (orden["id"],))
        orden["productos"] = cursor.fetchall()
        orden["hora"] = orden["fecha"].strftime("%I:%M %p")
        orden["fecha_mostrada"] = orden["fecha"].strftime("%d-%m-%Y")

    cursor.close()
    db.close()
    return ordenes

@app.put("/ordenes/{orden_id}/entregado")
def marcar_entregado(orden_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE ordenes SET entregado = TRUE WHERE id = %s", (orden_id,))
        db.commit()
        return {"success": True}
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar el estado de la orden")
    finally:
        cursor.close()
        db.close()


# ---------------- GRAFICAS ----------------
@app.get("/graficas/top-productos")
def top_productos():
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT nombre_producto, SUM(cantidad) as total_pedidos
        FROM orden_productos GROUP BY nombre_producto
        ORDER BY total_pedidos DESC
    """)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data

@app.get("/graficas/top-clientes")
def top_clientes():
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT cliente, COUNT(*) AS total_ordenes
        FROM ordenes
        GROUP BY cliente
        ORDER BY total_ordenes DESC
    """)
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data

@app.get("/productos/menos-pedido")
def producto_menos_pedido():
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT nombre_producto, SUM(cantidad) AS total_vendidos
        FROM orden_productos
        GROUP BY nombre_producto
        ORDER BY total_vendidos ASC
        LIMIT 1
    """)
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data

# ---------------- INVENTARIO ----------------
# ✅ GET Inventario
@app.get("/inventario")
def listar_inventario():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM inventario")
    datos = cursor.fetchall()
    cursor.close()
    db.close()
    return datos

# ✅ POST Inventario
@app.post("/inventario")
def agregar_insumo(nombre: str = Form(...), cantidad: float = Form(...), unidad: str = Form(...)):
    if cantidad < 0:
        raise HTTPException(status_code=400, detail="La cantidad no puede ser negativa.")
    if unidad not in UNIDADES_VALIDAS:
        raise HTTPException(status_code=400, detail="Unidad no permitida.")

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO inventario (nombre, cantidad, unidad) VALUES (%s, %s, %s)", (nombre, cantidad, unidad))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ✅ PUT Inventario (actualizar cantidad directamente)
@app.put("/inventario/{id}")
def actualizar_insumo(id: int, cantidad: float = Form(...)):
    if cantidad < 0:
        raise HTTPException(status_code=400, detail="La cantidad no puede ser negativa.")
    
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE inventario SET cantidad = %s WHERE id = %s", (cantidad, id))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ✅ DELETE Inventario
@app.delete("/inventario/{id}")
def eliminar_insumo(id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM inventario WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ✅ CONSUMO PARCIAL DE INSUMO
@app.post("/inventario/{id}/consumir")
def consumir_insumo(id: int, cantidad_usada: float = Form(...), unidad: str = Form(...)):
    if cantidad_usada <= 0:
        raise HTTPException(status_code=400, detail="Cantidad usada inválida.")
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Verifica que existe
    cursor.execute("SELECT cantidad, unidad FROM inventario WHERE id = %s", (id,))
    insumo = cursor.fetchone()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado.")

    if unidad != insumo["unidad"]:
        raise HTTPException(status_code=400, detail="Unidad no coincide con la registrada.")

    nueva_cantidad = insumo["cantidad"] - cantidad_usada
    if nueva_cantidad < 0:
        raise HTTPException(status_code=400, detail="No hay suficiente cantidad disponible.")

    # Actualiza
    cursor.execute("UPDATE inventario SET cantidad = %s WHERE id = %s", (nueva_cantidad, id))
    db.commit()
    cursor.close()
    db.close()

    return {"success": True, "restante": nueva_cantidad}

@app.get("/inventario/pdf")
def generar_pdf_inventario():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario")
    inventario = cursor.fetchall()
    cursor.close()
    db.close()

    # Crear archivo PDF temporal
    pdf_path = "inventario.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "📋 Reporte de Inventario - Cafetería")

    # Fecha
    c.setFont("Helvetica", 10)
    c.drawString(400, height - 50, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Encabezados
    y = height - 80
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Nombre")
    c.drawString(200, y, "Cantidad")
    c.drawString(270, y, "Unidad")
    c.drawString(350, y, "Estado")

    c.setFont("Helvetica", 10)
    y -= 20

    for item in inventario:
        if y < 60:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Nombre")
            c.drawString(200, y, "Cantidad")
            c.drawString(270, y, "Unidad")
            c.drawString(350, y, "Estado")
            c.setFont("Helvetica", 10)
            y -= 20

        cantidad = item['cantidad']
        estado = ""

        if cantidad < 2:
            estado = "❌ Muy bajo"
        elif 2 <= cantidad <= 4:
            estado = "⚠️ Rellenar stock"
        else:
            estado = "✅ Bien"

        # Mostrar fila
        c.drawString(50, y, item["nombre"])
        c.drawString(200, y, f"{cantidad:.2f}")
        c.drawString(270, y, item["unidad"])
        c.drawString(350, y, estado)

        y -= 20

    c.save()

    return FileResponse(pdf_path, media_type='application/pdf', filename="inventario.pdf")
# ---------------- MAIN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

# ✅ GET Inventario
@app.get("/inventario")
def listar_inventario():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM inventario")
    datos = cursor.fetchall()
    cursor.close()
    db.close()
    return datos

# ✅ POST Inventario
@app.post("/inventario")
def agregar_insumo(nombre: str = Form(...), cantidad: float = Form(...), unidad: str = Form(...)):
    if cantidad < 0:
        raise HTTPException(status_code=400, detail="La cantidad no puede ser negativa.")
    if unidad not in UNIDADES_VALIDAS:
        raise HTTPException(status_code=400, detail="Unidad no permitida.")

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO inventario (nombre, cantidad, unidad) VALUES (%s, %s, %s)", (nombre, cantidad, unidad))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ✅ PUT Inventario (actualizar cantidad directamente)
@app.put("/inventario/{id}")
def actualizar_insumo(id: int, cantidad: float = Form(...)):
    if cantidad < 0:
        raise HTTPException(status_code=400, detail="La cantidad no puede ser negativa.")
    
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE inventario SET cantidad = %s WHERE id = %s", (cantidad, id))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ✅ DELETE Inventario
@app.delete("/inventario/{id}")
def eliminar_insumo(id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM inventario WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

# ✅ CONSUMO PARCIAL DE INSUMO
@app.post("/inventario/{id}/consumir")
def consumir_insumo(id: int, cantidad_usada: float = Form(...), unidad: str = Form(...)):
    if cantidad_usada <= 0:
        raise HTTPException(status_code=400, detail="Cantidad usada inválida.")
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Verifica que existe
    cursor.execute("SELECT cantidad, unidad FROM inventario WHERE id = %s", (id,))
    insumo = cursor.fetchone()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado.")

    if unidad != insumo["unidad"]:
        raise HTTPException(status_code=400, detail="Unidad no coincide con la registrada.")

    nueva_cantidad = insumo["cantidad"] - cantidad_usada
    if nueva_cantidad < 0:
        raise HTTPException(status_code=400, detail="No hay suficiente cantidad disponible.")

    # Actualiza
    cursor.execute("UPDATE inventario SET cantidad = %s WHERE id = %s", (nueva_cantidad, id))
    db.commit()
    cursor.close()
    db.close()

    return {"success": True, "restante": nueva_cantidad}

@app.get("/inventario/pdf")
def generar_pdf_inventario():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario")
    inventario = cursor.fetchall()
    cursor.close()
    db.close()

    # Crear archivo PDF temporal
    pdf_path = "inventario.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "📋 Reporte de Inventario - Cafetería")

    # Fecha
    c.setFont("Helvetica", 10)
    c.drawString(400, height - 50, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Encabezados
    y = height - 80
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Nombre")
    c.drawString(200, y, "Cantidad")
    c.drawString(270, y, "Unidad")
    c.drawString(350, y, "Estado")

    c.setFont("Helvetica", 10)
    y -= 20

    for item in inventario:
        if y < 60:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Nombre")
            c.drawString(200, y, "Cantidad")
            c.drawString(270, y, "Unidad")
            c.drawString(350, y, "Estado")
            c.setFont("Helvetica", 10)
            y -= 20

        cantidad = item['cantidad']
        estado = ""

        if cantidad < 2:
            estado = "❌ Muy bajo"
        elif 2 <= cantidad <= 4:
            estado = "⚠️ Rellenar stock"
        else:
            estado = "✅ Bien"

        # Mostrar fila
        c.drawString(50, y, item["nombre"])
        c.drawString(200, y, f"{cantidad:.2f}")
        c.drawString(270, y, item["unidad"])
        c.drawString(350, y, estado)

        y -= 20

    c.save()

    return FileResponse(pdf_path, media_type='application/pdf', filename="inventario.pdf")
