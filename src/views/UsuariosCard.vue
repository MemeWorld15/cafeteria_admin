<template>
  <div class="usuarios-card">
    <h3>Empleados Registrados</h3>

    <!-- Mensaje de eliminación -->
    <p v-if="mensaje" :class="['alerta', mensajeColor]">{{ mensaje }}</p>

    <table v-if="empleados.length > 0">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Ocupación</th>
          <th>Correo</th>
          <th>Rendimiento</th>
          <th>Contraseña</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="emp in empleados" :key="emp.id">
          <td>
            <img :src="emp.foto || defaultAvatar" class="avatar" />
            {{ emp.nombre }}
          </td>
          <td>{{ emp.ocupacion }}</td>
          <td>{{ emp.correo }}</td>
          <td class="tel-verde">{{ emp.rendimiento }}</td>
          <td>
            <span>
              {{ mostrarContrasenas[emp.id] ? emp.contrasena : '••••••' }}
            </span>
            <i
              class="fas"
              :class="mostrarContrasenas[emp.id] ? 'fa-eye-slash' : 'fa-eye'"
              @click="toggleContrasena(emp.id)"
              style="margin-left: 0.5rem; cursor: pointer;"
            ></i>
          </td>
          <td>
            <i class="fas fa-trash-alt trash-icon" @click="eliminarEmpleado(emp.id)"></i>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else style="margin-top: 1rem; color: #888;">No hay empleados registrados aún.</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchEmpleados, eliminarEmpleadoPorId } from '../api'

const empleados = ref([])
const defaultAvatar = 'https://i.pravatar.cc/50?img=11'

const mensaje = ref('')
const mensajeColor = ref('success')

// Mostrar/ocultar contraseña por empleado
const mostrarContrasenas = ref({})

const toggleContrasena = (id) => {
  mostrarContrasenas.value[id] = !mostrarContrasenas.value[id]
}

// Cargar empleados desde API
const cargarEmpleados = async () => {
  try {
    empleados.value = await fetchEmpleados()
  } catch (err) {
    mensaje.value = 'Error al cargar empleados.'
    mensajeColor.value = 'error'
  }
}

// Eliminar empleado
const eliminarEmpleado = async (id) => {
  if (!confirm('¿Estás seguro de eliminar este empleado?')) return

  try {
    const res = await eliminarEmpleadoPorId(id)
    if (!res.ok) throw new Error()

    mensaje.value = 'El empleado ha sido eliminado.'
    mensajeColor.value = 'success'
    await cargarEmpleados()
  } catch {
    mensaje.value = 'Error al eliminar empleado.'
    mensajeColor.value = 'error'
  }

  setTimeout(() => (mensaje.value = ''), 3000)
}

onMounted(() => {
  cargarEmpleados()
})
</script>

<style scoped>
.usuarios-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
  margin-top: 1rem;
  overflow-x: auto;
}

.usuarios-card table {
  width: 100%;
  border-collapse: collapse;
}

.usuarios-card th,
.usuarios-card td {
  padding: 0.8rem;
  text-align: left;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.tel-verde {
  color: #0a9f67;
  font-weight: bold;
}

.trash-icon {
  color: #e74c3c;
  cursor: pointer;
}

/* Mensajes */
.alerta {
  margin-top: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
}

.success {
  background-color: #e0f9e5;
  color: #2e7d32;
}

.error {
  background-color: #fdecea;
  color: #c62828;
}
</style>
