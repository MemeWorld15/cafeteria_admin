<template>
  <div class="cocina-app">
    <!-- Topbar -->
    <header class="cocina-topbar">
      <div class="cocina-logo">
        <img :src="logo" alt="Logo" />
        <span class="cocina-brand">Cafetería</span>
      </div>
      <div class="cocina-user" @click="toggleDropdown">
        <i class="fas fa-sun" @click="toggleDarkMode"></i>
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
          <li :class="{ active: vista === 'caja' }" @click="vista = 'caja'">
            <i class="fas fa-cash-register"></i><span>Caja</span>
          </li>
        </ul>
      </aside>

      <!-- Vista Órdenes -->
      <main class="cocina-contenido" v-if="vista === 'ordenes'">
        <h2>Órdenes - Café</h2>
        <div v-for="(turnos, fecha) in ordenesAgrupadas" :key="fecha" class="bloque-fecha">
          <h3 class="fecha-title">📅 {{ fecha }}</h3>
          <div v-for="(ordenesTurno, turno) in turnos" :key="turno" class="bloque-turno">
            <h4 class="turno-title">🕐 Turno: {{ turno }}</h4>
            <div class="scroll-tabla">
              <table class="tabla-ordenes">
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Productos</th>
                    <th>Mesa</th>
                    <th>Hora</th>
                    <th>Status</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="orden in ordenesTurno" :key="orden.id">
                    <td><strong>{{ orden.cliente }}</strong></td>
                    <td>
                      <ul>
                        <li v-for="prod in orden.productos" :key="prod.id">
                          {{ prod.cantidad }} x {{ prod.nombre_producto }}
                        </li>
                      </ul>
                    </td>
                    <td>-</td>
                    <td>{{ orden.hora }}</td>
                    <td>
                      <span :class="['estado', orden.entregado ? 'entregado' : 'no-entregado']">
                        {{ orden.entregado ? 'Entregado' : 'En espera' }}
                      </span>
                    </td>
                    <td>
                      <button
                        v-if="!orden.entregado"
                        @click="marcarEntregado(orden.id)"
                        class="btn-entregar"
                      >
                        Marcar como entregado
                      </button>
                      <span v-else class="entregado-msg">✅ Entregado</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <!-- Vista Menú -->
      <main class="cocina-contenido" v-if="vista === 'menu'">
        <h2>Menú de Productos</h2>

        <h3>Agregar Platillo</h3>
        <form @submit.prevent="crearProductoNuevo" class="form-platillo">
          <input v-model="nuevoProducto.nombre" placeholder="Nombre" required />
          <textarea v-model="nuevoProducto.descripcion" placeholder="Descripción" required />
          <input
            v-model="nuevoProducto.precio"
            type="number"
            min="0.01"
            step="0.01"
            placeholder="Precio"
            required
          />
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
              <input
                v-model="editandoProducto.precio"
                type="number"
                min="0.01"
                step="0.01"
                required
              />
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

      <!-- Vista Caja -->
      <main class="cocina-contenido" v-if="vista === 'caja'">
        <Caja />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import logo from '../assets/images/LogoCafe.png'
import '../EstilosCss/cocinastyle.css'
import Caja from './Caja.vue'

import {
  fetchOrdenes,
  fetchProductos,
  fetchCategorias,
  toggleDisponibilidadProducto,
  eliminarProductoPorId,
  marcarOrdenComoEntregada,
  crearProducto,
  actualizarProducto
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
  ordenes.value = await fetchOrdenes()
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
})
</script>


<style scoped>
.entregado-msg {
  color: green;
  font-weight: bold;
}
.btn-entregar {
  background: #0a9f67;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-entregar:hover {
  background: #098658;
}
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
</style>
