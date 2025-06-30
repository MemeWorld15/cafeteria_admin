<template>
  <div class="caja-app">
    <main class="caja-contenido">
      <!-- Arqueo -->
      <div class="arqueo-section">
        <h2>Arqueo y Corte de Caja</h2>
        <div class="arqueo-details">
          <p><strong>Total efectivo ingresado:</strong> ${{ totalEfectivo.toFixed(2) }}</p>
          <p><strong>Total con tarjetas:</strong> ${{ totalTarjeta.toFixed(2) }}</p>
          <p><strong>Total general:</strong> ${{ totalGeneral.toFixed(2) }}</p>
          <button @click="realizarCorte" class="btn-corte">Realizar corte del día</button>
        </div>
      </div>

      <!-- Cortes -->
      <div class="cortes-section">
        <h2>Historial de Cortes</h2>
        <div v-if="cortesRealizados.length > 0">
          <ul class="cortes-list">
            <li v-for="corte in cortesRealizados" :key="corte.id" class="corte-item">
              <strong>{{ corte.fecha }}</strong> - ${{ corte.total.toFixed(2) }} 
              <span class="estado-corte">{{ corte.estado }}</span>
            </li>
          </ul>
        </div>
        <div v-else class="no-cortes">
          <p>No hay cortes realizados aún.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchArqueoDelDia, realizarCorteCaja, fetchCortes } from '../api'

// Estado del arqueo
const totalEfectivo = ref(0)
const totalTarjeta = ref(0)
const totalGeneral = ref(0)
const cortesRealizados = ref([])

// Carga los datos del arqueo
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

// Realiza el corte
const realizarCorte = async () => {
  try {
    const corte = await realizarCorteCaja(totalEfectivo.value, totalTarjeta.value)
    if (corte.success) {
      alert('Corte realizado exitosamente')
      cargarArqueo()
      cargarCortes()
    } else {
      alert('Error al realizar el corte')
    }
  } catch (error) {
    console.error('Error al realizar el corte:', error)
  }
}

// Carga los cortes previos
const cargarCortes = async () => {
  try {
    const cortes = await fetchCortes()
    cortesRealizados.value = cortes
  } catch (error) {
    console.error('Error al cargar cortes:', error)
  }
}

// Carga inicial
onMounted(() => {
  cargarArqueo()
  cargarCortes()
})
</script>

<style scoped>
/* (Estilos originales sin cambios) */
.caja-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f4f4f4;
}

.caja-contenido {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.arqueo-section, .cortes-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.arqueo-section h2, .cortes-section h2 {
  font-size: 1.5rem;
  color: #333;
}

.arqueo-details p {
  font-size: 1rem;
  margin: 10px 0;
}

.arqueo-details p strong {
  color: #0a9f67;
}

.btn-corte {
  background-color: #0a9f67;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.btn-corte:hover {
  background-color: #0a7c53;
}

.cortes-list {
  list-style-type: none;
  padding: 0;
}

.corte-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
}

.estado-corte {
  font-size: 1rem;
  font-weight: bold;
  color: green;
}

.no-cortes {
  font-size: 1rem;
  color: #666;
  text-align: center;
  padding: 20px;
}
</style>
