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
