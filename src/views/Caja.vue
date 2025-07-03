<template>
  <div class="caja-container">
    <div class="main-grid">
      <!-- Header Principal -->
      <div class="header-card">
        <div class="header-content">
          <div class="header-icon">💰</div>
          <div class="header-text">
            <h1>Sistema de Caja</h1>
            <p>Control integral de ventas y arqueo</p>
          </div>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <div class="stat-value">${{ totalVentas.toFixed(2) }}</div>
            <div class="stat-label">Total Ventas</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">${{ totalGastos.toFixed(2) }}</div>
            <div class="stat-label">Total Gastos</div>
          </div>
        </div>
      </div>

      <!-- Configuración del Corte -->
      <div class="config-card">
        <div class="card-header">
          <h3>⚙️ Configuración</h3>
        </div>
        <div class="config-content">
          <div class="config-row">
            <div class="input-container">
              <label>📅 Fecha</label>
              <input type="date" v-model="fechaSeleccionada" @change="calcularCorte" class="modern-input" />
            </div>
            <div class="input-container">
              <label>🕒 Turno</label>
              <select v-model="turnoSeleccionado" @change="calcularCorte" class="modern-select">
                <option value="matutino">🌅 Matutino</option>
                <option value="vespertino">🌆 Vespertino</option>
                <option value="nocturno">🌙 Nocturno</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Arqueo de Caja -->
      <div class="arqueo-card">
        <div class="card-header">
          <h3>🎯 Arqueo de Caja</h3>
        </div>
        <div class="arqueo-content">
          <div class="arqueo-input-section">
            <div class="money-input-wrapper">
              <label>💵 Monto en Caja</label>
              <div class="money-input">
                <span class="currency">$</span>
                <input type="number" v-model.number="montoEnCaja" placeholder="0.00" class="amount-field" />
              </div>
            </div>
            <button @click="realizarArqueo" class="btn-arqueo">
              <span class="btn-icon">🔍</span>
              Realizar Arqueo
            </button>
          </div>

          <!-- Resultado del Arqueo -->
          <div v-if="resultadoArqueo !== null" class="arqueo-result">
            <div v-if="resultadoArqueo === 0" class="result-perfect">
              <div class="result-icon">🎉</div>
              <div class="result-content">
                <h4>¡Perfecto!</h4>
                <p>La caja está completamente cuadrada</p>
              </div>
            </div>
            <div v-else-if="resultadoArqueo > 0" class="result-excess">
              <div class="result-icon">📈</div>
              <div class="result-content">
                <h4>Exceso de ${{ resultadoArqueo.toFixed(2) }}</h4>
                <p>Hay dinero adicional en la caja</p>
              </div>
            </div>
            <div v-else class="result-deficit">
              <div class="result-icon">📉</div>
              <div class="result-content">
                <h4>Déficit de ${{ Math.abs(resultadoArqueo).toFixed(2) }}</h4>
                <p>Falta dinero en la caja</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Gastos de Caja -->
      <div class="gastos-card">
        <div class="card-header">
          <h3>📋 Gastos de Caja</h3>
          <div class="gastos-summary">
            <span class="total-gastos-badge">${{ totalGastos.toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="gastos-content">
          <!-- Formulario para Agregar Gastos -->
          <div class="add-gasto-section">
            <div class="add-gasto-form">
              <div class="form-row">
                <div class="input-container flex-2">
                  <input v-model="nuevoGasto.descripcion" placeholder="Descripción del gasto..." class="modern-input" />
                </div>
                <div class="input-container flex-1">
                  <div class="money-input">
                    <span class="currency">$</span>
                    <input type="number" v-model.number="nuevoGasto.monto" placeholder="0.00" class="amount-field" />
                  </div>
                </div>
                <button @click="agregarGasto" class="btn-add-gasto">
                  <span class="btn-icon">➕</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Lista de Gastos -->
          <div class="gastos-list" v-if="gastos.length > 0">
            <div class="gastos-header">
              <span>Detalle de Gastos</span>
              <span>{{ gastos.length }} {{ gastos.length === 1 ? 'gasto' : 'gastos' }}</span>
            </div>
            <div class="gastos-items">
              <div v-for="(gasto, index) in gastos" :key="index" class="gasto-item">
                <div class="gasto-icon">💳</div>
                <div class="gasto-details">
                  <div class="gasto-descripcion">{{ gasto.descripcion }}</div>
                  <div class="gasto-timestamp">{{ new Date().toLocaleTimeString() }}</div>
                </div>
                <div class="gasto-amount">${{ gasto.monto.toFixed(2) }}</div>
                <button @click="eliminarGasto(index)" class="btn-delete-gasto">
                  <span>🗑️</span>
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="no-gastos">
            <div class="no-gastos-icon">📝</div>
            <p>No hay gastos registrados para este turno</p>
          </div>
        </div>
      </div>

      <!-- Resumen y Acciones -->
      <div class="summary-card">
        <div class="summary-content">
          <div class="summary-row">
            <div class="summary-item">
              <div class="summary-label">Ventas Totales</div>
              <div class="summary-value positive">${{ totalVentas.toFixed(2) }}</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">Gastos Totales</div>
              <div class="summary-value negative">-${{ totalGastos.toFixed(2) }}</div>
            </div>
            <div class="summary-item highlight">
              <div class="summary-label">Total Esperado</div>
              <div class="summary-value">${{ (totalVentas - totalGastos).toFixed(2) }}</div>
            </div>
          </div>
          
          <div class="action-buttons">
            <button @click="guardarCorte" class="btn-save-corte">
              <span class="btn-icon">💾</span>
              Guardar Corte de Caja
            </button>
            <button @click="generarReporte" class="btn-report">
              <span class="btn-icon">📊</span>
              Generar Reporte
            </button>
          </div>
        </div>
      </div>
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
  if (nuevoGasto.value.descripcion.trim() && nuevoGasto.value.monto > 0) {
    gastos.value.push({ 
      ...nuevoGasto.value,
      timestamp: new Date().toISOString()
    })
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
    resultado: resultadoArqueo.value,
    timestamp: new Date().toISOString()
  }

  console.log('Corte a guardar:', corte)
  alert('Corte guardado exitosamente')
}

// Generar reporte
const generarReporte = () => {
  console.log('Generando reporte...')
  alert('Reporte generado y enviado')
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
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto 1fr auto;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  grid-column: 1 / -1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-content {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}

.header-icon {
  font-size: 4rem;
  margin-right: 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-text h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.2;
}

.header-text p {
  margin: 0.5rem 0 0 0;
  color: #7f8c8d;
  font-size: 1.1rem;
}

.header-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-top: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-divider {
  width: 2px;
  height: 60px;
  background: linear-gradient(to bottom, transparent, #e1e8ed, transparent);
}

.config-card,
.arqueo-card,
.gastos-card,
.summary-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  height: fit-content;
}

.summary-card {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f8f9fa;
}

.card-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.config-row {
  display: flex;
  gap: 1rem;
}

.input-container {
  flex: 1;
}

.input-container label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
  font-size: 0.9rem;
}

.modern-input,
.modern-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
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

.arqueo-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.arqueo-input-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.money-input-wrapper {
  flex: 1;
}

.money-input {
  position: relative;
  display: flex;
  align-items: center;
}

.currency {
  position: absolute;
  left: 1rem;
  font-weight: 600;
  color: #667eea;
  font-size: 1.1rem;
  z-index: 1;
}

.amount-field {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  background: white;
}

.amount-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn-arqueo {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-arqueo:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.arqueo-result {
  padding: 1.5rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1rem;
  animation: slideIn 0.5s ease;
}

.result-perfect {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.result-excess {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.result-deficit {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
}

.result-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.result-content h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.result-content p {
  margin: 0;
  opacity: 0.9;
}

.gastos-summary {
  display: flex;
  align-items: center;
}

.total-gastos-badge {
  background: linear-gradient(135deg, #ff7b7b, #f093fb);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.add-gasto-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  align-items: end;
}

.flex-1 { flex: 1; }
.flex-2 { flex: 2; }

.btn-add-gasto {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-add-gasto:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.gastos-list {
  border: 1px solid #e1e8ed;
  border-radius: 16px;
  overflow: hidden;
}

.gastos-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.gastos-items {
  max-height: 300px;
  overflow-y: auto;
}

.gasto-item {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s ease;
}

.gasto-item:hover {
  background-color: #f8f9fa;
}

.gasto-item:last-child {
  border-bottom: none;
}

.gasto-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.gasto-details {
  flex: 1;
}

.gasto-descripcion {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.2rem;
}

.gasto-timestamp {
  font-size: 0.8rem;
  color: #7f8c8d;
}

.gasto-amount {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e74c3c;
  margin-right: 1rem;
}

.btn-delete-gasto {
  background: #ff6b6b;
  color: white;
  border: none;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-delete-gasto:hover {
  background: #ff5252;
  transform: scale(1.1);
}

.no-gastos {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

.no-gastos-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.summary-row {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 16px;
}

.summary-item {
  text-align: center;
  flex: 1;
}

.summary-item.highlight {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 1rem;
  border-radius: 12px;
  margin: 0 1rem;
}

.summary-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.summary-item.highlight .summary-label {
  color: rgba(255, 255, 255, 0.8);
}

.summary-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
}

.summary-value.positive {
  color: #4CAF50;
}

.summary-value.negative {
  color: #f44336;
}

.summary-item.highlight .summary-value {
  color: white;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.btn-save-corte,
.btn-report {
  flex: 1;
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-save-corte {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.btn-report {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
}

.btn-save-corte:hover,
.btn-report:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.btn-icon {
  font-size: 1.1rem;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .header-stats {
    flex-direction: column;
    gap: 1rem;
  }
  
  .stat-divider {
    width: 100%;
    height: 2px;
  }
  
  .config-row {
    flex-direction: column;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .summary-row {
    flex-direction: column;
    gap: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .caja-container {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .header-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .header-text h1 {
    font-size: 2rem;
  }
  
  .stat-value {
    font-size: 2rem;
  }
}
</style>
