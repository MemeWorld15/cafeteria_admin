// src/api.js
import { BASE_URL } from './config';

// --------- LOGIN ---------
export const login = (correo, contrasena) => {
  const formData = new FormData();
  formData.append('correo', correo);
  formData.append('contrasena', contrasena);

  return fetch(`${BASE_URL}/login`, {
    method: 'POST',
    body: formData,
    mode: 'cors' // para render
  });
};
// ---------------------- REGISTRO ----------------------
export const registrarUsuario = (formData) =>
  fetch(`${BASE_URL}/registro`, {
    method: 'POST',
    body: formData,
    mode: 'cors'
  });

// CATEGORÍAS
export const fetchCategorias = () => fetch(`${BASE_URL}/categorias`).then(res => res.json())
export const crearNuevaCategoria = (nombre) => {
  const formData = new FormData()
  formData.append('nombre', nombre)
  return fetch(`${BASE_URL}/categorias`, { method: 'POST', body: formData })
}
export const actualizarCategoria = (id, nombre) => {
  const formData = new FormData()
  formData.append('nombre', nombre)
  return fetch(`${BASE_URL}/categorias/${id}`, { method: 'PUT', body: formData })
}
export const eliminarCategoriaPorId = (id) =>
  fetch(`${BASE_URL}/categorias/${id}`, { method: 'DELETE' })

// PRODUCTOS
export const fetchProductos = () => fetch(`${BASE_URL}/productos`).then(res => res.json())
export const crearProducto = (formData) =>
  fetch(`${BASE_URL}/productos`, {
    method: 'POST',
    body: formData,
    mode: 'cors'
  });

export const actualizarProducto = (id, formData) =>
  fetch(`${BASE_URL}/productos/${id}`, { method: 'PUT', body: formData })
export const eliminarProductoPorId = (id) =>
  fetch(`${BASE_URL}/productos/${id}`, { method: 'DELETE' })

export const toggleDisponibilidadProducto = (id) =>
  fetch(`${BASE_URL}/productos/${id}/toggle-disponible`, {
    method: 'PUT',
    mode: 'cors'
  });
// ÓRDENES
export const fetchOrdenes = () =>
  fetch(`${BASE_URL}/ordenes`).then(res => res.json());

export const marcarOrdenComoEntregada = (id) =>
  fetch(`${BASE_URL}/ordenes/${id}/entregado`, {
    method: 'PUT',
    mode: 'cors'
  })


// EMPLEADOS
export const crearEmpleado = (formData) =>
  fetch(`${BASE_URL}/empleados`, { method: 'POST', body: formData })

export const fetchEmpleados = () =>
  fetch(`${BASE_URL}/empleados`).then(res => res.json())

export const eliminarEmpleadoPorId = (id) =>
  fetch(`${BASE_URL}/empleados/${id}`, { method: 'DELETE' })

// --------- MENÚ ---------
export const fetchMenu = () =>
  fetch(`${BASE_URL}/menu`, { method: 'GET', mode: 'cors' }).then(res => res.json())

// --------- ÓRDENES DEL CLIENTE ---------
export const fetchOrdenesCliente = (usuario_id) =>
  fetch(`${BASE_URL}/ordenes/cliente/${usuario_id}`, { method: 'GET', mode: 'cors' }).then(res => res.json())

export const enviarOrden = (payload) =>
  fetch(`${BASE_URL}/ordenar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    mode: 'cors'
  })

export const cancelarOrdenPorId = (id) =>
  fetch(`${BASE_URL}/ordenes/${id}`, {
    method: 'DELETE',
    mode: 'cors'
  })
// INVENTARIO
export const fetchInventario = () =>
  fetch(`${BASE_URL}/inventario`).then(res => res.json());

export const agregarInsumo = (formData) =>
  fetch(`${BASE_URL}/inventario`, {
    method: 'POST',
    body: formData,
    mode: 'cors'
  });

export const actualizarCantidadInsumo = (id, formData) =>
  fetch(`${BASE_URL}/inventario/${id}`, {
    method: 'PUT',
    body: formData
  });

export const editarNombreUnidadInsumo = (id, formData) =>
  fetch(`${BASE_URL}/inventario/${id}/editar`, {
    method: 'PUT',
    body: formData
  });

export const eliminarInsumoPorId = (id) =>
  fetch(`${BASE_URL}/inventario/${id}`, { method: 'DELETE' });

export const consumirInsumo = (id, formData) =>
  fetch(`${BASE_URL}/inventario/${id}/consumir`, {
    method: 'POST',
    body: formData
  });

//  NUEVA función para reabastecer insumo
export const reabastecerInsumo = (id, formData) =>
  fetch(`${BASE_URL}/inventario/${id}/reabastecer`, {
    method: 'POST',
    body: formData
  });



export const descargarInventarioPDF = () =>
  window.open(`${BASE_URL}/inventario/pdf`, "_blank");
// -------------------------------- ARQUEO DEL DÍA -------------------------------
export const fetchArqueoDelDia = () =>
  fetch(`${BASE_URL}/arqueo/dia`, { method: 'GET', mode: 'cors' }).then(res => res.json());

