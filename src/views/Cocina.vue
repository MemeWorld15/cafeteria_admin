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

        <!-- NUEVO: Botón para mostrar formulario -->
        <button @click="mostrarFormularioNuevo = !mostrarFormularioNuevo" class="btn-agregar">
          {{ mostrarFormularioNuevo ? 'Cancelar' : '➕ Agregar nuevo producto' }}
        </button>

        <!-- NUEVO: Formulario para agregar producto -->
        <div v-if="mostrarFormularioNuevo" class="formulario-nuevo">
          <input v-model="nuevoProducto.nombre" placeholder="Nombre del producto" />
          <input v-model="nuevoProducto.precio" type="number" step="0.01" placeholder="Precio" />
          <button @click="agregarProducto">Guardar producto</button>
        </div>

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
                  {{ prod.disponible ? 'Disponible' : 'No disponible' }}
                </span>
              </td>
              <td>
                <button @click="toggleDisponible(prod.id)">
                  {{ prod.disponible ? 'Desactivar' : 'Activar' }}
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
  toggleDisponibilidadProducto,
  eliminarProductoPorId,
  marcarOrdenComoEntregada,
  crearProducto
} from '../api'

const vista = ref('ordenes')
const ordenes = ref([])
const productos = ref([])
const nombreUsuario = ref('')
const rolUsuario = ref('')
const mostrarDropdown = ref(false)

// NUEVO: control para mostrar formulario de producto
const mostrarFormularioNuevo = ref(false)
const nuevoProducto = ref({ nombre: '', precio: 0 })

// Modo oscuro
const toggleDarkMode = () => {
  document.body.classList.toggle('dark-mode')
}

//Opciones 
const toggleDropdown = () => {
  mostrarDropdown.value = !mostrarDropdown.value
}

const cerrarSesion = () => {
  localStorage.clear()
  window.location.href = '/'
}

// Obtener productos
const obtenerProductos = async () => {
  try {
    productos.value = await fetchProductos()
  } catch (err) {
    console.error('Error al obtener productos:', err)
  }
}

// Obtener órdenes
const cargarOrdenes = async () => {
  try {
    ordenes.value = await fetchOrdenes()
  } catch (err) {
    console.error('Error cargando órdenes:', err)
  }
}

// Marcar como entregado
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

// Cambiar disponibilidad
const toggleDisponible = async (id) => {
  try {
    await toggleDisponibilidadProducto(id)
    await obtenerProductos()
  } catch (err) {
    console.error('Error al cambiar disponibilidad:', err)
  }
}

// Eliminar producto
const eliminarProducto = async (id) => {
  if (!confirm("¿Eliminar este producto?")) return
  try {
    await eliminarProductoPorId(id)
    await obtenerProductos()
  } catch (err) {
    console.error('Error al eliminar producto:', err)
  }
}

// NUEVO: Agregar producto
const agregarProducto = async () => {
  if (!nuevoProducto.value.nombre || nuevoProducto.value.precio <= 0) {
    alert("❌ Nombre y precio válidos requeridos")
    return
  }

  const formData = new FormData()
  formData.append('nombre', nuevoProducto.value.nombre)
  formData.append('precio', nuevoProducto.value.precio)
  formData.append('disponible', true)

  try {
    await crearProducto(formData)
    await obtenerProductos()
    mostrarFormularioNuevo.value = false
    nuevoProducto.value = { nombre: '', precio: 0 }
    alert("✅ Producto agregado correctamente")
  } catch (err) {
    console.error('Error al agregar producto:', err)
    alert("❌ Error al agregar producto")
  }
}

onMounted(() => {
  const rol = localStorage.getItem('usuario_rol')
  if (rol !== 'chef') {
    router.push('/login')
    return
  }

  nombreUsuario.value = localStorage.getItem('usuario_nombre') || 'Usuario'
  rolUsuario.value = rol
  cargarOrdenes()
  obtenerProductos()
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

/* NUEVO: estilos para formulario */
.formulario-nuevo {
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.formulario-nuevo input {
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.formulario-nuevo button {
  background-color: #0a9f67;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-agregar {
  margin-bottom: 1rem;
  padding: 8px 14px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
