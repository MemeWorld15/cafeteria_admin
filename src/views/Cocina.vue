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

    <!-- Main -->
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

      <!-- Órdenes -->
      <main class="cocina-contenido" v-if="vista === 'ordenes'">
        <h2>Órdenes - Café</h2>
        <table class="tabla-ordenes">
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Productos</th>
              <th>Fecha</th>
              <th>Hora</th>
              <th>Status</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="orden in ordenes" :key="orden.id">
              <td>{{ orden.cliente }}</td>
              <td>
                <ul>
                  <li v-for="prod in orden.productos" :key="prod.id">
                    {{ prod.cantidad }} x {{ prod.nombre_producto }}
                  </li>
                </ul>
              </td>
              <td>{{ orden.fecha }}</td>
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
                  Entregar
                </button>
                <span v-else class="entregado-msg">✅</span>
              </td>
            </tr>
          </tbody>
        </table>
      </main>

      <!-- Menú -->
      <main class="cocina-contenido" v-if="vista === 'menu'">
        <h2>Gestión de Platillos</h2>

        <!-- Agregar nuevo -->
        <form @submit.prevent="agregarProducto" class="form-agregar">
          <input v-model="nuevoProducto.nombre" placeholder="Nombre" required />
          <input v-model="nuevoProducto.descripcion" placeholder="Descripción" required />
          <input type="number" step="0.01" v-model="nuevoProducto.precio" placeholder="Precio" required />
          <button type="submit">Agregar</button>
        </form>

        <table class="tabla-ordenes">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Precio</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prod in productos" :key="prod.id">
              <td>
                <template v-if="prod.editando">
                  <input v-model="prod.nombre" />
                </template>
                <template v-else>
                  {{ prod.nombre }}
                </template>
              </td>
              <td>
                <template v-if="prod.editando">
                  <input v-model="prod.descripcion" />
                </template>
                <template v-else>
                  {{ prod.descripcion }}
                </template>
              </td>
              <td>
                <template v-if="prod.editando">
                  <input type="number" step="0.01" v-model="prod.precio" />
                </template>
                <template v-else>
                  ${{ prod.precio }}
                </template>
              </td>
              <td>
                <span :class="prod.disponible ? 'activo' : 'inactivo'">
                  {{ prod.disponible ? 'Disponible' : 'Agotado' }}
                </span>
              </td>
              <td>
                <template v-if="prod.editando">
                  <button @click="guardarEdicion(prod)">Guardar</button>
                  <button @click="cancelarEdicion(prod)">Cancelar</button>
                </template>
                <template v-else>
                  <button @click="iniciarEdicion(prod)">✏️</button>
                  <button @click="toggleDisponible(prod.id)">
                    {{ prod.disponible ? 'Desactivar' : 'Activar' }}
                  </button>
                  <button @click="eliminarProducto(prod.id)">🗑️</button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import logo from '../assets/images/LogoCafe.png'
import {
  fetchOrdenes,
  fetchProductos,
  agregarProductoApi,
  actualizarProductoApi,
  eliminarProductoPorId,
  toggleDisponibilidadProducto,
  marcarOrdenComoEntregada
} from '../api'

const vista = ref('menu')
const ordenes = ref([])
const productos = ref([])
const mostrarDropdown = ref(false)
const nombreUsuario = ref('')
const rolUsuario = ref('')
const nuevoProducto = ref({ nombre: '', descripcion: '', precio: '' })

const toggleDarkMode = () => {
  document.body.classList.toggle('dark-mode')
}
const toggleDropdown = () => {
  mostrarDropdown.value = !mostrarDropdown.value
}
const cerrarSesion = () => {
  localStorage.clear()
  window.location.href = '/'
}

const cargarOrdenes = async () => {
  ordenes.value = await fetchOrdenes()
}
const obtenerProductos = async () => {
  const data = await fetchProductos()
  productos.value = data.map(p => ({ ...p, editando: false }))
}
const marcarEntregado = async (id) => {
  await marcarOrdenComoEntregada(id)
  await cargarOrdenes()
}
const agregarProducto = async () => {
  const res = await agregarProductoApi({ ...nuevoProducto.value })
  if (res.ok) {
    nuevoProducto.value = { nombre: '', descripcion: '', precio: '' }
    await obtenerProductos()
  }
}
const iniciarEdicion = (p) => {
  p.editando = true
  p._backup = { nombre: p.nombre, descripcion: p.descripcion, precio: p.precio }
}
const cancelarEdicion = (p) => {
  Object.assign(p, p._backup)
  p.editando = false
}
const guardarEdicion = async (p) => {
  const res = await actualizarProductoApi(p.id, {
    nombre: p.nombre,
    descripcion: p.descripcion,
    precio: p.precio
  })
  if (res.ok) {
    p.editando = false
    await obtenerProductos()
  }
}
const eliminarProducto = async (id) => {
  if (confirm('¿Eliminar este producto?')) {
    await eliminarProductoPorId(id)
    await obtenerProductos()
  }
}
const toggleDisponible = async (id) => {
  await toggleDisponibilidadProducto(id)
  await obtenerProductos()
}

onMounted(() => {
  nombreUsuario.value = localStorage.getItem('usuario_nombre') || 'Usuario'
  rolUsuario.value = localStorage.getItem('usuario_rol') || ''
  cargarOrdenes()
  obtenerProductos()
})
</script>

<style scoped>
.form-agregar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
input {
  padding: 5px;
}
button {
  padding: 6px 12px;
  border: none;
  cursor: pointer;
}
.activo {
  color: green;
  font-weight: bold;
}
.inactivo {
  color: red;
  font-weight: bold;
}
.entregado-msg {
  color: green;
}
</style>
