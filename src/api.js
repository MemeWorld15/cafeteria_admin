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

// ÓRDENES
export const fetchOrdenes = () => fetch(`${BASE_URL}/ordenes`).then(res => res.json())

// EMPLEADOS
export const crearEmpleado = (formData) =>
  fetch(`${BASE_URL}/empleados`, { method: 'POST', body: formData })
