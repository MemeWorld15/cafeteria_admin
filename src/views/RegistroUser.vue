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

const nombre = ref('')
const correo = ref('')
const grado = ref('')
const carrera = ref('')
const contraseña = ref('')
const confirmar = ref('')
const mensaje = ref('')
const mensajeColor = ref('green')

function validarCorreo(correo) {
  return correo.endsWith('@gmail.com') || correo.endsWith('@unach.mx')
}

async function registrarUsuario() {
  mensaje.value = ''

  // Validaciones frontend
  if (!nombre.value || !correo.value || !grado.value || !carrera.value || !contraseña.value || !confirmar.value) {
    mensaje.value = 'Todos los campos son obligatorios.'
    mensajeColor.value = 'red'
    return
  }

  if (!validarCorreo(correo.value)) {
    mensaje.value = 'El correo debe ser @gmail.com o @unach.mx.'
    mensajeColor.value = 'red'
    return
  }

  if (contraseña.value !== confirmar.value) {
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
    formData.append('contraseña', contraseña.value)

    const res = await fetch('https://cafeteria-admin-rowd.onrender.com', {
       method: "POST",
       body: formData,
       mode: "cors"
    })

    if (!res.ok) throw new Error()

    mensaje.value = 'Registro exitoso. Redirigiendo...'
    mensajeColor.value = 'green'

    setTimeout(() => {
      window.location.href = '/login'
    }, 2000)
  } catch (err) {
    mensaje.value = 'Error al registrar. El correo ya existe.'
    mensajeColor.value = 'red'
  }
}
</script>
