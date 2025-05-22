<template>
  <div class="admin-inventario">
    <h3>Inventario</h3>

    <!-- Formulario para agregar -->
    <form @submit.prevent="agregarInsumo" class="form-inventario">
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
  <span v-if="item.cantidad <= 4 && item.cantidad >= 2" style="color: #d35400; font-weight: bold;">
    ⚠️ Rellenar stock
  </span>
  <span v-else-if="item.cantidad < 2" style="color: red; font-weight: bold;">
    ❌ Muy bajo
  </span>
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
              <button @click="iniciarEdicion(item)">✏️</button>
              <button @click="eliminarInsumo(item.id)">🗑️</button>
            </template>

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
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

const inventario = ref([])
const nuevoInsumo = ref({ nombre: '', cantidad: '', unidad: '' })
const unidadesDisponibles = ['kg', 'g', 'l', 'ml', 'piezas']




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
const descargarPDF = () => {
  window.open("http://localhost:8000/inventario/pdf", "_blank")
}



// Obtener datos
const obtenerInventario = async () => {
  const res = await fetch('http://localhost:8000/inventario')
  const data = await res.json()
  inventario.value = data.map(item => ({
    ...item,
    mostrarCampo: false,
    cantidadConsumir: '',
    unidadConsumir: '',
    error: '',
    editando: false,
    nombreOriginal: item.nombre,
    unidadOriginal: item.unidad
  }))
}

// Agregar nuevo insumo
const agregarInsumo = async () => {
  const formData = new FormData()
  formData.append('nombre', nuevoInsumo.value.nombre)
  formData.append('cantidad', nuevoInsumo.value.cantidad)
  formData.append('unidad', nuevoInsumo.value.unidad)

  const res = await fetch('http://localhost:8000/inventario', {
    method: 'POST',
    body: formData
  })

  if (res.ok) {
    obtenerInventario()
    nuevoInsumo.value = { nombre: '', cantidad: '', unidad: '' }
  }
}

// Mostrar campo de consumo
const mostrarCampoConsumo = (item) => {
  item.mostrarCampo = true
  item.cantidadConsumir = ''
  item.unidadConsumir = ''
  item.error = ''
}

// Conversión entre unidades compatibles
const convertir = (valor, de, a) => {
  const conversiones = {
    kg: { g: v => v * 1000 },
    g: { kg: v => v / 1000 },
    l: { ml: v => v * 1000 },
    ml: { l: v => v / 1000 }
  }
  return de === a ? valor : conversiones[de]?.[a]?.(valor)
}

// Consumir cantidad
const consumir = async (item) => {
  const usado = item.cantidadConsumir
  const unidadUsada = item.unidadConsumir
  const actual = item.cantidad
  const unidadActual = item.unidad

  if (!usado || usado <= 0 || !unidadUsada) {
    item.error = 'Completa los datos correctamente.'
    return
  }

  let usadoConvertido = convertir(usado, unidadUsada, unidadActual)

  if (usadoConvertido === undefined) {
    item.error = 'Unidades incompatibles.'
    return
  }

  const restante = actual - usadoConvertido

  if (restante < 0) {
    item.error = 'No puedes consumir más de lo disponible.'
    return
  }

  const formData = new FormData()
  formData.append('cantidad', restante)

  const res = await fetch(`http://localhost:8000/inventario/${item.id}`, {
    method: 'PUT',
    body: formData
  })

  if (res.ok) {
    obtenerInventario()
  }
}

// Eliminar insumo
const eliminarInsumo = async (id) => {
  if (!confirm("¿Eliminar este insumo?")) return
  await fetch(`http://localhost:8000/inventario/${id}`, { method: 'DELETE' })
  obtenerInventario()
}

// Editar nombre/unidad
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
  const formData = new FormData()
  formData.append('nombre', item.nombre)
  formData.append('unidad', item.unidad)

  const res = await fetch(`http://localhost:8000/inventario/${item.id}/editar`, {
    method: 'PUT',
    body: formData
  })

  if (res.ok) {
    item.editando = false
    obtenerInventario()
  } else {
    alert("Error al guardar los cambios.")
  }
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

</style>
