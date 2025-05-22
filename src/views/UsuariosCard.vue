<template>
  <div class="usuarios-card">
    <h3>Empleados Registrados</h3>

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
          <td><i class="fas fa-trash-alt trash-icon"></i></td>
        </tr>
      </tbody>
    </table>

    <p v-else style="margin-top: 1rem; color: #888;">No hay empleados registrados aún.</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const empleados = ref([])
const defaultAvatar = 'https://i.pravatar.cc/50?img=11' // backup img

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/empleados')
    if (!res.ok) throw new Error('Error al cargar empleados')
    empleados.value = await res.json()
  } catch (err) {
    console.error('Error:', err)
  }
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
</style>
