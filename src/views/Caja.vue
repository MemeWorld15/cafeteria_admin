<template>
  <div class="caja-container">
    <div class="card-caja">
      <div class="header">
        <h2>💰 Resumen de Caja</h2>
        <div class="header-subtitle">Sistema de Control de Ventas</div>
      </div>

      <!-- Selector de Fecha -->
      <div class="form-section">
        <div class="input-group">
          <label for="fecha">
            <span class="icon">📅</span>
            Seleccionar fecha
          </label>
          <input type="date" v-model="fechaSeleccionada" @change="calcularCorte" class="modern-input" />
        </div>
      </div>

      <!-- Selector de Turno -->
      <div class="form-section">
        <div class="input-group">
          <label for="turno">
            <span class="icon">🕒</span>
            Seleccionar Turno
          </label>
          <select v-model="turnoSeleccionado" @change="calcularCorte" class="modern-select">
            <option value="matutino">Matutino (6:00 - 14:00)</option>
            <option value="vespertino">Vespertino (14:00 - 22:00)</option>
            <option value="nocturno">Nocturno (22:00 - 6:00)</option>
          </select>
        </div>
      </div>

      <!-- Corte de Caja -->
      <div class="corte-section">
        <div class="section-header">
          <h3>💎 Corte del Día</h3>
        </div>
        <div class="total-ventas">
          <span class="currency">$</span>
          <span class="amount">{{ totalVentas.toFixed(2) }}</span>
        </div>
        <div class="total-label">Total de Ventas</div>
      </div>

      <!-- Arqueo de Caja -->
      <div class="arqueo-section">
        <div class="section-header">
          <h3>📦 Arqueo de Caja</h3>
        </div>
        <div class="input-group">
          <label for="montoCaja">Monto contado en caja</label>
          <div class="amount-input-wrapper">
            <span class="currency-symbol">$</span>
            <input type="number" v-model.number="montoEnCaja" class="amount-input" placeholder="0.00" />
          </div>
        </div>
        <button @click="realizarArqueo" class="btn-primary">
          <span class="btn-icon">🔍</span>
          Realizar Arqueo
        </button>

        <div v-if="resultadoArqueo !== null" class="resultado-arqueo">
          <div v-if="resultadoArqueo === 0" class="status-card success">
            <div class="status-icon">✅</div>
            <div class="status-text">¡Caja Cuadrada!</div>
            <div class="status-subtitle">Todo está en orden</div>
          </div>
          <div v-else-if="resultadoArqueo > 0" class="status-card warning">
            <div class="status-icon">⚠️</div>
            <div class="status-text">Sobra ${{ resultadoArqueo.toFixed(2) }}</div>
            <div class="status-subtitle">Dinero adicional en caja</div>
          </div>
          <div v-else class="status-card error">
            <div class="status-icon">❌</div>
            <div class="status-text">Falta ${{ Math.abs(resultadoArqueo).toFixed(2) }}</div>
            <div class="status-subtitle">Diferencia negativa</div>
          </div>
        </div>
      </div>

      <!-- Gastos en Caja -->
      <div class="gastos-section">
        <div class="section-header">
          <h3>📝 Gastos en Caja</h3>
        </div>
        
        <div class="gastos-form">
          <div class="input-group">
            <input v-model="nuevoGasto.descripcion" placeholder="Descripción del gasto" class="modern-input" />
          </div>
          <div class="input-group">
            <div class="amount-input-wrapper">
              <span class="currency-symbol">$</span>
              <input type="number" v-model.number="nuevoGasto.monto" placeholder="0.00" class="amount-input" />
            </div>
          </div>
          <button @click="agregarGasto" class="btn-secondary">
            <span class="btn-icon">➕</span>
            Agregar Gasto
          </button>
        </div>

        <div class="gastos-list" v-if="gastos.length > 0">
          <div v-for="(g, i) in gastos" :key="i" class="gasto-item">
            <div class="gasto-info">
              <div class="gasto-descripcion">{{ g.descripcion }}</div>
              <div class="gasto-monto">${{ g.monto.toFixed(2) }}</div>
            </div>
            <button @click="eliminarGasto(i)" class="btn-delete">
              <span class="btn-icon">🗑️</span>
            </button>
          </div>
          <div class="total-gastos">
            <strong>Total Gastos: ${{ totalGastos.toFixed(2) }}</strong>
          </div>
        </div>
      </div>

      <!-- Botón para Guardar el Corte -->
      <button @click="guardarCorte" class="btn-save">
        <span class="btn-icon">💾</span>
        Guardar Corte
      </button>
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
* {
  box-sizing: border-box;
}

.caja-container {
  display: flex;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.card-caja {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 600;
}

.header-subtitle {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.form-section,
.corte-section,
.arqueo-section,
.gastos-section {
  margin-bottom: 2rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h3 {
  margin: 0;
  color: #34495e;
  font-size: 1.3rem;
  font-weight: 600;
}

.input-group {
  margin-bottom: 1rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
  font-size: 0.9rem;
}

.icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.modern-input,
.modern-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e1e8ed;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
}

.modern-input:focus,
.modern-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.amount-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.currency-symbol {
  position: absolute;
  left: 1rem;
  color: #7f8c8d;
  font-weight: 600;
  z-index: 1;
}

.amount-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2rem;
  border: 2px solid #e1e8ed;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
}

.amount-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.total-ventas {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  border-radius: 15px;
  margin-bottom: 1rem;
  color: white;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.total-ventas .currency {
  font-size: 1.5rem;
  font-weight: 300;
}

.total-ventas .amount {
  font-size: 2.5rem;
  font-weight: 700;
  margin-left: 0.2rem;
}

.total-label {
  text-align: center;
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.btn-primary,
.btn-secondary,
.btn-save {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  margin-top: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #ff7b7b, #f093fb);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 123, 123, 0.3);
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 123, 123, 0.4);
}

.btn-save {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  width: 100%;
  font-size: 1.1rem;
  padding: 1rem;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.btn-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.btn-delete {
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 50%;
  width: 35px;
  height: 35px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-delete:hover {
  background: #ff5252;
  transform: scale(1.1);
}

.status-card {
  padding: 1.5rem;
  border-radius: 15px;
  margin-top: 1rem;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.status-card.success {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.status-card.warning {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.status-card.error {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
}

.status-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.status-text {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
}

.status-subtitle {
  font-size: 0.9rem;
  opacity: 0.9;
}

.gastos-form {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 15px;
  margin-bottom: 1.5rem;
  border: 1px solid #e9ecef;
}

.gastos-list {
  background: white;
  border-radius: 15px;
  padding: 1rem;
  border: 1px solid #e9ecef;
}

.gasto-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s ease;
}

.gasto-item:hover {
  background-color: #f8f9fa;
}

.gasto-item:last-child {
  border-bottom: none;
}

.gasto-info {
  flex: 1;
}

.gasto-descripcion {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.2rem;
}

.gasto-monto {
  color: #e74c3c;
  font-weight: 600;
  font-size: 1.1rem;
}

.total-gastos {
  text-align: center;
  padding: 1rem;
  background: linear-gradient(135deg, #ff7b7b, #f093fb);
  color: white;
  border-radius: 10px;
  margin-top: 1rem;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .caja-container {
    padding: 1rem;
  }
  
  .card-caja {
    padding: 1.5rem;
  }
  
  .total-ventas .amount {
    font-size: 2rem;
  }
}
</style>
