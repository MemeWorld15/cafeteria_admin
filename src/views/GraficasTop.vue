<template>
  <div class="graficas-top">
    <div class="graf-grid">
      <div class="graf-item">
        <h3>📊 Productos más pedidos</h3>
        <canvas ref="chartProductos"></canvas>
      </div>

      <div class="graf-item">
        <h3>👤 Clientes con más órdenes</h3>
        <canvas ref="chartClientes"></canvas>
      </div>

      <div class="graf-item">
        <h3>📉 Producto menos pedido</h3>
        <canvas ref="chartMenosPedido"></canvas>
      </div>
    </div>
  </div>
</template>
<style scoped>
<script setup>
import { ref, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import {
  fetchTopProductos,
  fetchTopClientes,
  fetchProductoMenosPedido
} from '../api'

Chart.register(...registerables)

const chartProductos = ref(null)
const chartClientes = ref(null)
const chartMenosPedido = ref(null)

const cargarGraficas = async () => {
  try {
    const topProductos = await fetchTopProductos()
    const topClientes = await fetchTopClientes()
    const menosPedido = await fetchProductoMenosPedido()

    new Chart(chartProductos.value, {
      type: 'bar',
      data: {
        labels: topProductos.map(p => p.nombre_producto),
        datasets: [{
          label: 'Cantidad total pedida',
          data: topProductos.map(p => p.total_pedidos),
          backgroundColor: '#4CAF50'
        }]
      }
    })

    new Chart(chartClientes.value, {
      type: 'doughnut',
      data: {
        labels: topClientes.map(c => c.cliente),
        datasets: [{
          label: 'Órdenes',
          data: topClientes.map(c => c.total_ordenes),
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#7E57C2']
        }]
      }
    })

    new Chart(chartMenosPedido.value, {
      type: 'bar',
      data: {
        labels: [menosPedido.nombre_producto],
        datasets: [{
          label: 'Veces vendido',
          data: [menosPedido.total_vendidos],
          backgroundColor: '#E91E63'
        }]
      }
    })
  } catch (err) {
    console.error('Error al cargar gráficas:', err)
  }
}

onMounted(cargarGraficas)
</script>
.graficas-top {
  padding: 2rem;
  max-width: 1200px;
  margin: auto;
}

.graf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}

.graf-item {
  background: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.graf-item h3 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
  text-align: center;
}

canvas {
  width: 100% !important;
  height: 300px !important;
}
</style>
