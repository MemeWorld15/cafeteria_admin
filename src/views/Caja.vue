<template>
  <div class="caja-container">
    <div class="card-caja">
      <h2>Resumen de Caja</h2>

      <div class="form-section">
        <label for="fecha">📅 Seleccionar fecha:</label>
        <input type="date" v-model="fechaSeleccionada" @change="calcularCorte" />
      </div>

      <div class="corte-section">
        <h3>💰 Corte del Día</h3>
        <p><strong>Total Ventas:</strong> ${{ totalVentas.toFixed(2) }}</p>
      </div>

      <div class="arqueo-section">
        <h3>📦 Arqueo de Caja</h3>
        <label for="montoCaja">Monto contado en caja:</label>
        <input type="number" v-model.number="montoEnCaja" />
        <button @click="realizarArqueo">Realizar Arqueo</button>

        <div v-if="resultadoArqueo !== null" class="resultado-arqueo">
          <p v-if="resultadoArqueo === 0" class="verde">✅ ¡Caja Cuadrada!</p>
          <p v-else-if="resultadoArqueo > 0" class="amarillo">
            ⚠️ Sobra ${{ resultadoArqueo.toFixed(2) }}
          </p>
          <p v-else class="rojo">
            ❌ Falta ${{ Math.abs(resultadoArqueo).toFixed(2) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
  display: flex;
  justify-content: center;
  padding: 2rem;
  background-color: #f3f3f3;
  min-height: 100vh;
}

.card-caja {
  background: #fff;
  padding: 2rem 2.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}

.card-caja h2 {
  margin-bottom: 1.5rem;
  text-align: center;
}

.form-section,
.corte-section,
.arqueo-section {
  margin-bottom: 1.5rem;
}

input[type="date"],
input[type="number"] {
  width: 100%;
  padding: 0.6rem;
  margin-top: 0.5rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

button {
  margin-top: 1rem;
  padding: 0.6rem 1rem;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.resultado-arqueo {
  margin-top: 1rem;
}

.verde {
  color: green;
  font-weight: bold;
}
.amarillo {
  color: goldenrod;
  font-weight: bold;
}
.rojo {
  color: red;
  font-weight: bold;
}
</style>
