<template>
  <div class="cocina-app">
    <!-- Topbar -->
    <header class="cocina-topbar">
      <div class="cocina-logo">
        <img :src="logo" alt="Logo" />
        <span class="cocina-brand">Cafetería</span>
      </div>
      <div class="cocina-user" @click="toggleDropdown">
        <i class="fas fa-sun" @click.stop="toggleDarkMode"></i>
        <i class="fas fa-bell"></i>
        <i class="fas fa-user"></i>
        <div class="cocina-user-info">
          <span class="cocina-usuario">{{ nombreUsuario }}</span><br />
          <span class="cocina-rol">{{ rolUsuario }}</span>
        </div>
        <i class="fas fa-chevron-down"></i>
        <div v-if="mostrarDropdown" class="dropdown-menu" @click.stop>
          <p>{{ nombreUsuario }}</p>
          <hr />
          <button @click="cerrarSesion">Cerrar sesión</button>
        </div>
      </div>
    </header>

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
      </aside>

      <!-- Vista Órdenes -->
      <main class="cocina-contenido" v-if="vista === 'ordenes'">
        <h2>📋 Órdenes - Café</h2>
        <div v-for="(turnos, fecha) in ordenesAgrupadas" :key="fecha" class="bloque-fecha">
          <h3 class="fecha-title">📅 {{ formatFecha(fecha) }}</h3>
          <div v-for="(ordenesTurno, turno) in turnos" :key="turno" class="bloque-turno">
            <h4 class="turno-title">🕐 Turno: {{ turno }}</h4>

            <!-- En espera -->
            <div class="scroll-tabla">
              <h5>🕒 En espera</h5>
              <table class="tabla-ordenes">
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Productos</th>
                    <th>Mesa</th>
                    <th>Hora</th>
                    <th>Status</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="orden in ordenesTurno.filter(o => !o.entregado)" :key="orden.id">
                    <td><strong>{{ orden.cliente }}</strong></td>
                    <td>
                      <ul>
                        <li v-for="prod in orden.productos" :key="prod.id">
                          {{ prod.cantidad }} x {{ prod.nombre_producto }}
                        </li>
                      </ul>
                    </td>
                    <td>-</td>
                    <td>{{ orden.hora }}</td>
                    <td><span class="estado no-entregado">En espera</span></td>
                    <td>
                      <button @click="marcarEntregado(orden.id)" class="btn-entregar">
                        Marcar como entregado
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>

              <!-- Entregadas -->
              <h5>✅ Entregadas</h5>
              <table class="tabla-ordenes">
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Productos</th>
                    <th>Mesa</th>
                    <th>Hora</th>
                    <th>Status</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="orden in ordenesTurno.filter(o => o.entregado)" :key="orden.id">
                    <td><strong>{{ orden.cliente }}</strong></td>
                    <td>
                      <ul>
                        <li v-for="prod in orden.productos" :key="prod.id">
                          {{ prod.cantidad }} x {{ prod.nombre_producto }}
                        </li>
                      </ul>
                    </td>
                    <td>-</td>
                    <td>{{ orden.hora }}</td>
                    <td><span class="estado entregado">Entregado</span></td>
                    <td><span class="entregado-msg">✅ Entregado</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <!-- Vista Menú -->
      <main class="cocina-contenido" v-if="vista === 'menu'">
        <h2>Menú de Productos</h2>

        <h3>Agregar Platillo</h3>
        <form @submit.prevent="crearProductoNuevo" class="form-platillo">
          <input v-model="nuevoProducto.nombre" placeholder="Nombre" required />
          <textarea v-model="nuevoProducto.descripcion" placeholder="Descripción" required />
          <input v-model="nuevoProducto.precio" type="number" min="0.01" step="0.01" placeholder="Precio" required />
          <select v-model="nuevoProducto.categoria_id" required>
            <option disabled value="">Seleccionar categoría</option>
            <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
          </select>
          <button type="submit">Agregar</button>
        </form>
        <p v-if="mensaje" :style="{ color: mensajeColor }">{{ mensaje }}</p>

        <table class="tabla-ordenes">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Precio</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prod in productos" :key="prod.id">
              <td>{{ prod.nombre }}</td>
              <td>{{ categoriaNombre(prod.categoria_id) }}</td>
              <td>${{ prod.precio }}</td>
              <td>
                <span :class="prod.disponible ? 'activo' : 'inactivo'">
                  {{ prod.disponible ? 'Disponible' : 'Agotado' }}
                </span>
              </td>
              <td>
                <button @click="abrirEditar(prod)">Editar</button>
                <button @click="toggleDisponible(prod.id)">
                  {{ prod.disponible ? 'Marcar Agotado' : 'Marcar Disponible' }}
                </button>
                <button @click="eliminarProducto(prod.id)">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Modal de edición -->
        <div v-if="editandoProducto" class="modal-overlay" @click.self="cerrarModal">
          <div class="modal">
            <h3>Editar Platillo</h3>
            <form @submit.prevent="guardarEdicion">
              <input v-model="editandoProducto.nombre" required />
              <textarea v-model="editandoProducto.descripcion" required />
              <input v-model="editandoProducto.precio" type="number" min="0.01" step="0.01" required />
              <select v-model="editandoProducto.categoria_id" required>
                <option disabled value="">Seleccionar categoría</option>
                <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
              </select>
              <div class="modal-buttons">
                <button type="submit">Guardar</button>
                <button type="button" @click="cerrarModal">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>


<style scoped>
/* Estructura principal */
.cocina-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #fff;
}
.cocina-topbar {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 10;
}
.cocina-logo {
  display: flex;
  align-items: center;
}
.cocina-logo img {
  height: 30px;
  margin-right: 10px;
}
.cocina-brand {
  font-weight: bold;
  font-size: 1.2rem;
}
.cocina-user {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 10px;
  position: relative;
}
.cocina-user-info {
  display: inline-block;
  text-align: right;
  font-size: 13px;
}
.dropdown-menu {
  position: absolute;
  right: 0;
  top: 40px;
  background: white;
  border: 1px solid #ccc;
  padding: 10px;
  z-index: 5;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
.cocina-main {
  display: flex;
  flex: 1;
}
.cocina-sidebar {
  width: 200px;
  background: #f0f0f0;
  padding: 1rem;
}
.cocina-sidebar ul {
  list-style: none;
  padding: 0;
}
.cocina-sidebar li {
  padding: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.cocina-sidebar li.active {
  background: #ddd;
  font-weight: bold;
}
.cocina-sidebar li i {
  margin-right: 8px;
}
.cocina-contenido {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

/* Tablas de órdenes */
.tabla-ordenes {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.5rem;
}
.tabla-ordenes th,
.tabla-ordenes td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

/* Estados */
.estado {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}
.no-entregado {
  background: #ffe0b2;
  color: #c87f00;
}
.entregado {
  background: #c8e6c9;
  color: #2e7d32;
}
.entregado-msg {
  color: #2e7d32;
  font-weight: bold;
}

/* Botones */
.btn-entregar {
  background-color: #0a9f67;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-entregar:hover {
  background: #098658;
}

/* Bloques de fecha y turno */
.bloque-fecha {
  margin-bottom: 2rem;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 8px;
}
.fecha-title {
  color: #333;
  margin-bottom: 0.5rem;
}
.turno-title {
  margin-top: 1rem;
  font-weight: bold;
  color: #444;
}
h5 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  font-weight: bold;
  color: #333;
}

/* Scroll horizontal en tablas */
.scroll-tabla {
  overflow-x: auto;
}

/* Formulario de productos */
.form-platillo {
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 500px;
}
.form-platillo input,
textarea,
select {
  padding: 8px;
  font-size: 1rem;
}
.form-platillo button {
  background: #0a9f67;
  color: white;
  padding: 8px;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

/* Modal edición de producto */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal {
  background: white;
  padding: 20px;
  border-radius: 6px;
  width: 90%;
  max-width: 400px;
}
.modal-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}
.modal-buttons button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.modal-buttons button:first-child {
  background: #0a9f67;
  color: white;
}
.modal-buttons button:last-child {
  background: #ccc;
}

/* Estado de disponibilidad en menú */
.activo {
  color: green;
  font-weight: bold;
}
.inactivo {
  color: red;
  font-weight: bold;
}

</style>
