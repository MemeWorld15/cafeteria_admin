<template>
  <div class="caja-app">
    <!-- Topbar -->
    <header class="caja-topbar">
      <div class="caja-logo">
        <img :src="logo" alt="Logo" />
        <span class="caja-brand">Caja</span>
      </div>
      <div class="caja-user" @click="toggleDropdown">
        <i class="fas fa-sun" @click="toggleDarkMode"></i>
        <i class="fas fa-bell"></i>
        <i class="fas fa-user"></i>
        <div class="caja-user-info">
          <span class="caja-usuario">{{ nombreUsuario }}</span><br />
          <span class="caja-rol">{{ rolUsuario }}</span>
        </div>
        <i class="fas fa-chevron-down"></i>
        <div v-if="mostrarDropdown" class="dropdown-menu" @click.stop>
          <p>{{ nombreUsuario }}</p>
          <hr />
          <button @click="cerrarSesion">Cerrar sesión</button>
        </div>
      </div>
    </header>

    <!-- Sidebar -->
    <aside class="caja-sidebar">
      <ul>
        <li :class="{ active: vista === 'arqueo' }" @click="vista = 'arqueo'">
          <i class="fas fa-cash-register"></i><span>Arqueo</span>
        </li>
        <li :class="{ active: vista === 'cortes' }" @click="vista = 'cortes'">
          <i class="fas fa-history"></i><span>Cortes</span>
        </li>
      </ul>
    </aside>

    <!-- Arqueo de Caja -->
    <main class="caja-contenido" v-if="vista === 'arqueo'">
      <h2>Arqueo y Corte de Caja</h2>
      <div class="arqueo-section">
        <p><strong>Total efectivo ingresado:</strong> ${{ totalEfectivo }}</p>
        <p><strong>Total con tarjetas:</strong> ${{ totalTarjeta }}</p>
        <p><strong>Total general:</strong> ${{ totalGeneral }}</p>
        <button @click="realizarCorte" class="btn-corte">Realizar corte del día</button>
      </div>
    </main>

    <!-- Historial de cortes -->
    <main class="caja-contenido" v-if="vista === 'cortes'">
      <h2>Historial de Cortes</h2>
      <div v-if="cortesRealizados.length > 0">
        <ul>
          <li v-for="corte in cortesRealizados" :key="corte.id">
            <strong>{{ corte.fecha }}</strong> - ${{ corte.total }} <span class="estado-corte">{{ corte.estado }}</span>
          </li>
        </ul>
      </div>
      <div v-else>
        <p>No hay cortes realizados aún.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import logo from '../assets/images/LogoCafe.png'
import { fetchArqueoDelDia, realizarCorteCaja, fetchCortes } from '../api'

const vista = ref('arqueo')
const totalEfectivo = ref(0)
const totalTarjeta = ref(0)
const totalGeneral = ref(0)
const cortesRealizados = ref([])

const nombreUsuario = ref('')
const rolUsuario = ref('')
const mostrarDropdown = ref(false)

// Método para activar/desactivar modo oscuro
const toggleDarkMode = () => document.body.classList.toggle('dark-mode')
const toggleDropdown = () => (mostrarDropdown.value = !mostrarDropdown.value)
const cerrarSesion = () => {
  localStorage.clear()
  window.location.href = '/login'
}

// Función para cargar arqueo del día
const cargarArqueo = async () => {
  try {
    const arqueo = await fetchArqueoDelDia()
    totalEfectivo.value = arqueo.efectivo
    totalTarjeta.value = arqueo.tarjeta
    totalGeneral.value = arqueo.total
  } catch (error) {
    console.error('Error al cargar el arqueo:', error)
  }
}

// Función para realizar el corte de caja
const realizarCorte = async () => {
  try {
    const corte = await realizarCorteCaja(totalEfectivo.value, totalTarjeta.value)
    if (corte.success) {
      alert('Corte realizado exitosamente')
      cargarArqueo() // Actualizar los totales
      cargarCortes() // Actualizar el historial de cortes
    } else {
      alert('Error al realizar el corte')
    }
  } catch (error) {
    console.error('Error al realizar el corte:', error)
  }
}

// Función para cargar el historial de cortes realizados
const cargarCortes = async () => {
  try {
    const cortes = await fetchCortes()
    cortesRealizados.value = cortes
  } catch (error) {
    console.error('Error al cargar cortes:', error)
  }
}

// Cargar información al montar el componente
onMounted(() => {
  if (localStorage.getItem('usuario_rol') !== 'Caja') {
    window.location.href = '/login'
    return
  }
  nombreUsuario.value = localStorage.getItem('usuario_nombre') || 'Usuario'
  rolUsuario.value = 'Caja'
  cargarArqueo()
  cargarCortes()
})
</script>

<style scoped>
.caja-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.caja-topbar {
  background: #0a9f67;
  padding: 10px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.caja-logo {
  display: flex;
  align-items: center;
}

.caja-logo img {
  width: 40px;
  margin-right: 10px;
}

.caja-brand {
  font-size: 1.5rem;
  font-weight: bold;
}

.caja-sidebar {
  background: #f4f4f4;
  width: 250px;
  padding-top: 20px;
}

.caja-sidebar ul {
  list-style-type: none;
  padding: 0;
}

.caja-sidebar ul li {
  padding: 15px;
  cursor: pointer;
  font-size: 1rem;
}

.caja-sidebar ul li:hover {
  background: #e0e0e0;
}

.caja-contenido {
  flex: 1;
  padding: 20px;
}

.arqueo-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.arqueo-section p {
  margin-bottom: 10px;
}

.btn-corte {
  background-color: #0a9f67;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.estado-corte {
  font-size: 0.9rem;
  color: green;
  font-weight: bold;
}

.caja-user {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.caja-user-info {
  margin-left: 10px;
}

.caja-user-info span {
  font-size: 0.9rem;
}
</style>
