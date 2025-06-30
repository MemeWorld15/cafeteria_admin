<template>
  <div class="caja-container">
    <h2>Resumen de Caja</h2>

    <label for="fecha">Seleccionar fecha:</label>
    <input type="date" v-model="fechaSeleccionada" @change="calcularCorte" />

    <h3>Corte del Día</h3>
    <p>Total Ventas: ${{ totalVentas.toFixed(2) }}</p>

    <h3>Arqueo de Caja</h3>
    <label for="montoCaja">Monto contado en caja:</label>
    <input type="number" v-model.number="montoEnCaja" />
    <button @click="realizarArqueo">Realizar Arqueo</button>

    <div v-if="resultadoArqueo !== null">
      <p v-if="resultadoArqueo === 0" style="color: green;">¡Caja Cuadrada!</p>
      <p v-else-if="resultadoArqueo > 0" style="color: orange;">
        Sobra ${{ resultadoArqueo.toFixed(2) }}
      </p>
      <p v-else style="color: red;">
        Falta ${{ Math.abs(resultadoArqueo).toFixed(2) }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { fetchOrdenes } from '../api'

const fechaSeleccionada = ref(new Date().toISOString().slice(0, 10))
const totalVentas = ref(0)
const montoEnCaja = ref(0)
const resultadoArqueo = ref(null)

const calcularCorte = async () => {
  const todasOrdenes = await fetchOrdenes()

  const ordenesDelDia = todasOrdenes.filter(o => o.fecha.startsWith(fechaSeleccionada.value))
  totalVentas.value = ordenesDelDia.reduce((total, orden) => {
    const totalOrden = orden.productos.reduce((suma, p) => suma + p.cantidad * p.precio_unitario, 0)
    return total + totalOrden
  }, 0)

  resultadoArqueo.value = null
}

const realizarArqueo = () => {
  resultadoArqueo.value = montoEnCaja.value - totalVentas.value
}

onMounted(() => {
  calcularCorte()
})
</script>

<style scoped>
.caja-container {
  max-width: 600px;
  margin: auto;
  padding: 2rem;
}
</style>
