<template>
  <div class="cocina-app">
    <!--prueba  Topbar -->
    <header class="cocina-topbar">
      <div class="cocina-logo">
        <img :src="logo" alt="Logo" />
        <span class="cocina-brand">Cafetería</span>
      </div>
      <div class="cocina-user" @click="toggleDropdown">
        <i class="fas fa-sun" @click.stop="toggleDarkMode"></i>
        <i class="fas fa-bell"></i>
        <i class="fas fa-user"></i>
        <div class="cocina-user-info">
          <span class="cocina-usuario">{{ nombreUsuario }}</span><br />
          <span class="cocina-rol">{{ rolUsuario }}</span>
        </div>
        <i class="fas fa-chevron-down"></i>
        <div v-if="mostrarDropdown" class="dropdown-menu" @click.stop>
          <p>{{ nombreUsuario }}</p>
          <hr />
          <button @click="cerrarSesion">Cerrar sesión</button>
        </div>
      </div>
    </header>

    <div class="cocina-main">
      <!-- Sidebar -->
      <aside class="cocina-sidebar">
        <ul>
          <li :class="{ active: vista === 'menu' }" @click="vista = 'menu'">
            <i class="fas fa-utensils"></i><span>Menú</span>
          </li>
          <li :class="{ active: vista === 'ordenes' }" @click="vista = 'ordenes'">
            <i class="fas fa-receipt"></i><span>Órdenes</span>
          </li>
        </ul>
      </aside>

      <!-- Vista Órdenes con separación -->
      <main class="cocina-contenido" v-if="vista === 'ordenes'">
        <h2>📋 Órdenes - Café</h2>
        <div v-if="!hayOrdenesPendientes">
              <p>No hay órdenes pendientes en este momento. 💤</p>
            </div>
        <!-- Órdenes por realizar -->
        <section class="bloque-seccion">
          <h3 class="seccion-title">🕒 Órdenes por realizar</h3>
          <!--<script setu" :key="'pend-' + fecha">-->
            <div v-for="(turnos, fecha) in ordenesAgrupadas" :key="'pend-' + fecha">
            <div v-for="(ordenesTurno, turno) in turnos" :key="'pend-' + turno + fecha">
              <div v-if="ordenesTurno.some(o => !o.entregado)">
                <h4 class="fecha-turno">📅 {{ formatFecha(fecha) }} — 🕐 {{ turno }}</h4>
                <div class="scroll-tabla">
                  <table class="tabla-ordenes">
                    <thead>
                      <tr>
                        <th>Cliente</th>
                        <th>Productos</th>
                        <th>Notas</th>
                        <th>Hora</th>
                        <th>Status</th>
                        <th>Acción</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="orden in ordenesTurno.filter(o => !o.entregado && !o.cancelada)" :key="orden.id">
                        <td><strong>{{ orden.cliente }}</strong></td>
                        <td>
                          <ul>
                            <li v-for="prod in orden.productos" :key="prod.id">
                              {{ prod.cantidad }} x {{ prod.nombre_producto }}
                            </li>
                          </ul>
                        </td>
                        <td>{{ orden.nota || 'Sin Notas' }}</td>
                        <td>{{ orden.hora }}</td>
                        <td><span class="estado no-entregado">En espera</span></td>
                        <td>
                          <button @click="marcarEntregado(orden.id)" class="btn-entregar">Marcar como entregado</button>
                          <button @click="cancelarOrdenChef(orden.id)" class="btn-cancelar">Cancelar</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Órdenes entregadas -->
        <section class="bloque-seccion">
          <h3 class="seccion-title">✅ Órdenes entregadas</h3>
          <div v-for="(turnos, fecha) in ordenesAgrupadas" :key="'ent-' + fecha">
          
            <div v-for="(ordenesTurno, turno) in turnos" :key="'ent-' + turno + fecha">
              <div v-if="ordenesTurno.some(o => o.entregado)">
                <h4 class="fecha-turno">📅 {{ formatFecha(fecha) }} — 🕐 {{ turno }}</h4>
                <div class="scroll-tabla">
                  <table class="tabla-ordenes">
                    <thead>
                      <tr>
                        <th>Cliente</th>
                        <th>Productos</th>
                        <th>Nota</th>
                        <th>Hora</th>
                        <th>Status</th>
                        <th>Acción</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="orden in ordenesTurno.filter(o => o.entregado)" :key="orden.id">
                        <td><strong>{{ orden.cliente }}</strong></td>
                        <td>
                          <ul>
                            <li v-for="prod in orden.productos" :key="prod.id">
                              {{ prod.cantidad }} x {{ prod.nombre_producto }}
                            </li>
                          </ul>
                        </td>
                        <td>{{ orden.nota || '-' }}</td>
                        <td>{{ orden.hora }}</td>
                        <td>
                          <span v-if="orden.cancelada" class="estado cancelada">Cancelada</span>
                          <span v-else class="estado entregado">Entregado</span>
                        </td>

                        <td><span class="entregado-msg">✅ Entregado</span></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <!-- Vista Menú -->
      <main class="cocina-contenido" v-if="vista === 'menu'">
        <h2>Menú de Productos</h2>

        <h3>Agregar Platillo</h3>
        <form @submit.prevent="crearProductoNuevo" class="form-platillo">
          <input v-model="nuevoProducto.nombre" placeholder="Nombre" required />
          <textarea v-model="nuevoProducto.descripcion" placeholder="Descripción" required />
          <input v-model="nuevoProducto.precio" type="number" min="0.01" step="0.01" placeholder="Precio" required />
          <select v-model="nuevoProducto.categoria_id" required>
            <option disabled value="">Seleccionar categoría</option>
            <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
          </select>
          <button type="submit">Agregar</button>
        </form>
        <p v-if="mensaje" :style="{ color: mensajeColor }">{{ mensaje }}</p>

        <table class="tabla-ordenes">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Precio</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prod in productos" :key="prod.id">
              <td>{{ prod.nombre }}</td>
              <td>{{ categoriaNombre(prod.categoria_id) }}</td>
              <td>${{ prod.precio }}</td>
              <td>
                <span :class="prod.disponible ? 'activo' : 'inactivo'">
                  {{ prod.disponible ? 'Disponible' : 'Agotado' }}
                </span>
              </td>
              <td>
                <button @click="abrirEditar(prod)">Editar</button>
                <button @click="toggleDisponible(prod.id)">
                  {{ prod.disponible ? 'Marcar Agotado' : 'Marcar Disponible' }}
                </button>
                <button @click="eliminarProducto(prod.id)">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Modal de edición -->
        <div v-if="editandoProducto" class="modal-overlay" @click.self="cerrarModal">
          <div class="modal">
            <h3>Editar Platillo</h3>
            <form @submit.prevent="guardarEdicion">
              <input v-model="editandoProducto.nombre" required />
              <textarea v-model="editandoProducto.descripcion" required />
              <input v-model="editandoProducto.precio" type="number" min="0.01" step="0.01" required />
              <select v-model="editandoProducto.categoria_id" required>
                <option disabled value="">Seleccionar categoría</option>
                <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
              </select>
              <div class="modal-buttons">
                <button type="submit">Guardar</button>
                <button type="button" @click="cerrarModal">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'

import logo from '../assets/images/LogoCafe.png'
import {
  fetchOrdenes,
  fetchProductos,
  fetchCategorias,
  toggleDisponibilidadProducto,
  eliminarProductoPorId,
  marcarOrdenComoEntregada,
  crearProducto,
  actualizarProducto,
  cancelarOrdenChef
} from '../api'

const vista = ref('ordenes')
const ordenes = ref([])
const productos = ref([])
const categorias = ref([])
const nuevoProducto = ref({ nombre: '', descripcion: '', precio: '', categoria_id: '' })
const editandoProducto = ref(null)
const nombreUsuario = ref('')
const rolUsuario = ref('')
const mostrarDropdown = ref(false)
const mensaje = ref('')
const mensajeColor = ref('green')
const cancelarOrdenChef = async (id) => {
  if (!confirm("¿Seguro que deseas cancelar esta orden?")) return;
  try {
    const res = await cancelarOrdenCocina(id);
    if (res.success) {
      alert(res.message || "✅ Orden cancelada correctamente.");
      await cargarOrdenes();
    } else {
      alert("❌ Error al cancelar la orden.");
    }
  } catch (error) {
    alert("❌ Error al cancelar la orden.");
    console.error(error);
  }
};

//ver si hay ordenes 
const hayOrdenesPendientes = computed(() => {
  for (const fecha in ordenesAgrupadas.value) {
    for (const turno in ordenesAgrupadas.value[fecha]) {
      if (ordenesAgrupadas.value[fecha][turno].some(o => !o.entregado && !o.cancelada)) {
        return true;
      }
    }
  }
  return false;
});


const ordenesAgrupadas = computed(() => {
  const agrupadas = {}
  ordenes.value.forEach(o => {
    const fecha = o.fecha
    const hora = parseInt(o.hora.split(':')[0])
    let turno = ''
    if (hora >= 6 && hora < 14) turno = 'Mañana'
    else if (hora >= 14 && hora < 22) turno = 'Tarde'
    else turno = 'Noche'

    if (!agrupadas[fecha]) agrupadas[fecha] = {}
    if (!agrupadas[fecha][turno]) agrupadas[fecha][turno] = []
    agrupadas[fecha][turno].push(o)
  })
  return agrupadas
})

const toggleDarkMode = () => document.body.classList.toggle('dark-mode')
const toggleDropdown = () => (mostrarDropdown.value = !mostrarDropdown.value)
const cerrarSesion = () => {
  localStorage.clear()
  window.location.href = '/'
}

const cargarOrdenes = async () => {
  const data = await fetchOrdenes()
  ordenes.value = data.map(ord => {
    const fechaObj = new Date(ord.fecha)
    return {
      ...ord,
      hora: fechaObj.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      })
    }
  })
}

const formatFecha = fechaStr => {
  const fechaObj = new Date(fechaStr)
  return fechaObj.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const obtenerProductos = async () => {
  productos.value = await fetchProductos()
}
const obtenerCategorias = async () => {
  categorias.value = await fetchCategorias()
}
const categoriaNombre = id => categorias.value.find(c => c.id === id)?.nombre || '—'

const crearProductoNuevo = async () => {
  mensaje.value = ''
  const p = parseFloat(nuevoProducto.value.precio)
  if (isNaN(p) || p <= 0) {
    mensaje.value = 'Precio debe ser > 0'
    mensajeColor.value = 'red'
    setTimeout(() => (mensaje.value = ''), 3000)
    return
  }
  try {
    const fd = new FormData()
    Object.entries(nuevoProducto.value).forEach(([k, v]) => fd.append(k, v))
    await crearProducto(fd)
    mensaje.value = '✅ Agregado'
    mensajeColor.value = 'green'
    Object.assign(nuevoProducto.value, { nombre: '', descripcion: '', precio: '', categoria_id: '' })
    await obtenerProductos()
  } catch {
    mensaje.value = '❌ Error al agregar'
    mensajeColor.value = 'red'
  }
  setTimeout(() => (mensaje.value = ''), 3000)
}

const toggleDisponible = async id => {
  await toggleDisponibilidadProducto(id)
  await obtenerProductos()
}

const eliminarProducto = async id => {
  if (!confirm('¿Eliminar este platillo?')) return
  await eliminarProductoPorId(id)
  await obtenerProductos()
}

const abrirEditar = prod => (editandoProducto.value = { ...prod })
const cerrarModal = () => (editandoProducto.value = null)

const guardarEdicion = async () => {
  const p = editandoProducto.value
  const price = parseFloat(p.precio)
  if (isNaN(price) || price <= 0) {
    mensaje.value = 'Precio debe ser > 0'
    mensajeColor.value = 'red'
    setTimeout(() => (mensaje.value = ''), 3000)
    return
  }
  try {
    const fd = new FormData()
    Object.entries(p).forEach(([k, v]) => fd.append(k, v))
    await actualizarProducto(p.id, fd)
    mensaje.value = '✅ Actualizado'
    mensajeColor.value = 'green'
    await obtenerProductos()
    cerrarModal()
  } catch {
    mensaje.value = '❌ Error al actualizar'
    mensajeColor.value = 'red'
  }
  setTimeout(() => (mensaje.value = ''), 3000)
}

const marcarEntregado = async id => {
  try {
    const res = await marcarOrdenComoEntregada(id)
    if (res.ok) {
      await cargarOrdenes()
      alert('✅ Orden entregada')
    } else alert('❌ Error al entregar')
  } catch {
    alert('❌ Error al entregar')
  }
}


onMounted(() => {
  if (localStorage.getItem('usuario_rol') !== 'chef') {
    window.location.href = '/login'
    return
  }
  nombreUsuario.value = localStorage.getItem('usuario_nombre') || 'Usuario'
  rolUsuario.value = 'Chef'
  cargarOrdenes()
  obtenerProductos()
  obtenerCategorias()
  // Actualización automática de órdenes cada 5 segundos
setInterval(() => {
  cargarOrdenes()
}, 5000)

})
</script>

<style scoped>
/* Estructura principal */
.cocina-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #fff;
}
.cocina-topbar {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 10;
}
.cocina-logo {
  display: flex;
  align-items: center;
}
.cocina-logo img {
  height: 30px;
  margin-right: 10px;
}
.cocina-brand {
  font-weight: bold;
  font-size: 1.2rem;
}
.cocina-user {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 10px;
  position: relative;
}
.cocina-user-info {
  display: inline-block;
  text-align: right;
  font-size: 13px;
}
.dropdown-menu {
  position: absolute;
  right: 0;
  top: 40px;
  background: white;
  border: 1px solid #ccc;
  padding: 10px;
  z-index: 5;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
.cocina-main {
  display: flex;
  flex: 1;
}
.cocina-sidebar {
  width: 200px;
  background: #f0f0f0;
  padding: 1rem;
}
.cocina-sidebar ul {
  list-style: none;
  padding: 0;
}
.cocina-sidebar li {
  padding: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.cocina-sidebar li.active {
  background: #ddd;
  font-weight: bold;
}
.cocina-sidebar li i {
  margin-right: 8px;
}
.cocina-contenido {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

/* Tablas de órdenes */
.tabla-ordenes {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.5rem;
}
.tabla-ordenes th,
.tabla-ordenes td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

/* Estados */
.estado {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}
.no-entregado {
  background: #ffe0b2;
  color: #c87f00;
}
.entregado {
  background: #c8e6c9;
  color: #2e7d32;
}
.entregado-msg {
  color: #2e7d32;
  font-weight: bold;
}

/* Botones */
.btn-entregar {
  background-color: #0a9f67;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-entregar:hover {
  background: #098658;
}

/* Bloques de fecha y turno */
.bloque-fecha {
  margin-bottom: 2rem;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 8px;
}
.fecha-title {
  color: #333;
  margin-bottom: 0.5rem;
}
.turno-title {
  margin-top: 1rem;
  font-weight: bold;
  color: #444;
}
h5 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  font-weight: bold;
  color: #333;
}

/* Scroll horizontal en tablas */
.scroll-tabla {
  overflow-x: auto;
}

/* Formulario de productos */
.form-platillo {
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 500px;
}
.form-platillo input,
textarea,
select {
  padding: 8px;
  font-size: 1rem;
}
.form-platillo button {
  background: #0a9f67;
  color: white;
  padding: 8px;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

/* Modal edición de producto */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal {
  background: white;
  padding: 20px;
  border-radius: 6px;
  width: 90%;
  max-width: 400px;
}
.modal-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}
.modal-buttons button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.modal-buttons button:first-child {
  background: #0a9f67;
  color: white;
}
.modal-buttons button:last-child {
  background: #ccc;
}

/* Estado de disponibilidad en menú */
.activo {
  color: green;
  font-weight: bold;
}
.inactivo {
  color: red;
  font-weight: bold;
}
.cancelada {
  background: #ffcdd2;
  color: #b71c1c;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}


</style>
