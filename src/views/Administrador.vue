<template>
  <div class="admin-app">
    <!-- Topbar -->
    <header class="admin-topbar">
      <div class="admin-topbar-logo">
        <img :src="logo" alt="Logo" />
        <div>
          <span class="admin-brand">Cafetería</span><br />
          <span class="admin-role">Administrador</span>
        </div>
      </div>
      <div class="top-right">
        <i :class="isDarkMode ? 'fas fa-moon' : 'fas fa-sun'" @click="toggleDarkMode"></i>
        <i class="fas fa-bell"></i>
        <i class="fas fa-user"></i>
        <span class="admin-name">{{ nombreUsuario }}</span>
        <i class="fas fa-chevron-down"></i>
      </div>
    </header>

    <!-- Main Body -->
    <div class="admin-main-body">
      <!-- Sidebar -->
      <aside class="admin-sidebar" :class="{ collapsed: isCollapsed }">
        <div class="admin-toggle-btn" @click="toggleSidebar">
          <i class="fas fa-bars"></i>
        </div>
        <nav class="admin-nav">
          <ul>
            <li :class="{ active: vistaActual === 'menu' }" @click="cambiarVista('menu')">
              <i class="fas fa-utensils"></i><span>Menú</span>
            </li>
            <li :class="{ active: vistaActual === 'graficas' }" @click="cambiarVista('graficas')">
              <i class="fas fa-chart-pie"></i><span>Ventas</span>
            </li>
            <li :class="{ active: vistaActual === 'ordenes' }" @click="cambiarVista('ordenes')">
              <i class="fas fa-receipt"></i><span>Órdenes</span>
            </li>
            <li :class="{ active: vistaActual === 'usuarios' }" @click="cambiarVista('usuarios')">
              <i class="fas fa-users"></i><span>Usuarios</span>
            </li>
            <li :class="{ active: vistaActual === 'agregar-empleado' }" @click="cambiarVista('agregar-empleado')">
              <i class="fas fa-user-plus"></i><span>Agregar Empleados</span>
            </li>
            <li :class="{ active: vistaActual === 'inventario' }" @click="cambiarVista('inventario')">
              <i class="fas fa-box-open"></i><span>Inventario</span>
            </li>
            

          </ul>
        </nav>
        <div class="admin-settings">
          <i class="fas fa-cog"></i><span>Configuración</span>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="admin-content">
        <h2>Bienvenido al Panel de Administración</h2>

        <UsuariosCard v-if="vistaActual === 'usuarios'" />
        <div v-if="vistaActual === 'ordenes'">
  <h3>Órdenes registradas</h3>
  <table class="tabla-ordenes">
    <thead>
      <tr>
        <th>ID</th>
        <th>Cliente</th>
        <th>Fecha</th>
        <th>Hora</th>
        <th>Total</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="orden in ordenes" :key="orden.id">
        <td>{{ orden.id }}</td>
        <td>{{ orden.cliente }}</td>
        <td>{{ orden.fecha }}</td>
        <td>{{ orden.hora }}</td>
        <td>
          ${{ orden.productos.reduce((acc, p) => acc + p.cantidad * p.precio_unitario, 0).toFixed(2) }}
        </td>
        <td>
          <span :class="orden.entregado ? 'entregado' : 'no-entregado'">
            {{ orden.entregado ? 'Entregado' : 'Pendiente' }}
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</div>


        <!-- Formulario para crear empleados -->
        <div v-if="vistaActual === 'agregar-empleado'" class="form-empleado">
          <h3>Agregar Nuevo Empleado</h3>
          <form @submit.prevent="crearEmpleado">
            <input v-model="nuevoEmpleado.nombre" type="text" placeholder="Nombre completo" required />
            <input v-model="nuevoEmpleado.correo" type="email" placeholder="Correo" required />
            <select v-model="nuevoEmpleado.ocupacion" required>
              <option disabled value="">Seleccionar ocupación</option>
              <option value="chef">Chef</option>
            </select>

            <!--<input v-model="nuevoEmpleado.ocupacion" type="text" placeholder="Ocupación" required />-->
            <input v-model="nuevoEmpleado.rendimiento" type="text" placeholder="Teléfono" required />
            <input v-model="nuevoEmpleado.contraseña" type="text" placeholder="Contraseña" required />
            <button type="button" @click="generarContrasena">Generar Contraseña Aleatoria</button>

            <button type="submit">Registrar</button>
            <p v-if="mensaje" :style="{ color: mensajeColor }">{{ mensaje }}</p>
          </form>
        </div>

        <!-- Formulario para gestionar el menú -->
        <div v-if="vistaActual === 'menu'" class="admin-menu-form">
          <h3>Agregar Categoría</h3>
          <form @submit.prevent="crearCategoria">
            <input v-model="nuevaCategoria" type="text" placeholder="Nombre de categoría" required />
            <button type="submit">Agregar Categoría</button>
          </form>
          <!-- Identar muy bien -->
          <h3 style="margin-top: 2rem;">Categorías Existentes</h3>
          <ul class="lista-categorias">
            <li v-for="cat in categorias" :key="cat.id">
              <input v-if="categoriaEditando?.id === cat.id" v-model="categoriaEditando.nombre" />
              <span v-else>{{ cat.nombre }}</span>

              <button v-if="categoriaEditando?.id === cat.id" @click="guardarEdicionCategoria">Guardar</button>
              <button v-if="categoriaEditando?.id === cat.id" @click="cancelarEdicionCategoria">Cancelar</button>
              
              <button v-else @click="iniciarEdicionCategoria(cat)">✏️</button>
              <button @click="eliminarCategoria(cat.id)">🗑️</button>
            </li>
          </ul>


          <h3 style="margin-top: 2rem;">Agregar Producto</h3>
          <form @submit.prevent="crearProducto">
            <input v-model="nuevoProducto.nombre" type="text" placeholder="Nombre del producto" required />
            <textarea v-model="nuevoProducto.descripcion" placeholder="Descripción" required></textarea>
            <input v-model="nuevoProducto.precio" type="number" placeholder="Precio" required />
            <select v-model="nuevoProducto.categoria_id" required>
              <option disabled value="">Seleccionar categoría</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
            </select>
            <button type="submit">Agregar Producto</button>
          </form>

          <!-- Productos existentes -->
          <h3 style="margin-top: 3rem;">Productos Existentes</h3>
          <table class="tabla-productos">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Precio</th>
                <th>Categoría</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="prod in productos" :key="prod.id">
                <td>{{ prod.nombre }}</td>
                <td>${{ prod.precio }}</td>
                <td>{{ categorias.find(cat => cat.id === prod.categoria_id)?.nombre || '—' }}</td>
                <td>
                  <button @click="editarProducto(prod)">✏️</button>
                  <button @click="eliminarProducto(prod.id)">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Formulario edición -->
          <div v-if="productoEditando" class="editar-producto-form">
            <h4>Editar Producto</h4>
            <input v-model="productoEditando.nombre" type="text" placeholder="Nombre" />
            <input v-model="productoEditando.precio" type="number" placeholder="Precio" />
            <textarea v-model="productoEditando.descripcion" placeholder="Descripción" />
            <select v-model="productoEditando.categoria_id">
              <option v-for="cat in categorias" :value="cat.id" :key="cat.id">{{ cat.nombre }}</option>
            </select>
            <button @click="guardarEdicion">Guardar</button>
            <button @click="productoEditando = null">Cancelar</button>
          </div>

          <p v-if="mensajeMenu" :style="{ color: mensajeColor, marginTop: '1rem' }">{{ mensajeMenu }}</p>
        </div>
        <GraficasTop v-if="vistaActual === 'graficas'" />
        <Inventario v-if="vistaActual === 'inventario'" />
      </div>
    </div>
  </div>
  
</template>

<!--<script setup>
import { ref, onMounted } from 'vue'
import logo from '../assets/images/LogoCafe.png'
import UsuariosCard from './UsuariosCard.vue'
import '../EstilosCss/AdminStylo.css'

const isCollapsed = ref(false)
const vistaActual = ref('menu')

const cambiarVista = (vista) => {
  vistaActual.value = vista
}

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleDarkMode = () => {
  document.body.classList.toggle('dark-mode')
}

// Empleados
const nuevoEmpleado = ref({
  nombre: '',
  correo: '',
  ocupacion: '',
  rendimiento: ''
})
const mensaje = ref('')
const mensajeColor = ref('green')

const crearEmpleado = async () => {
  mensaje.value = ''
  try {
    const formData = new FormData()
    Object.entries(nuevoEmpleado.value).forEach(([key, val]) =>
      formData.append(key, val)
    )
    formData.append('creado_por', 1)
    const res = await fetch('http://localhost:8000/empleados', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error()
    mensaje.value = 'Empleado creado exitosamente.'
    mensajeColor.value = 'green'
    nuevoEmpleado.value = { nombre: '', correo: '', ocupacion: '', rendimiento: '' }
  } catch (err) {
    mensaje.value = 'Error al registrar empleado.'
    mensajeColor.value = 'red'
  }
}

// Menú
const nuevaCategoria = ref('')
const nuevoProducto = ref({ nombre: '', descripcion: '', precio: '', categoria_id: '' })
const categorias = ref([])
const productos = ref([])
const mensajeMenu = ref('')
const productoEditando = ref(null)

const crearCategoria = async () => {
  mensajeMenu.value = ''
  try {
    const formData = new FormData()
    formData.append('nombre', nuevaCategoria.value)
    const res = await fetch('http://localhost:8000/categorias', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error()
    mensajeMenu.value = 'Categoría agregada.'
    mensajeColor.value = 'green'
    nuevaCategoria.value = ''
    obtenerCategorias()
  } catch (err) {
    mensajeMenu.value = 'Error al agregar categoría.'
    mensajeColor.value = 'red'
  }
}
const categoriaEditando = ref(null)

const iniciarEdicionCategoria = (categoria) => {
  categoriaEditando.value = { ...categoria }
}

const cancelarEdicionCategoria = () => {
  categoriaEditando.value = null
}

const guardarEdicionCategoria = async () => {
  const formData = new FormData()
  formData.append('nombre', categoriaEditando.value.nombre)

  const res = await fetch(`http://localhost:8000/categorias/${categoriaEditando.value.id}`, {
    method: 'PUT',
    body: formData
  })

  if (res.ok) {
    mensajeMenu.value = 'Categoría actualizada.'
    mensajeColor.value = 'green'
    categoriaEditando.value = null
    obtenerCategorias()
  } else {
    mensajeMenu.value = 'Error al actualizar categoría.'
    mensajeColor.value = 'red'
  }
}

const eliminarCategoria = async (id) => {
  if (!confirm("¿Eliminar esta categoría? Esto podría afectar productos asociados.")) return

  const res = await fetch(`http://localhost:8000/categorias/${id}`, {
    method: 'DELETE'
  })

  if (res.ok) {
    mensajeMenu.value = 'Categoría eliminada.'
    mensajeColor.value = 'green'
    obtenerCategorias()
  } else {
    mensajeMenu.value = 'No se pudo eliminar la categoría.'
    mensajeColor.value = 'red'
  }
}


const crearProducto = async () => {
  mensajeMenu.value = ''
  try {
    const formData = new FormData()
    for (const [key, val] of Object.entries(nuevoProducto.value)) {
      formData.append(key, val)
    }
    const res = await fetch('http://localhost:8000/productos', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error()
    mensajeMenu.value = 'Producto agregado.'
    mensajeColor.value = 'green'
    nuevoProducto.value = { nombre: '', descripcion: '', precio: '', categoria_id: '' }
    obtenerProductos()
  } catch (err) {
    mensajeMenu.value = 'Error al agregar producto.'
    mensajeColor.value = 'red'
  }
}

const obtenerCategorias = async () => {
  const res = await fetch('http://localhost:8000/categorias')
  categorias.value = await res.json()
}

const obtenerProductos = async () => {
  const res = await fetch('http://localhost:8000/productos')
  productos.value = await res.json()
}

const eliminarProducto = async (id) => {
  if (!confirm("¿Eliminar este producto?")) return
  const res = await fetch(`http://localhost:8000/productos/${id}`, {
    method: 'DELETE'
  })
  if (res.ok) {
    mensajeMenu.value = 'Producto eliminado.'
    mensajeColor.value = 'green'
    obtenerProductos()
  }
}

const editarProducto = (prod) => {
  productoEditando.value = { ...prod }
}

const guardarEdicion = async () => {
  const formData = new FormData()
  for (const [key, val] of Object.entries(productoEditando.value)) {
    formData.append(key, val)
  }
  const res = await fetch(`http://localhost:8000/productos/${productoEditando.value.id}`, {
    method: 'PUT',
    body: formData
  })
  if (res.ok) {
    mensajeMenu.value = 'Producto actualizado.'
    mensajeColor.value = 'green'
    productoEditando.value = null
    obtenerProductos()
  }
}

onMounted(() => {
  obtenerCategorias()
  obtenerProductos()
})
</script>-->
<script setup>
import { ref, onMounted } from 'vue'
import logo from '../assets/images/LogoCafe.png'
import UsuariosCard from './UsuariosCard.vue'
import '../EstilosCss/AdminStylo.css'
import GraficasTop from './GraficasTop.vue'
import Inventario from './Inventario.vue'



const isCollapsed = ref(false)
const vistaActual = ref('menu')

const cambiarVista = (vista) => {
  vistaActual.value = vista
}

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const isDarkMode = ref(false)

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  document.body.classList.toggle('dark-mode', isDarkMode.value)
  localStorage.setItem('modo_oscuro', isDarkMode.value ? 'true' : 'false')
}



// Empleados
const nuevoEmpleado = ref({
  nombre: '',
  correo: '',
  ocupacion: '',
  rendimiento: '',
  contraseña: ''
})

const mensaje = ref('')
const mensajeColor = ref('green')

const crearEmpleado = async () => {
  mensaje.value = ''
  try {
    const creadorId = parseInt(localStorage.getItem('usuario_id') || '0')

    if (!creadorId) {
      mensaje.value = 'Error: usuario no autenticado.'
      mensajeColor.value = 'red'
      return
    }

    const formData = new FormData()
    Object.entries(nuevoEmpleado.value).forEach(([key, val]) =>
      formData.append(key, val)
    )
    formData.append('creado_por', creadorId)

    const res = await fetch('http://localhost:8000/empleados', {
      method: 'POST',
      body: formData
    })

    if (!res.ok) {
      const errorData = await res.json()
      console.error(errorData)
      throw new Error()
    }

    mensaje.value = 'Empleado creado exitosamente.'
    mensajeColor.value = 'green'

    // Resetear el formulario
    nuevoEmpleado.value = {
      nombre: '',
      correo: '',
      ocupacion: '',
      rendimiento: '',
      contraseña: ''
    }
  } catch (err) {
    mensaje.value = 'Error al registrar empleado.'
    mensajeColor.value = 'red'
  }
}

const generarContrasena = () => {
  const caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  let password = ""
  for (let i = 0; i < 8; i++) {
    password += caracteres.charAt(Math.floor(Math.random() * caracteres.length))
  }
  nuevoEmpleado.value.contraseña = password
}


// Menú
const nuevaCategoria = ref('')
const nuevoProducto = ref({ nombre: '', descripcion: '', precio: '', categoria_id: '' })
const categorias = ref([])
const productos = ref([])
const mensajeMenu = ref('')
const productoEditando = ref(null)
const ordenes = ref([])
const nombreUsuario = ref('')


const crearCategoria = async () => {
  mensajeMenu.value = ''
  try {
    const formData = new FormData()
    formData.append('nombre', nuevaCategoria.value)
    const res = await fetch('http://localhost:8000/categorias', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error()
    mensajeMenu.value = 'Categoría agregada.'
    mensajeColor.value = 'green'
    nuevaCategoria.value = ''
    obtenerCategorias()
  } catch (err) {
    mensajeMenu.value = 'Error al agregar categoría.'
    mensajeColor.value = 'red'
  }
}
const crearProducto = async () => {
  mensajeMenu.value = ''
  try {
    const formData = new FormData()
    for (const [key, val] of Object.entries(nuevoProducto.value)) {
      formData.append(key, val)
    }

    const res = await fetch('http://localhost:8000/productos', {
      method: 'POST',
      body: formData
    })

    if (!res.ok) throw new Error()

    mensajeMenu.value = 'Producto agregado.'
    mensajeColor.value = 'green'
    nuevoProducto.value = { nombre: '', descripcion: '', precio: '', categoria_id: '' }
    obtenerProductos()
  } catch (err) {
    mensajeMenu.value = 'Error al agregar producto.'
    mensajeColor.value = 'red'
  }
}


const obtenerCategorias = async () => {
  const res = await fetch('http://localhost:8000/categorias')
  categorias.value = await res.json()
}

const obtenerProductos = async () => {
  const res = await fetch('http://localhost:8000/productos')
  productos.value = await res.json()
}

const obtenerOrdenes = async () => {
  const res = await fetch('http://localhost:8000/ordenes')
  ordenes.value = await res.json()
}

const eliminarCategoria = async (id) => {
  if (!confirm("¿Eliminar esta categoría? Esto podría afectar productos asociados.")) return

  const res = await fetch(`http://localhost:8000/categorias/${id}`, {
    method: 'DELETE'
  })

  if (res.ok) {
    mensajeMenu.value = 'Categoría eliminada.'
    mensajeColor.value = 'green'
    obtenerCategorias()
  } else {
    mensajeMenu.value = 'No se pudo eliminar la categoría.'
    mensajeColor.value = 'red'
  }
}

const editarProducto = (prod) => {
  productoEditando.value = { ...prod }
}

const guardarEdicion = async () => {
  const formData = new FormData()
  for (const [key, val] of Object.entries(productoEditando.value)) {
    formData.append(key, val)
  }
  const res = await fetch(`http://localhost:8000/productos/${productoEditando.value.id}`, {
    method: 'PUT',
    body: formData
  })
  if (res.ok) {
    mensajeMenu.value = 'Producto actualizado.'
    mensajeColor.value = 'green'
    productoEditando.value = null
    obtenerProductos()
  }
}

const eliminarProducto = async (id) => {
  if (!confirm("¿Eliminar este producto?")) return
  const res = await fetch(`http://localhost:8000/productos/${id}`, {
    method: 'DELETE'
  })
  if (res.ok) {
    mensajeMenu.value = 'Producto eliminado.'
    mensajeColor.value = 'green'
    obtenerProductos()
  }
}

const categoriaEditando = ref(null)

const iniciarEdicionCategoria = (categoria) => {
  categoriaEditando.value = { ...categoria }
}

const cancelarEdicionCategoria = () => {
  categoriaEditando.value = null
}

const guardarEdicionCategoria = async () => {
  const formData = new FormData()
  formData.append('nombre', categoriaEditando.value.nombre)

  const res = await fetch(`http://localhost:8000/categorias/${categoriaEditando.value.id}`, {
    method: 'PUT',
    body: formData
  })

  if (res.ok) {
    mensajeMenu.value = 'Categoría actualizada.'
    mensajeColor.value = 'green'
    categoriaEditando.value = null
    obtenerCategorias()
  } else {
    mensajeMenu.value = 'Error al actualizar categoría.'
    mensajeColor.value = 'red'
  }
}

onMounted(() => {
  nombreUsuario.value = localStorage.getItem('usuario_nombre') || 'Usuario'
  obtenerCategorias()
  obtenerProductos()
  obtenerOrdenes()
  isDarkMode.value = localStorage.getItem('modo_oscuro') === 'true'
  if (isDarkMode.value) {
    document.body.classList.add('dark-mode')
  }
})
</script>