<template>
  <div class="menu-app">
    <!-- Topbar -->
    <header class="menu-topbar">
      <div class="menu-topbar-logo">
        <img :src="logo" alt="Logo" />
        <div>
          <span class="menu-brand">Cafetería</span><br />
          <span class="menu-role">Cliente</span>
        </div>
      </div>
      <div class="top-right">
        <i class="fas fa-sun" @click="toggleDarkMode"></i>
        <i class="fas fa-user"></i>
        
        <span class="menu-name">{{ nombreUsuario }}</span>
        <!--<span class="menu-name">{{ nombreUsuario }}</span>-->
        <!--<span class="menu-name">Gavano</span>-->
        <!--<i class="fas fa-chevron-down"></i>-->
        <div class="dropdown" @click="toggleDropdown">
          <i class="fas fa-chevron-down"></i>
          <div v-if="mostrarDropdown" class="dropdown-menu" @click.stop>
            <p class="usuario-nombre">{{ nombreUsuario }}</p>
            <hr />
            <button class="logout-btn" @click="cerrarSesion">Cerrar sesión</button>
          </div>
        </div>
      </div>
    </header>

    <!-- Tabs -->
    <div class="menu-tabs">
      <button :class="{ active: vista === 'menu' }" @click="vista = 'menu'">Menú</button>
      <button :class="{ active: vista === 'ordenes' }" @click="vista = 'ordenes'">Órdenes</button>
    </div>

    <!-- Main Body -->
    <div class="menu-main-body">
      <!-- Vista Menú -->
      <template v-if="vista === 'menu'">
        <aside class="menu-sidebar scrollable">
          <h3>Categorías</h3>
          <ul>
            <li v-for="cat in categorias" :key="cat"
                :class="{ active: categoriaSeleccionada === cat }"
                @click="categoriaSeleccionada = cat">
              {{ cat }}
            </li>
            <li :class="{ active: categoriaSeleccionada === 'Todas' }" @click="categoriaSeleccionada = 'Todas'">
              Todas
            </li>
          </ul>
        </aside>

        <main class="menu-content">
          <input type="text" placeholder="Buscar..." class="menu-buscar" />
          <div class="menu-seccion scrollable">
            <div class="menu-titulo">Menú <span class="mesa">Mesa 1</span></div>
            <div v-for="categoria in categorias" :key="categoria"
                v-show="categoriaSeleccionada === 'Todas' || categoriaSeleccionada === categoria"
                class="menu-categoria">
              <h2 @click="toggleCategoria(categoria)" style="cursor: pointer;">
                {{ categoria }}
                <i :class="['fas', categoriaExpandida[categoria] ? 'fa-chevron-up' : 'fa-chevron-down']" style="margin-left: 8px;" />
              </h2>
              <div v-show="categoriaExpandida[categoria]">
              <div class="menu-item"
                  v-for="platillo in platillos[categoria]"
                  :key="platillo.nombre"
                  :class="{ 'no-disponible': platillo.disponible === false }"
                >
                  <div>
                    <strong>
                      {{ platillo.nombre }}
                      <span v-if="!platillo.disponible">(No disponible)</span>
                    </strong>
                    <p>{{ platillo.descripcion }}</p>
                  </div>
                  <div class="menu-precio">
                    ${{ parseFloat(platillo.precio).toFixed(2) }}
                    <button
                      @click="agregarProductoOrden(platillo)"
                      :disabled="!platillo.disponible"
                    >+</button>
                    <button
                      @click="disminuirProductoOrden(platillo)"
                      :disabled="!platillo.disponible"
                    >−</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <aside class="menu-orden scrollable">
          <h3>Orden</h3>
          <p><strong>Mesa</strong> 1</p>
          <div class="menu-resumen">
            <div v-if="orden.length === 0">Aún no hay productos en la orden.</div>
            <div v-else>
              <p v-for="item in orden" :key="item.nombre">
                - {{ item.cantidad }} x {{ item.nombre }}
                <span>${{ (item.precio * item.cantidad).toFixed(2) }}</span>
                <button @click="eliminarProductoOrden(item)">❌</button>
              </p>
            </div>
          </div>
          <input v-model="nombreCliente" type="text" placeholder="Nombre del cliente" />
          <textarea v-model="notaOrden" placeholder="Nota"></textarea>
          <p class="menu-total">Total: <strong>${{ calcularTotal() }}</strong></p>
          <button class="menu-ordenar" @click="enviarOrden">ORDENAR</button>
          <p v-if="mensajeConfirmacion" style="margin-top: 0.5rem; color: green;">{{ mensajeConfirmacion }}</p>
        </aside>
      </template>

      <!-- Vista Órdenes -->
      <template v-if="vista === 'ordenes'">
        <main class="ordenes-historial scrollable">
          <h3>Órdenes previas</h3>
          <ul class="ordenes-lista">
            <li v-for="ord in historialOrdenes" :key="ord.id" class="orden-item">
              <strong>{{ ord.cliente }}</strong><br />
              <span>{{ ord.fecha }} {{ ord.hora }}</span>
              <ul>
                <li v-for="p in ord.productos" :key="p.nombre_producto">
                  {{ p.cantidad }} x {{ p.nombre_producto }} - ${{ (p.cantidad * p.precio_unitario).toFixed(2) }}
                </li>
              </ul>
              <p><strong>Total:</strong> ${{ ord.total }}</p>
              <span :class="['estado', ord.entregado ? 'entregado' : 'no-entregado']">
                {{ ord.entregado ? 'Entregado' : 'En espera' }}
              </span>
              <button
                :disabled="!puedeCancelar(ord.fecha) || ord.entregado"
                :class="['cancelar-btn', { desactivado: !puedeCancelar(ord.fecha) || ord.entregado }]"
                @click="cancelarOrden(ord.id)"
              >
                Cancelar
              </button>
            </li>
          </ul>
        </main>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import logo from '../assets/images/LogoCafe.png'
import '../EstilosCss/menuc.css'

import {
  fetchMenu,
  fetchOrdenesCliente,
  enviarOrden as enviarOrdenAPI,
  cancelarOrdenPorId
} from '../api'

const vista = ref('menu')
const categorias = ref([])
const platillos = ref({})
const categoriaSeleccionada = ref('Todas')
const categoriaExpandida = ref({})
const orden = ref([])

const nombreCliente = ref(localStorage.getItem("usuario_nombre") || '')
const notaOrden = ref('')
const mensajeConfirmacion = ref('')
const historialOrdenes = ref([])
const nombreUsuario = ref(localStorage.getItem("usuario_nombre") || "Invitado")
const rolUsuario = ref(localStorage.getItem("usuario_rol") || 'Cliente')
const usuario_id = parseInt(localStorage.getItem("usuario_id") || '0')
const mostrarDropdown = ref(false)


const toggleCategoria = (cat) => {
  categoriaExpandida.value[cat] = !categoriaExpandida.value[cat]
}

const toggleDarkMode = () => {
  document.body.classList.toggle('dark-mode')
}

const toggleDropdown = () => {
  mostrarDropdown.value = !mostrarDropdown.value
}

const cerrarSesion = () => {
  localStorage.clear()
  window.location.href = '/'  
}

const obtenerMenu = async () => {
  platillos.value = await fetchMenu()
  categorias.value = Object.keys(platillos.value)
  categoriaSeleccionada.value = 'Todas'

  const expanded = {}
  categorias.value.forEach(cat => (expanded[cat] = true))
  categoriaExpandida.value = expanded
}

const agregarProductoOrden = (producto) => {
  const existe = orden.value.find(p => p.nombre === producto.nombre)
  if (existe) {
    existe.cantidad++
  } else {
    orden.value.push({ ...producto, cantidad: 1, precio: parseFloat(producto.precio) })
  }
}

const disminuirProductoOrden = (producto) => {
  const index = orden.value.findIndex(p => p.nombre === producto.nombre)
  if (index !== -1) {
    if (orden.value[index].cantidad > 1) {
      orden.value[index].cantidad--
    } else {
      orden.value.splice(index, 1)
    }
  }
}

const eliminarProductoOrden = (producto) => {
  orden.value = orden.value.filter(p => p.nombre !== producto.nombre)
}

const calcularTotal = () => {
  return orden.value.reduce((acc, prod) => acc + prod.precio * prod.cantidad, 0).toFixed(2)
}

const enviarOrden = async () => {
  if (!nombreCliente.value.trim() || orden.value.length === 0) {
    alert("Por favor ingresa el nombre del cliente y al menos un producto.")
    return
  }

  const payload = {
    cliente: nombreCliente.value,
    nota: notaOrden.value,
    usuario_id,
    productos: orden.value.map(p => ({
      nombre: p.nombre,
      cantidad: p.cantidad,
      precio: p.precio
    }))
  }

  const res = await enviarOrdenAPI(payload)
  if (res.ok) {
    mensajeConfirmacion.value = 'Orden enviada correctamente.'
    orden.value = []
    notaOrden.value = ''
    obtenerOrdenes()
    setTimeout(() => mensajeConfirmacion.value = '', 4000)
  } else {
    alert('Error al enviar la orden.')
  }
}

const cancelarOrden = async (ordenId) => {
  const confirmar = confirm("¿Seguro que quieres cancelar esta orden?")
  if (!confirmar) return

  const res = await cancelarOrdenPorId(ordenId)
  if (!res.ok) {
    alert("Error al cancelar la orden.")
  } else {
    await obtenerOrdenes()
    alert("Orden cancelada correctamente.")
  }
}

const puedeCancelar = (fechaRaw) => {
  const fechaReal = new Date(fechaRaw)
  const ahora = new Date()
  const diferenciaMin = (ahora - fechaReal) / 1000 / 60
  return diferenciaMin <= 2
}

const obtenerOrdenes = async () => {
  if (!usuario_id) return
  const data = await fetchOrdenesCliente(usuario_id)

  historialOrdenes.value = data.map(ord => ({
    ...ord,
    total: ord.productos.reduce((acc, p) => acc + p.precio_unitario * p.cantidad, 0).toFixed(2),
    fechaDate: new Date(ord.fecha)
  }))
}

onMounted(() => {
  const rol = localStorage.getItem('usuario_rol')
  if (rol !== 'cliente') {
    router.push('/login')
    return
  }

  obtenerMenu()
  obtenerOrdenes()
})
</script>
