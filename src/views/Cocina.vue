<template>
  <div class="cocina-app">
    <!-- Topbar -->
    <header class="cocina-topbar">
      <div class="cocina-logo">
        <img :src="logo" alt="Logo" />
        <span class="cocina-brand">Cafetería</span>
      </div>
      <div class="cocina-user">
        <i class="fas fa-sun" @click="toggleDarkMode"></i>
        <i class="fas fa-bell"></i>
        <i class="fas fa-user"></i>
        <div class="cocina-user-info">
        <span class="cocina-usuario">{{ nombreUsuario }}</span><br />
        <span class="cocina-rol">{{ rolUsuario }}</span>
      </div>


        <!--<span class="cocina-username">Gavano</span>-->
        <i class="fas fa-chevron-down"></i>
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

      <!-- Contenido -->
       
      <main class="cocina-contenido" v-if="vista === 'ordenes'">
        <h2>Órdenes - Café</h2>
        <div class="scroll-tabla"> <!-- 👈 Añadido -->
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
                <button v-if="!orden.entregado" @click="marcarEntregado(orden.id)">Marcar como entregado</button>
              </td>
            </tr>
          </tbody>
        </table>
        </div> <!-- 👈 Añadido -->
      </main>
      <!-- Vista Menú -->
<main class="cocina-contenido" v-if="vista === 'menu'">
  <h2>Menú de Productos</h2>
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


const vista = ref('ordenes')
const ordenes = ref([])
const nombreUsuario = ref('')
const rolUsuario = ref('')


const toggleDarkMode = () => {
  document.body.classList.toggle('dark-mode')
}


const cargarOrdenes = async () => {
  try {
    const res = await fetch('http://localhost:8000/ordenes')
    ordenes.value = await res.json()
  } catch (err) {
    console.error('Error cargando órdenes:', err)
  }
}

const marcarEntregado = async (id) => {
  try {
    await fetch(`http://localhost:8000/ordenes/${id}/entregado`, {
      method: 'PUT'
    })
    cargarOrdenes()
  } catch (err) {
    console.error('Error al marcar como entregado:', err)
  }
}
const productos = ref([])

const obtenerProductos = async () => {
  const res = await fetch('http://localhost:8000/productos')
  productos.value = await res.json()
}

const toggleDisponible = async (id) => {
  await fetch(`http://localhost:8000/productos/${id}/toggle-disponible`, { method: 'PUT' })
  obtenerProductos()
}

const eliminarProducto = async (id) => {
  if (!confirm("¿Eliminar este producto?")) return
  await fetch(`http://localhost:8000/productos/${id}`, { method: 'DELETE' })
  obtenerProductos()
}


onMounted(() => {
  nombreUsuario.value = localStorage.getItem('usuario_nombre') || 'Usuario'
  rolUsuario.value = localStorage.getItem('usuario_rol') || 'Rol'

  cargarOrdenes()
  obtenerProductos()

  
})
</script>
