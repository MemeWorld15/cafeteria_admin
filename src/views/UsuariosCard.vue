<template>
  <div class="usuarios-card">
    <h3>Empleados Registrados</h3>
    <!-- Mensaje de éxito o error -->
    <p v-if="mensaje" :class="['alerta', mensajeColor]">
      {{ mensaje }}
    </p>

    <table v-if="empleados.length > 0">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Ocupación</th>
          <th>Correo</th>
          <th>Rendimiento</th>
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
          <!--<td><i class="fas fa-trash-alt trash-icon"></i></td>-->
          <td><i class="fas fa-trash-alt trash-icon" @click="eliminarEmpleado(emp.id)"></i></td>
        </tr>
      </tbody>
    </table>

    <p v-else style="margin-top: 1rem; color: #888;">No hay empleados registrados aún.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchEmpleados, eliminarEmpleadoPorId } from '../api'

const empleados = ref([])
const defaultAvatar = 'https://i.pravatar.cc/50?img=11'

const cargarEmpleados = async () => {
  try {
    empleados.value = await fetchEmpleados()
  } catch (err) {
    console.error('Error al cargar empleados:', err)
  }
}

const eliminarEmpleado = async (id) => {
  if (!confirm('¿Estás seguro de eliminar este empleado?')) return
  try {
    await eliminarEmpleadoPorId(id)
    mensaje.value = 'El empleado ha sido eliminado.'
    mensajeColor.value = 'green'
    await cargarEmpleados()
  } catch (err) {
    console.error('Error al eliminar empleado:', err)
    mensaje.value = 'Error al eliminar el empleado.'
    mensajeColor.value = 'red'
  }

  // Ocultar el mensaje después de unos segundos
  setTimeout(() => {
    mensaje.value = ''
  }, 3000)
}


onMounted(cargarEmpleados)
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
/* Estilos para mensajes */
.alerta {
  padding: 0.8rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-weight: bold;
}

.success {
  background-color: #e9f7ef;
  color: #27ae60;
  border: 1px solid #27ae60;
}

.error {
  background-color: #fdecea;
  color: #c0392b;
  border: 1px solid #c0392b;
}
</style>
