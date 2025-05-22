import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegistroUser from '../views/RegistroUser.vue'
import Administrador from '../views/Administrador.vue'
import ClienteCompra from '../views/ClienteCompra.vue'
import MenuCafe from '../views/MenuCafe.vue'
import UsuariosCard from '../views/UsuariosCard.vue'
import Cocina from '../views/Cocina.vue' // 👈 NUEVO

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/registro',
    name: 'registro',
    component: RegistroUser
  },
  {
    path: '/administrador',
    name: 'administrador',
    component: Administrador
  },
  {
    path: '/cliente',
    name: 'cliente',
    component: ClienteCompra
  },
  {
    path: '/menu',
    name: 'menu',
    component: MenuCafe
  },
  {
    path: '/empleados',
    name: 'empleados',
    component: UsuariosCard
  },
  {
    path: '/cocina', // 👈 NUEVA RUTA
    name: 'cocina',
    component: Cocina
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
