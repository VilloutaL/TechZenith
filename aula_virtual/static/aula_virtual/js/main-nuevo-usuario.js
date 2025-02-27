// Definir las URLs para las dos consultas
const urlTodosUsuarios = '/obtener-usuarios/';
const urlApoderados = '/obtener-usuarios/?rol=Apoderados';
const urlUsuario = '/obtener_usuario/?username=';

// Elementos claves del DOM
const usernameRegistro = document.getElementById("in-username-registro");
const emailRegistro = document.getElementById('in-email-registro');
const nextBtn = document.getElementById("next-btn");
const backBtn = document.getElementById('back-btn');
const boxBtnRegistro = document.getElementById('box-btns-registro');
const divStep2 = document.getElementById("step-2");
const divStep3 = document.getElementById('step-3');
const checkIsAlumno = document.getElementById('check-is-alumno');
const checkIsProfesor = document.getElementById('check-is-profesor');
const checkIsApoderado = document.getElementById('check-is-apoderado');
const selectTutorAsociado = document.getElementById('select-tutor-asociado');
const formNewUser = document.getElementById('form-new-user');
const sendBtn = document.getElementById('send-btn');

// Función para validar formulario antes de enviar
function validarFormulario() {
    if (checkIsAlumno.checked) {
        if (selectTutorAsociado.value === 'None') {
            alert('Por favor, seleccione un tutor asociado.');
            return false;
        }
    }
    return true;
}

async function actualizarSelectTutorAsociado(tutorUsername) {
    try {
        const apoderados = await obtenerTodosLosApoderados();
        console.log("Apoderados obtenidos:", apoderados);
        
        selectTutorAsociado.innerHTML = '<option value="None">Seleccione</option>'; // Limpiar opciones anteriores
        apoderados.forEach(apoderado => {
            const newOption = document.createElement('option');
            newOption.value = apoderado.username;
            newOption.innerText = apoderado.first_name ? `${apoderado.first_name} ${apoderado.last_name}` : apoderado.username;
            selectTutorAsociado.appendChild(newOption);
        });

        // Establecer el valor del select
        selectTutorAsociado.value = tutorUsername.toString(); // Asegurarse de convertir a cadena si es necesario
        console.log("Valor del select actualizado:", selectTutorAsociado.value);
    } catch (error) {
        console.error('Error al actualizar select de tutor asociado:', error);
    }
}

// Función para obtener todos los usuarios
const obtenerTodosLosUsuarios = async () => {
    try {
        const response = await fetch(urlTodosUsuarios);
        if (!response.ok) {
            throw new Error('Error al obtener todos los usuarios');
        }
        return await response.json();
    } catch (error) {
        console.error('Error en fetchTodosUsuarios:', error);
    }
};

// Función para obtener los apoderados
const obtenerTodosLosApoderados = async () => {
    try {
        const response = await fetch(urlApoderados);
        if (!response.ok) {
            throw new Error('Error al obtener los usuarios con rol Apoderados');
        }
        return await response.json();
    } catch (error) {
        console.error('Error en fetchApoderados:', error);
    }
};

// Función para obtener todos los usuarios
const obtenerUsuario = async (username) => {
    try {
        const urlCompleta = urlUsuario + username
        const response = await fetch(urlCompleta);
        if (!response.ok) {
            throw new Error('Error al obtener el usuario');
        }
        return await response.json();
    } catch (error) {
        console.error('Error en fetchUsuario:', error);
    }
};

// Función para validad el rut.
const validarRut = (rut) => {
    rut = rut.replace(/\./g, '').replace(/-/g, '');
    if (!/^[0-9]+[kK0-9]$/.test(rut)) {
        return false;
    }
    let cuerpo = rut.slice(0, -1);
    let dv = rut.slice(-1).toUpperCase();
    if (cuerpo.length < 7) {
        return false;
    }
    let suma = 0;
    let multiplo = 2;
    for (let i = 1; i <= cuerpo.length; i++) {
        let index = multiplo * rut.charAt(cuerpo.length - i);
        suma += index;

        multiplo = (multiplo < 7) ? multiplo + 1 : 2;
    }
    let dvEsperado = 11 - (suma % 11);
    dvEsperado = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'K' : dvEsperado.toString();
    return dvEsperado === dv;
};

// Función Listener btn step 1
nextBtn.addEventListener('click', async ()=>{
    const usuarios = await obtenerTodosLosUsuarios()
    const rut = usernameRegistro.value;
    
    // Validar el RUT
    if (!validarRut(rut)) {
        alert('El RUT ingresado no es válido. Por favor, verifica y vuelve a intentarlo.');
        return;
    }

    const usuarioExistente = usuarios.find(usuario => usuario.username == rut)
    if (usuarioExistente) {
        console.log("El usuario ya existe, Falta implementar la opcion de modificarlo.")
        const usuario = await obtenerUsuario(rut);
        divStep2.classList = ""
        boxBtnRegistro.classList = ""
        nextBtn.classList = "disable"
        usernameRegistro.readOnly = true;
        emailRegistro.value = usuario.email;
        checkIsApoderado.checked = usuario.is_apoderado;
        checkIsProfesor.checked = usuario.is_profesor;
        if(usuario.is_alumno){
            checkIsAlumno.checked = true;
            divStep3.classList = ""
            await actualizarSelectTutorAsociado(usuario.tutor);
        }
        sendBtn.innerText = "Modificar usuario"


        console.log(usuario)          
    } else {
        divStep2.classList = ""
        boxBtnRegistro.classList = ""
        nextBtn.classList = "disable"
        usernameRegistro.readOnly = true;
        sendBtn.innerText = "Crear usuario"
    }
})

// Función Listener Check btn is alumno
checkIsAlumno.addEventListener('change', async () => {
    if(checkIsAlumno.checked){
        if(checkIsApoderado.checked || checkIsProfesor.checked){
            alert("Un alumno no puede ser Profesor o Apoderado, porfavor verifique los datos.")
            checkIsAlumno.checked = false; 
        } else {
            divStep3.classList = ""
            const apoderados = await obtenerTodosLosApoderados();
            console.log(apoderados)
            apoderados.forEach(apoderado => {
                const newOption = document.createElement('option');
                newOption.value = apoderado.username;
                newOption.innerText = apoderado.first_name ? `${apoderado.first_name} ${apoderado.last_name}` : apoderado.username;
                selectTutorAsociado.appendChild(newOption);
            });
        };
    } else {
        divStep3.classList = "disable"
        selectTutorAsociado.innerHTML = '<option value="None">Seleccione</option>'
    }
})

checkIsApoderado.addEventListener('change', () => {
    if(checkIsApoderado.checked && checkIsAlumno.checked){
        alert("Un alumno no puede ser Profesor o Apoderado, porfavor verifique los datos.")
        checkIsApoderado.checked = false;
    }
})

checkIsProfesor.addEventListener('change', () => {
    if(checkIsProfesor.checked && checkIsAlumno.checked){
        alert("Un alumno no puede ser Profesor o Apoderado, porfavor verifique los datos.")
        checkIsProfesor.checked = false;
    }
})

backBtn.addEventListener('click', () => {
    usernameRegistro.value = "";
    usernameRegistro.readOnly = false;
    nextBtn.classList = "";
    divStep2.classList = "disable";
    divStep3.classList = "disable";
    boxBtnRegistro.classList = "disable"
    emailRegistro.value = ""
    checkIsAlumno.checked = false
    checkIsApoderado.checked = false
    checkIsProfesor.checked = false
})

// Listener para el envío del formulario
formNewUser.addEventListener('submit', function(event) {
    if (!validarFormulario()) {
        event.preventDefault();
    }
});