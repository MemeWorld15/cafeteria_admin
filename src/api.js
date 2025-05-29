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
