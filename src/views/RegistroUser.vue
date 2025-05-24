<template>
  <div class="registro-page">
    <div class="registro-container">
      <!-- Lado Izquierdo -->
      <div class="left-side">
        <img :src="logo" alt="Logo Cafetería" class="logo" />
      </div>

      <!-- Lado Derecho -->
      <div class="right-side">
        <h2>CREAR CUENTA</h2>
        <h3>Regístrate con tus datos</h3>
        <form @submit.prevent="registrarUsuario">
          <input v-model="nombre" type="text" placeholder="Nombre Completo" class="input-field" required />
          <input v-model="correo" type="email" placeholder="Correo Electrónico" class="input-field" required />

          <select v-model="grado" class="input-field" required>
            <option disabled value="">Selecciona tu grado</option>
            <option v-for="n in 9" :key="n" :value="n">{{ n }}</option>
          </select>

          <select v-model="carrera" class="input-field" required>
            <option disabled value="">Selecciona tu carrera</option>
            <option>Ingeniería en Software</option>
            <option>Lengua</option>
            <option>Administración</option>
          </select>

          <input v-model="contraseña" type="password" placeholder="Contraseña" class="input-field" required />
          <input v-model="confirmar" type="password" placeholder="Confirmar Contraseña" class="input-field" required />

          <button type="submit" class="register-button">REGISTRARSE</button>
        </form>

        <p class="login-text">
          ¿Ya tienes una cuenta?
          <router-link to="/login" class="login-link">Inicia sesión aquí</router-link>
        </p>

        <p v-if="mensaje" :style="{ color: mensajeColor, marginTop: '10px' }">{{ mensaje }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import '../EstilosCss/registro.css'
import logo from '../assets/images/LogoCafe.png'
import { useRouter } from 'vue-router'

const router = useRouter()

const nombre = ref('')
const correo = ref('')
const grado = ref('')
const carrera = ref('')
const contrasena = ref('')
const confirmar = ref('')
const mensaje = ref('')
const mensajeColor = ref('green')

function validarCorreo(correo) {
  return correo.endsWith('@gmail.com') || correo.endsWith('@unach.mx')
}

async function registrarUsuario() {
  mensaje.value = ''

  if (!nombre.value || !correo.value || !grado.value || !carrera.value || !contrasena.value || !confirmar.value) {
    mensaje.value = 'Todos los campos son obligatorios.'
    mensajeColor.value = 'red'
    return
  }

  if (!validarCorreo(correo.value)) {
    mensaje.value = 'El correo debe ser @gmail.com o @unach.mx.'
    mensajeColor.value = 'red'
    return
  }

  if (contrasena.value !== confirmar.value) {
    mensaje.value = 'Las contraseñas no coinciden.'
    mensajeColor.value = 'red'
    return
  }

  try {
    const formData = new FormData()
    formData.append('nombre', nombre.value)
    formData.append('correo', correo.value)
    formData.append('grado', grado.value)
    formData.append('carrera', carrera.value)
    formData.append('contrasena', contrasena.value) // <- CORREGIDO

    const res = await fetch('https://cafeteria-admin-rowd.onrender.com/registro', {
      method: "POST",
      body: formData,
      mode: "cors"
    })

    if (!res.ok) {
      const data = await res.json()
      throw new Error(data?.detail || 'Error al registrar.')
    }

    mensaje.value = 'Registro exitoso. Redirigiendo...'
    mensajeColor.value = 'green'

    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    mensaje.value = err.message === 'Failed to fetch'
      ? 'No se pudo conectar al servidor.'
      : err.message
    mensajeColor.value = 'red'
  }
}
</script>
