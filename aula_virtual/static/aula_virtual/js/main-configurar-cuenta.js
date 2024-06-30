function validarContraseña(contraseña) {
    // Requiere al menos 10 caracteres, una letra minúscula, una letra mayúscula y un número
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{10,}$/;
    return regex.test(contraseña);
}

const form = document.getElementById('conf-cuenta');

form.addEventListener('submit', function(event) {
    // Validación de campos obligatorios
    const nombre = document.getElementById('in-first-name').value
    const apellido = document.getElementById('in-last-name').value
    const contraseña1 = document.getElementById('in-password').value
    const contraseña2 = document.getElementById('in-password-val').value

    if (nombre === '' || apellido === '') {
        alert('Por favor completa todos los campos obligatorios.');
        event.preventDefault(); // Evita que se envíe el formulario si hay campos obligatorios vacíos
        return;
    }

    if (!validarContraseña(contraseña1)) {
        alert('La contraseña debe tener al menos 10 caracteres, una letra minúscula, una letra mayúscula y un número.');
        event.preventDefault(); // Evita que se envíe el formulario si la contraseña no cumple con los requisitos
        return;
    }

    // Verifica que las contraseñas coincidan
    if (contraseña1 !== contraseña2) {
        alert('Las contraseñas no coinciden.');
        event.preventDefault(); // Evita que se envíe el formulario si las contraseñas no coinciden
        return;
    }

    // Si todo está correcto, el formulario se enviará normalmente
});