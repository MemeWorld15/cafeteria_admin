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
          <input v-model="contrasena" type="password" placeholder="Contraseña" class="login-input" />
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

const correo = ref('')
const contraseña = ref('')
const error = ref('')
const router = useRouter()

/*NO USAR
  const handleLogin = () => {
  if (correo.value === 'admin@cafe.com' && contraseña.value === 'admin123') {
    router.push('/administrador')
  } else if (correo.value === 'cliente@cafe.com' && contraseña.value === 'cliente123') {
    router.push('/cliente')
  } else {
    error.value = 'Credenciales inválidas'
  }
}*/
const handleLogin = async () => {
  try {
    const formData = new FormData();
    formData.append("correo", correo.value);
    formData.append("contraseña", contraseña.value);

    const res = await fetch("https://cafeteria-admin-czwt.onrender.com/login", {
      method: "POST",
      body: formData,
      mode: "cors"
    });


    if (!res.ok) throw new Error("Credenciales inválidas");

    const data = await res.json();

   localStorage.setItem("usuario_id", data.usuario_id);
   localStorage.setItem('usuario_rol', data.rol)
   localStorage.setItem("usuario_nombre", data.nombre);



    if (data.rol === "admin") {
      router.push("/administrador");
    } else if (data.rol === "chef") {
      router.push("/cocina");
    } else {
      router.push("/menu");
    }
  } catch (err) {
    error.value = "Correo o contraseña incorrectos.";
  }
};

</script>
