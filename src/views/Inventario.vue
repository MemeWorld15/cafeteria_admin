<template>
  <div class="admin-inventario">
    <h3>Inventario</h3>

    <!-- Alerta de stock bajo -->
    <div v-if="alertasStock.length" class="alerta-inventario">
      <strong>⚠️ Atención:</strong> Hay {{ alertasStock.length }} insumo(s) con stock bajo.
      <ul>
        <li v-for="item in alertasStock" :key="item.id">
          {{ item.nombre }} ({{ item.cantidad.toFixed(2) }} {{ item.unidad }})
        </li>
      </ul>
    </div>

    <!-- Formulario para agregar -->
    <form @submit.prevent="agregarNuevoInsumo" class="form-inventario">
      <input v-model="nuevoInsumo.nombre" type="text" placeholder="Nombre del insumo" required />
      <input v-model.number="nuevoInsumo.cantidad" type="number" placeholder="Cantidad" required />
      <select v-model="nuevoInsumo.unidad" required>
        <option disabled value="">Unidad</option>
        <option v-for="u in unidadesDisponibles" :key="u">{{ u }}</option>
      </select>
      <button type="submit">Agregar</button>
      <button class="secondary" @click="imprimirPDF" style="margin-top: 1rem;">🖨️ Imprimir Inventario</button>
    </form>

    <!-- Tabla -->
    <table class="tabla-inventario">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Cantidad</th>
          <th>Unidad</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in inventario" :key="item.id">
          <td>
            <template v-if="item.editando">
              <input v-model="item.nombre" />
            </template>
            <template v-else>
              {{ item.nombre }}
            </template>
          </td>

          <td>
            {{ item.cantidad.toFixed(2) }}
            <span v-if="item.cantidad <= 4 && item.cantidad >= 2" style="color: #d35400; font-weight: bold;">⚠️ Rellenar stock</span>
            <span v-else-if="item.cantidad < 2" style="color: red; font-weight: bold;">❌ Muy bajo</span>
          </td>

          <td>
            <template v-if="item.editando">
              <select v-model="item.unidad">
                <option disabled value="">Unidad</option>
                <option v-for="u in unidadesDisponibles" :key="u">{{ u }}</option>
              </select>
            </template>
            <template v-else>
              {{ item.unidad }}
            </template>
          </td>

          <td>
            <template v-if="item.editando">
              <button @click="guardarEdicion(item)">Guardar</button>
              <button @click="cancelarEdicion(item)">Cancelar</button>
            </template>
            <template v-else>
              <button @click="mostrarCampoConsumo(item)">Consumir</button>
              <button @click="mostrarCampoReabastecer(item)">➕ Reabastecer</button>
              <button @click="iniciarEdicion(item)">✏️</button>
              <button @click="eliminarInsumo(item.id)">🗑️</button>
            </template>

            <!-- Consumir -->
            <div v-if="item.mostrarCampo">
              <input type="number" v-model.number="item.cantidadConsumir" placeholder="Cantidad" style="width: 70px" />
              <select v-model="item.unidadConsumir">
                <option disabled value="">Unidad</option>
                <option v-for="u in unidadesDisponibles" :key="u">{{ u }}</option>
              </select>
              <button @click="consumir(item)">OK</button>
              <button @click="item.mostrarCampo = false">Cancelar</button>
              <div v-if="item.error" style="color: red;">{{ item.error }}</div>
            </div>

            <!-- Reabastecer -->
            <div v-if="item.mostrarCampoReabastecer">
              <input type="number" v-model.number="item.cantidadReabastecer" placeholder="Cantidad" style="width: 70px" />
              <select v-model="item.unidadReabastecer">
                <option disabled value="">Unidad</option>
                <option v-for="u in unidadesDisponibles" :key="u">{{ u }}</option>
              </select>
              <button @click="reabastecer(item)">OK</button>
              <button @click="item.mostrarCampoReabastecer = false">Cancelar</button>
              <div v-if="item.errorReabastecer" style="color: red;">{{ item.errorReabastecer }}</div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

import {
  fetchInventario,
  agregarInsumo,
  actualizarCantidadInsumo,
  editarNombreUnidadInsumo,
  eliminarInsumoPorId,
  consumirInsumo,
  descargarInventarioPDF
} from '../api'

const inventario = ref([])
const nuevoInsumo = ref({ nombre: '', cantidad: '', unidad: '' })
const unidadesDisponibles = ['kg', 'g', 'l', 'ml', 'piezas']
const alertasStock = ref([])

// 📦 Obtener inventario
const obtenerInventario = async () => {
  try {
    const data = await fetchInventario()
    inventario.value = data.map(item => ({
      ...item,
      mostrarCampo: false,
      mostrarCampoReabastecer: false,
      cantidadConsumir: '',
      unidadConsumir: '',
      cantidadReabastecer: '',
      unidadReabastecer: '',
      error: '',
      errorReabastecer: '',
      editando: false,
      nombreOriginal: item.nombre,
      unidadOriginal: item.unidad
    }))
    verificarStockBajo()
  } catch (error) {
    console.error("Error cargando inventario", error)
  }
}

// 🔔 Verificar stock bajo
const verificarStockBajo = () => {
  alertasStock.value = inventario.value.filter(item => item.cantidad < 4)
}

// ➕ Agregar insumo
const agregarNuevoInsumo = async () => {
  const form = new FormData()
  form.append('nombre', nuevoInsumo.value.nombre)
  form.append('cantidad', nuevoInsumo.value.cantidad)
  form.append('unidad', nuevoInsumo.value.unidad)

  const res = await agregarInsumo(form)
  if (res.ok) {
    nuevoInsumo.value = { nombre: '', cantidad: '', unidad: '' }
    await obtenerInventario()
  }
}

// 🧮 Mostrar campo para consumir
const mostrarCampoConsumo = (item) => {
  item.mostrarCampo = true
  item.cantidadConsumir = ''
  item.unidadConsumir = ''
  item.error = ''
}

// ➕ Mostrar campo para reabastecer
const mostrarCampoReabastecer = (item) => {
  item.mostrarCampoReabastecer = true
  item.cantidadReabastecer = ''
  item.unidadReabastecer = ''
  item.errorReabastecer = ''
}

// 🔄 Conversión de unidades
const convertir = (valor, de, a) => {
  const conversiones = {
    kg: { g: v => v * 1000 },
    g: { kg: v => v / 1000 },
    l: { ml: v => v * 1000 },
    ml: { l: v => v / 1000 }
  }
  return de === a ? valor : conversiones[de]?.[a]?.(valor)
}

// 🔥 Consumir insumo
const consumir = async (item) => {
  const { cantidadConsumir, unidadConsumir } = item
  if (!cantidadConsumir || cantidadConsumir <= 0 || !unidadConsumir) {
    item.error = 'Completa todos los campos.'
    return
  }

  const usado = convertir(cantidadConsumir, unidadConsumir, item.unidad)
  if (usado === undefined) {
    item.error = 'Unidades incompatibles.'
    return
  }

  if (item.cantidad - usado < 0) {
    item.error = 'Cantidad insuficiente.'
    return
  }

  const form = new FormData()
  form.append('cantidad_usada', usado)
  form.append('unidad', item.unidad)

  const res = await consumirInsumo(item.id, form)
  if (res.ok) obtenerInventario()
}

// 🔄 Reabastecer insumo
const reabastecer = async (item) => {
  const { cantidadReabastecer, unidadReabastecer } = item
  if (!cantidadReabastecer || cantidadReabastecer <= 0 || !unidadReabastecer) {
    item.errorReabastecer = 'Completa todos los campos.'
    return
  }

  const aumento = convertir(cantidadReabastecer, unidadReabastecer, item.unidad)
  if (aumento === undefined) {
    item.errorReabastecer = 'Unidades incompatibles.'
    return
  }

  const form = new FormData()
  form.append('cantidad_agregada', aumento)
  form.append('unidad', item.unidad)

  const res = await actualizarCantidadInsumo(item.id, form)
  if (res.ok) {
    await obtenerInventario()
    item.mostrarCampoReabastecer = false
  } else {
    item.errorReabastecer = 'Error al actualizar.'
  }
}

// 🗑️ Eliminar insumo
const eliminarInsumo = async (id) => {
  if (!confirm('¿Eliminar este insumo?')) return
  await eliminarInsumoPorId(id)
  obtenerInventario()
}

// ✏️ Edición
const iniciarEdicion = (item) => {
  item.editando = true
  item.nombreOriginal = item.nombre
  item.unidadOriginal = item.unidad
}

const cancelarEdicion = (item) => {
  item.nombre = item.nombreOriginal
  item.unidad = item.unidadOriginal
  item.editando = false
}

const guardarEdicion = async (item) => {
  const form = new FormData()
  form.append('nombre', item.nombre)
  form.append('unidad', item.unidad)

  const res = await editarNombreUnidadInsumo(item.id, form)
  if (res.ok) {
    item.editando = false
    obtenerInventario()
  } else {
    alert('Error al guardar los cambios.')
  }
}

// 🖨️ PDF
const imprimirPDF = () => {
  const doc = new jsPDF()
  doc.text("Reporte de Inventario - Cafetería", 14, 15)
  doc.setFontSize(10)
  doc.text(`Fecha: ${new Date().toLocaleDateString()}`, 14, 22)

  autoTable(doc, {
    startY: 28,
    head: [['Nombre', 'Cantidad', 'Unidad']],
    body: inventario.value.map(item => [
      item.nombre,
      item.cantidad.toFixed(2),
      item.unidad
    ])
  })

  doc.save(`Inventario_${new Date().toLocaleDateString()}.pdf`)
}

onMounted(obtenerInventario)
</script>


<style scoped>
button {
  background-color: #4CAF50; /* verde */
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  margin-right: 4px;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #45a049;
}

button.danger {
  background-color: #e74c3c;
}

button.danger:hover {
  background-color: #c0392b;
}

button.secondary {
  background-color: #3498db;
}

button.secondary:hover {
  background-color: #2980b9;
}

.form-inventario {
  margin-bottom: 1rem;
}

.form-inventario input,
.form-inventario select {
  margin-right: 0.5rem;
}

.tabla-inventario {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.tabla-inventario th,
.tabla-inventario td {
  border: 1px solid #ccc;
  padding: 8px;
}

.btn-pdf {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 14px;
  margin-bottom: 1rem;
  cursor: pointer;
  border-radius: 5px;
}

.btn-pdf:hover {
  background-color: #45a049;
}
.alerta-inventario {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
}
.alerta-inventario ul {
  margin-top: 0.5rem;
  padding-left: 1.2rem;
}


</style>
