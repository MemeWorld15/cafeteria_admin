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
        <!-- Dropdown -->
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
        <h2>Órdenes - Café</h2>
        <div class="scroll-tabla">
          <table class="tabla-ordenes">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Productos</th>
                <th>Mesa</th>
                <th>Fecha</th>
                <th>Hora</th>
                <th>Status</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="orden in ordenes" :key="orden.id">
                <td><strong>{{ orden.cliente }}</strong></td>
                <td>
                  <ul>
                    <li v-for="prod in orden.productos" :key="prod.id">
                      {{ prod.cantidad }} x {{ prod.nombre_producto }}
                    </li>
                  </ul>
                </td>
                <td>-</td>
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
                    Marcar como entregado
                  </button>
                  <span v-else class="entregado-msg">✅ Entregado</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>

      <!-- Menú -->
      <main class="cocina-contenido" v-if="vista === 'menu'">
        <h2>Menú de Productos</h2>

        <!-- Formulario para agregar producto -->
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

        <!-- Lista de productos -->
        <table class="tabla-ordenes">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Precio</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prod in productos" :key="prod.id">
              <td>{{ prod.nombre }}</td>
              <td>${{ prod.precio }}</td>
              <td>
                <span :class="prod.disponible ? 'activo' : 'inactivo'">
                  {{ prod.disponible ? 'Disponible' : 'Agotado' }}
                </span>
              </td>
              <td>
                <button @click="toggleDisponible(prod.id)">
                  {{ prod.disponible ? 'Marcar como Agotado' : 'Marcar como Disponible' }}
                </button>
                <button @click="eliminarProducto(prod.id)">Eliminar</button>
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
import '../EstilosCss/cocinastyle.css'

import {
  fetchOrdenes,
  fetchProductos,
  fetchCategorias,
  toggleDisponibilidadProducto,
  eliminarProductoPorId,
  marcarOrdenComoEntregada,
  crearProducto
} from '../api'

// Estados
const vista = ref('ordenes')
const ordenes = ref([])
const productos = ref([])
const categorias = ref([])
const nuevoProducto = ref({
  nombre: '',
  descripcion: '',
  precio: '',
  categoria_id: ''
})
const nombreUsuario = ref('')
const rolUsuario = ref('')
const mostrarDropdown = ref(false)
const mensaje = ref('')
const mensajeColor = ref('green')

// Funciones
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
  try {
    ordenes.value = await fetchOrdenes()
  } catch (err) {
    console.error('Error cargando órdenes:', err)
  }
}

const obtenerProductos = async () => {
  try {
    productos.value = await fetchProductos()
  } catch (err) {
    console.error('Error al obtener productos:', err)
  }
}

const obtenerCategorias = async () => {
  try {
    categorias.value = await fetchCategorias()
  } catch (err) {
    console.error('Error al obtener categorías:', err)
  }
}

const marcarEntregado = async (id) => {
  try {
    const res = await marcarOrdenComoEntregada(id)
    if (!res.ok) throw new Error()
    await cargarOrdenes()
    alert("✅ Orden marcada como entregada.")
  } catch (err) {
    console.error('Error al marcar como entregado:', err)
    alert("❌ Error al marcar como entregado.")
  }
}

const toggleDisponible = async (id) => {
  try {
    await toggleDisponibilidadProducto(id)
    await obtenerProductos()
  } catch (err) {
    console.error('Error al cambiar disponibilidad:', err)
  }
}

const eliminarProducto = async (id) => {
  if (!confirm("¿Eliminar este producto?")) return
  try {
    await eliminarProductoPorId(id)
    await obtenerProductos()
  } catch (err) {
    console.error('Error al eliminar producto:', err)
  }
}

const crearProductoNuevo = async () => {
  mensaje.value = ''
  try {
    const precio = parseFloat(nuevoProducto.value.precio)
    if (isNaN(precio) || precio <= 0) {
      mensaje.value = 'El precio debe ser mayor a cero.'
      mensajeColor.value = 'red'
      return
    }

    const formData = new FormData()
    Object.entries(nuevoProducto.value).forEach(([key, val]) => formData.append(key, val))

    await crearProducto(formData)
    mensaje.value = '✅ Producto agregado correctamente.'
    mensajeColor.value = 'green'
    nuevoProducto.value = { nombre: '', descripcion: '', precio: '', categoria_id: '' }
    await obtenerProductos()
  } catch (err) {
    console.error('Error al crear producto:', err)
    mensaje.value = '❌ Error al agregar producto.'
    mensajeColor.value = 'red'
  }
}

onMounted(() => {
  const rol = localStorage.getItem('usuario_rol')
  if (rol !== 'chef') {
    window.location.href = '/login'
    return
  }

  nombreUsuario.value = localStorage.getItem('usuario_nombre') || 'Usuario'
  rolUsuario.value = rol
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
  background-color: #0a9f67;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-entregar:hover {
  background-color: #098658;
}

.form-platillo {
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 500px;
}

.form-platillo input,
.form-platillo textarea,
.form-platillo select {
  padding: 8px;
  font-size: 1rem;
}

.form-platillo button {
  background-color: #0a9f67;
  color: white;
  padding: 8px;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}
</style>
