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
          <p class="usuario-nombre">{{ nombreUsuario }}</p>
          <hr />
          <button @click="cerrarSesion">Cerrar sesión</button>
        </div>
      </div>
    </header>

    <!-- Main Body -->
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
        <div class="cocina-settings">
          <i class="fas fa-cog"></i><span>Configuración</span>
        </div>
      </aside>

      <!-- Órdenes -->
      <main class="cocina-contenido" v-if="vista === 'ordenes'">
        <!-- ... -->
      </main>

      <!-- Menú -->
      <main class="cocina-contenido" v-if="vista === 'menu'">
        <h2>Menú de Productos</h2>

        <!-- Agregar Platillo -->
        <h3>Agregar Platillo</h3>
        <form @submit.prevent="crearProductoNuevo" class="form-platillo">
          <input v-model="nuevoProducto.nombre" type="text" placeholder="Nombre del platillo" required />
          <textarea v-model="nuevoProducto.descripcion" placeholder="Descripción del platillo" required></textarea>
          <input v-model="nuevoProducto.precio" type="number" min="0.01" step="0.01" placeholder="Precio" required />
          <select v-model="nuevoProducto.categoria_id" required>
            <option disabled value="">Seleccionar categoría</option>
            <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
          </select>
          <button type="submit">Agregar</button>
        </form>

        <p v-if="mensaje" :style="{ color: mensajeColor }">{{ mensaje }}</p>

        <!-- Tabla de productos -->
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

        <!-- Modal edición -->
        <div v-if="editandoProducto" class="modal-overlay" @click.self="cerrarModal">
          <div class="modal">
            <h3>Editar Platillo</h3>
            <form @submit.prevent="guardarEdicion">
              <input v-model="editandoProducto.nombre" type="text" required />
              <textarea v-model="editandoProducto.descripcion" required></textarea>
              <input v-model="editandoProducto.precio" type="number" min="0.01" step="0.01" required />
              <select v-model="editandoProducto.categoria_id" required>
                <option disabled value="">Seleccionar categoría</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
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
import { ref, onMounted } from 'vue'
import logo from '../assets/images/LogoCafe.png'
import '../EstilosCss/cocinastyle.css'
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

const toggleDarkMode = () => document.body.classList.toggle('dark-mode')
const toggleDropdown = () => mostrarDropdown.value = !mostrarDropdown.value
const cerrarSesion = () => { localStorage.clear(); window.location.href = '/' }

const cargarOrdenes = async () => { ordenes.value = await fetchOrdenes() }
const obtenerProductos = async () => { productos.value = await fetchProductos() }
const obtenerCategorias = async () => { categorias.value = await fetchCategorias() }
const categoriaNombre = id => categorias.value.find(c => c.id === id)?.nombre || '—'

// Agregar producto
const crearProductoNuevo = async () => {
  mensaje.value = ''
  const precio = parseFloat(nuevoProducto.value.precio)
  if (!precio || precio <= 0) {
    mensaje.value = 'El precio debe ser > 0'
    mensajeColor.value = 'red'
    return
  }
  try {
    const fd = new FormData()
    Object.entries(nuevoProducto.value).forEach(([k,v]) => fd.append(k, v))
    await crearProducto(fd)
    mensaje.value = '✅ Agregado!'
    mensajeColor.value = 'green'
    nuevoProducto.value = { nombre: '', descripcion: '', precio: '', categoria_id: '' }
    await obtenerProductos()
  } catch {
    mensaje.value = '❌ Error al agregar'
    mensajeColor.value = 'red'
  }
  setTimeout(() => mensaje.value = '', 3000)
}

// Disponibilidad y eliminación
const toggleDisponible = async id => {
  await toggleDisponibilidadProducto(id)
  await obtenerProductos()
}
const eliminarProducto = async id => {
  if (!confirm('¿Eliminar este platillo?')) return
  await eliminarProductoPorId(id)
  await obtenerProductos()
}

// Editar
const abrirEditar = prod => editandoProducto.value = { ...prod }
const cerrarModal = () => editandoProducto.value = null
const guardarEdicion = async () => {
  const p = editandoProducto.value
  const precio = parseFloat(p.precio)
  if (!precio || precio <= 0) {
    mensaje.value = 'Precio debe ser > 0'
    mensajeColor.value = 'red'
    setTimeout(() => mensaje.value = '', 3000)
    return
  }
  try {
    const fd = new FormData()
    Object.entries(p).forEach(([k,v]) => fd.append(k, v))
    await actualizarProducto(p.id, fd)
    mensaje.value = '✅ Actualizado!'
    mensajeColor.value = 'green'
    await obtenerProductos()
    cerrarModal()
  } catch {
    mensaje.value = '❌ Error al actualizar'
    mensajeColor.value = 'red'
  }
  setTimeout(() => mensaje.value = '', 3000)
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
/* existing styles... */
.form-platillo { margin-bottom:2rem; display:flex; flex-direction:column; gap:10px; max-width:500px; }
.form-platillo input, textarea, select { padding:8px; font-size:1rem; }
.form-platillo button { background:#0a9f67;color:#fff;padding:8px;border:none;cursor:pointer;border-radius:4px; }

.modal-overlay { position:fixed; top:0; left:0; width:100%; height:100%; background:#00000066; display:flex; align-items:center; justify-content:center; }
.modal { background:#fff; padding:20px; border-radius:6px; width:90%; max-width:400px; }
.modal-buttons { display:flex; justify-content:space-between; margin-top:15px; }
.modal-buttons button { flex:1; margin:0 5px; padding:8px; cursor:pointer; border:none; border-radius:4px; }
.modal-buttons button:first-child { background:#0a9f67; color:#fff; }
.modal-buttons button:last-child { background:#ccc; }
</style>
