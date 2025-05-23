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


app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cafeteria-admin.vercel.app"],  # Dominio de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Ruta de prueba
@app.get("/")
def root():
    return {"message": "¡La API está funcionando correctamente!"}

# Ruta de login
@app.post("/login")
def login(correo: str = Form(...), contraseña: str = Form(...)):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT id, rol, nombre FROM usuarios WHERE correo=%s AND contraseña=%s", (correo, contraseña))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        return {
            "success": True,
            "rol": user[1],
            "usuario_id": user[0],
            "nombre": user[2]
        }
    raise HTTPException(status_code=401, detail="Credenciales inválidas")


# Solo ejecuta esto si se llama directamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Usa el puerto de Render o 8000 por defecto local
    uvicorn.run(app, host="0.0.0.0", port=port)

# MODELOS Pydantic
class ProductoOrden(BaseModel):
    nombre: str
    cantidad: int
    precio: float

class OrdenEntrada(BaseModel):
    cliente: str
    nota: str = ""
    usuario_id: Optional[int]
    productos: List[ProductoOrden]


@app.post("/login")
def login(correo: str = Form(...), contraseña: str = Form(...)):
    db = get_db_connection()
    #cursor = db.cursor(dictionary=True)
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE correo=%s AND contraseña=%s", (correo, contraseña))
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


# REGISTER
@app.post("/register")
def register(
    nombre: str = Form(...),
    correo: str = Form(...),
    contraseña: str = Form(...),
    grado: str = Form(...),
    carrera: str = Form(...)
):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contraseña, grado, carrera, rol) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, correo, contraseña, grado, carrera, 'cliente')
        )
        db.commit()
        return {"success": True}
    except mysql.connector.Error:
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    finally:
        cursor.close()
        db.close()


@app.post("/empleados")
def crear_empleado(
    nombre: str = Form(...),
    correo: str = Form(...),
    ocupacion: str = Form(...),
    rendimiento: str = Form(...),
    contraseña: str = Form(...),
    creado_por: int = Form(...)
):
    db = get_db_connection()
    cursor = db.cursor()

    foto = f"https://i.pravatar.cc/150?img={abs(hash(correo)) % 70 + 1}"

    try:
        # Insertar en empleados
        cursor.execute("""
            INSERT INTO empleados (nombre, correo, ocupacion, rendimiento, contraseña, foto, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, correo, ocupacion, rendimiento, contraseña, foto, creado_por))

        # Si es chef, también lo insertamos como usuario
        if ocupacion.lower() == "chef":
            cursor.execute("""
                INSERT INTO usuarios (nombre, correo, contraseña, grado, carrera, rol)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, correo, contraseña, "-", "-", "chef"))

        db.commit()
        return {"success": True}
    except mysql.connector.Error as e:
        db.rollback()
        print("Error:", e)
        raise HTTPException(status_code=400, detail="Error al registrar empleado/usuario")
    finally:
        cursor.close()
        db.close()


@app.get("/empleados")
def obtener_empleados():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM empleados")
    empleados = cursor.fetchall()
    cursor.close()
    db.close()
    return empleados

# MENU
@app.get("/menu")
def obtener_menu():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
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

# CATEGORÍAS
@app.get("/categorias")
def listar_categorias():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()
    db.close()
    return categorias

@app.post("/categorias")
def agregar_categoria(nombre: str = Form(...)):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (nombre,))
        db.commit()
        return {"success": True}
    except mysql.connector.Error:
        raise HTTPException(status_code=400, detail="Categoría ya existe")
    finally:
        cursor.close()
        db.close()

@app.put("/categorias/{categoria_id}")
def editar_categoria(categoria_id: int, nombre: str = Form(...)):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE categorias SET nombre = %s WHERE id = %s", (nombre, categoria_id))
        db.commit()
        return {"success": True}
    except mysql.connector.Error:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la categoría")
    finally:
        cursor.close()
        db.close()

@app.delete("/categorias/{categoria_id}")
def eliminar_categoria(categoria_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM categorias WHERE id = %s", (categoria_id,))
        db.commit()
        return {"success": True}
    except mysql.connector.Error:
        raise HTTPException(status_code=400, detail="No se pudo eliminar la categoría")
    finally:
        cursor.close()
        db.close()

# PRODUCTOS
@app.post("/productos")
def agregar_producto(nombre: str = Form(...), descripcion: str = Form(...), precio: float = Form(...), categoria_id: int = Form(...)):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO productos (nombre, descripcion, precio, categoria_id) VALUES (%s, %s, %s, %s)",
                   (nombre, descripcion, precio, categoria_id))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

@app.put("/productos/{producto_id}")
def editar_producto(
    producto_id: int,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    precio: float = Form(...),
    categoria_id: int = Form(...),
):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE productos 
            SET nombre = %s, descripcion = %s, precio = %s, categoria_id = %s 
            WHERE id = %s
        """, (nombre, descripcion, precio, categoria_id, producto_id))
        db.commit()
        return {"success": True}
    except mysql.connector.Error:
        raise HTTPException(status_code=400, detail="Error al actualizar producto")
    finally:
        cursor.close()
        db.close()

@app.get("/productos")
def listar_productos():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    db.close()
    return productos

# ORDENES

@app.post("/ordenar")
def crear_orden(data: OrdenEntrada):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO ordenes (cliente, nota, usuario_id, entregado) VALUES (%s, %s, %s, %s)",
            (data.cliente, data.nota, data.usuario_id, False)
        )
        orden_id = cursor.lastrowid

        for prod in data.productos:
            cursor.execute("""
                INSERT INTO orden_productos (orden_id, nombre_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (orden_id, prod.nombre, prod.cantidad, prod.precio))

        db.commit()
        return {"success": True, "orden_id": orden_id}
    except mysql.connector.Error:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al registrar la orden")
    finally:
        cursor.close()
        db.close()

@app.get("/ordenes")
def listar_ordenes():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ordenes ORDER BY id DESC")
    ordenes = cursor.fetchall()

    for orden in ordenes:
        cursor.execute("SELECT * FROM orden_productos WHERE orden_id = %s", (orden["id"],))
        productos = cursor.fetchall()
        orden["productos"] = productos

        if isinstance(orden["fecha"], datetime):
            orden["hora"] = orden["fecha"].strftime("%I:%M %p")
            orden["fecha"] = orden["fecha"].strftime("%d-%m-%Y")
        else:
            orden["hora"] = "N/A"

    cursor.close()
    db.close()
    return ordenes

@app.put("/ordenes/{orden_id}/entregado")
def marcar_entregado(orden_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE ordenes SET entregado = 1 WHERE id = %s", (orden_id,))
        db.commit()
        return {"success": True}
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar el estado de la orden")
    finally:
        cursor.close()
        db.close()

# NUEVA RUTA: CANCELAR ORDEN
@app.delete("/ordenes/{orden_id}")
def cancelar_orden(orden_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT fecha, entregado FROM ordenes WHERE id = %s", (orden_id,))
        orden = cursor.fetchone()

        if not orden:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        if orden["entregado"]:
            raise HTTPException(status_code=400, detail="La orden ya fue entregada")

        tiempo_creacion = orden["fecha"]
        ahora = datetime.now()

        if (ahora - tiempo_creacion) > timedelta(minutes=2):
            raise HTTPException(status_code=403, detail="La orden ya no se puede cancelar")

        cursor.execute("DELETE FROM ordenes WHERE id = %s", (orden_id,))
        db.commit()
        return {"success": True, "message": "Orden cancelada"}
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo cancelar la orden")
    finally:
        cursor.close()
        db.close()

@app.get("/productos")
def listar_productos():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    db.close()
    return productos
@app.put("/productos/{producto_id}/toggle-disponible")
def toggle_disponibilidad(producto_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE productos SET disponible = NOT disponible WHERE id = %s", (producto_id,))
        db.commit()
        return {"success": True}
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo cambiar disponibilidad")
    finally:
        cursor.close()
        db.close()
@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
        db.commit()
        return {"success": True}
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo eliminar el producto")
    finally:
        cursor.close()
        db.close()


@app.get("/ventas")
def obtener_ventas():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM ordenes WHERE entregado = 1 ORDER BY fecha DESC")
    ventas = cursor.fetchall()

    for orden in ventas:
        cursor.execute("SELECT * FROM orden_productos WHERE orden_id = %s", (orden["id"],))
        productos = cursor.fetchall()
        orden["productos"] = productos
        orden["total"] = sum(p["cantidad"] * float(p["precio_unitario"]) for p in productos)

        if isinstance(orden["fecha"], datetime):
            orden["fecha"] = orden["fecha"].strftime("%d-%m-%Y")
            orden["hora"] = orden["fecha"].strftime("%I:%M %p")
        else:
            orden["hora"] = "N/A"

    cursor.close()
    db.close()
    return ventas

@app.get("/ordenes/cliente/{usuario_id}")
def obtener_ordenes_cliente(usuario_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM ordenes WHERE usuario_id = %s ORDER BY id DESC", (usuario_id,))
        ordenes = cursor.fetchall()

        for orden in ordenes:
            cursor.execute("SELECT * FROM orden_productos WHERE orden_id = %s", (orden["id"],))
            productos = cursor.fetchall()
            orden["productos"] = productos

            if isinstance(orden["fecha"], datetime):
                orden["hora"] = orden["fecha"].strftime("%I:%M %p")
                orden["fecha_mostrada"] = orden["fecha"].strftime("%d-%m-%Y")
                # ✨ Importante: mantenemos orden["fecha"] como datetime real
            else:
                orden["hora"] = "N/A"
                orden["fecha_mostrada"] = "N/A"

        return ordenes
    finally:
        cursor.close()
        db.close()

@app.get("/graficas/top-productos")
def productos_mas_pedidos():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT nombre_producto, SUM(cantidad) AS total_pedidos
            FROM orden_productos
            GROUP BY nombre_producto
            ORDER BY total_pedidos DESC
        """)
        resultados = cursor.fetchall()
        return resultados
    finally:
        cursor.close()
        db.close()


@app.get("/graficas/top-clientes")
def clientes_top():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT cliente, COUNT(*) AS total_ordenes
            FROM ordenes
            GROUP BY cliente
            ORDER BY total_ordenes DESC
        """)
        resultados = cursor.fetchall()
        return resultados
    finally:
        cursor.close()
        db.close()
@app.get("/productos/menos-pedido")
def producto_menos_pedido():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Sumamos las cantidades por producto
    cursor.execute("""
        SELECT nombre_producto, SUM(cantidad) AS total_vendidos
        FROM orden_productos
        GROUP BY nombre_producto
        ORDER BY total_vendidos ASC
        LIMIT 1
    """)
    resultado = cursor.fetchone()

    cursor.close()
    db.close()

    return resultado or {"nombre_producto": "N/A", "total_vendidos": 0}

from fastapi import Form

# Unidades válidas
UNIDADES_VALIDAS = {"kg", "g", "l", "ml", "piezas", "unidad", "taza"}

# Conexión
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        sslmode="require"
    )

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
