<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Lado Izquierdo -->
      <div class="login-left">
        <img :src="logo" alt="Logo Cafetería" class="login-logo" />
      </div>

      <!-- Lado Derecho -->
      <div class="login-right">
        <h2>BIENVENIDO</h2>
        <h3>Ingrese a su cuenta</h3>
        <form @submit.prevent="handleLogin">
          <input v-model="correo" type="email" placeholder="Correo Electrónico" class="login-input" />

          <!-- Campo de contraseña con botón para mostrar/ocultar -->
          <div class="password-wrapper" style="position: relative;">
            <input
              :type="mostrarContrasena ? 'text' : 'password'"
              v-model="contrasena"
              placeholder="Contraseña"
              class="login-input"
            />
            <i
              class="fas"
              :class="mostrarContrasena ? 'fa-eye-slash' : 'fa-eye'"
              @click="toggleContrasena"
              style="cursor: pointer; position: absolute; right: 10px; top: 12px;"
            ></i>
          </div>

          <button type="submit" class="login-button">INICIAR SESIÓN</button>
        </form>

        <p class="login-registro-text">
          ¿No tienes una cuenta?
          <router-link to="/registro" class="login-registro-link">Regístrate aquí</router-link>
        </p>
        <p v-if="error" style="color: red;">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logo from '../assets/images/LogoCafe.png'
import '../EstilosCss/login.css'
import { login } from '../api' 

const correo = ref('')
const contrasena = ref('')
const error = ref('')
const mostrarContrasena = ref(false)
const router = useRouter()

const toggleContrasena = () => {
  mostrarContrasena.value = !mostrarContrasena.value
}

const handleLogin = async () => {
  try {
    const res = await login(correo.value, contrasena.value)

    if (!res.ok) throw new Error()

    const data = await res.json()

    localStorage.setItem('usuario_id', data.usuario_id)
    localStorage.setItem('usuario_rol', data.rol)
    localStorage.setItem('usuario_nombre', data.nombre)

    if (data.rol === 'admin') {
      router.push('/administrador')
    } else if (data.rol === 'chef') {
      router.push('/cocina')
    } else {
      router.push('/menu')
    }
  } catch (err) {
    error.value = 'Correo o contraseña incorrectos.'
  }
}
</script>

