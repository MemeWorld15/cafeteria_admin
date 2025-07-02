<template>
  <div class="caja-container">
    <div class="card-caja">
      <h2>Resumen de Caja</h2>

      <!-- Selector de Fecha -->
      <div class="form-section">
        <label for="fecha">📅 Seleccionar fecha:</label>
        <input type="date" v-model="fechaSeleccionada" @change="calcularCorte" />
      </div>

      <!-- Selector de Turno -->
      <div class="form-section">
        <label for="turno">🕒 Seleccionar Turno:</label>
        <select v-model="turnoSeleccionado" @change="calcularCorte">
          <option value="matutino">Matutino</option>
          <option value="vespertino">Vespertino</option>
          <option value="nocturno">Nocturno</option>
        </select>
      </div>

      <!-- Corte de Caja -->
      <div class="corte-section">
        <h3>💰 Corte del Día</h3>
        <p><strong>Total Ventas:</strong> ${{ totalVentas.toFixed(2) }}</p>
      </div>

      <!-- Arqueo de Caja -->
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

      <!-- Gastos en Caja -->
      <div class="gastos-section">
        <h3>📝 Gastos en Caja</h3>
        <input v-model="nuevoGasto.descripcion" placeholder="Descripción del gasto" />
        <input type="number" v-model.number="nuevoGasto.monto" placeholder="Monto del gasto" />
        <button @click="agregarGasto">Agregar Gasto</button>

        <ul>
          <li v-for="(g, i) in gastos" :key="i">
            {{ g.descripcion }} - ${{ g.monto.toFixed(2) }}
            <button @click="eliminarGasto(i)">❌</button>
          </li>
        </ul>
      </div>

      <!-- Botón para Guardar el Corte -->
      <button @click="guardarCorte">💾 Guardar Corte</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchOrdenes } from '../api'

const fechaSeleccionada = ref(new Date().toISOString().slice(0, 10))
const turnoSeleccionado = ref('matutino')
const totalVentas = ref(0)
const montoEnCaja = ref(0)
const resultadoArqueo = ref(null)

const gastos = ref([])
const nuevoGasto = ref({ descripcion: '', monto: 0 })

// Calcular el total de ventas
const calcularCorte = async () => {
  const todasOrdenes = await fetchOrdenes()

  const ordenesDelDia = todasOrdenes.filter(o =>
    o.fecha.startsWith(fechaSeleccionada.value) &&
    o.turno === turnoSeleccionado.value
  )

  totalVentas.value = ordenesDelDia.reduce((total, orden) => {
    const totalOrden = orden.productos.reduce((suma, p) => suma + p.cantidad * p.precio_unitario, 0)
    return total + totalOrden
  }, 0)

  resultadoArqueo.value = null
}

// Agregar un gasto
const agregarGasto = () => {
  if (nuevoGasto.value.descripcion && nuevoGasto.value.monto > 0) {
    gastos.value.push({ ...nuevoGasto.value })
    nuevoGasto.value = { descripcion: '', monto: 0 }
  }
}

// Eliminar un gasto
const eliminarGasto = (index) => {
  gastos.value.splice(index, 1)
}

// Realizar el arqueo
const totalGastos = computed(() => gastos.value.reduce((sum, g) => sum + g.monto, 0))

const realizarArqueo = () => {
  const totalEsperado = totalVentas.value - totalGastos.value
  resultadoArqueo.value = montoEnCaja.value - totalEsperado
}

// Guardar el corte (para backend o archivo)
const guardarCorte = () => {
  const corte = {
    fecha: fechaSeleccionada.value,
    turno: turnoSeleccionado.value,
    totalVentas: totalVentas.value,
    gastos: gastos.value,
    totalGastos: totalGastos.value,
    montoCaja: montoEnCaja.value,
    resultado: resultadoArqueo.value
  }

  console.log('Corte a guardar:', corte)
  // Aquí puedes hacer el POST a tu API o guardarlo en base de datos
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
.arqueo-section,
.gastos-section {
  margin-bottom: 1.5rem;
}

input[type="date"],
input[type="number"],
select {
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

ul {
  list-style-type: none;
  padding: 0;
}

ul li {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
</style>
