// Definir las URLs para las dos consultas
const urlTodosUsuarios = '/obtener-usuarios/';
const urlApoderados = '/obtener-usuarios/?rol=Apoderados';

// Elementos claves del DOM
const usernameRegistro = document.getElementById("in-username-registro");
const nextBtnPt1 = document.getElementById("next-btn-pt1");
const nextBtnPt2 = document.getElementById("next-btn-pt2");
const divStep2 = document.getElementById("step-2");
const divStep3 = document.getElementById('step-3');
const checkIsAlumno = document.getElementById('check-is-alumno');
const checkIsProfesor = document.getElementById('check-is-profesor');
const checkIsApoderado = document.getElementById('check-is-apoderado');
const selectTutorAsociado = document.getElementById('select-tutor-asociado');

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
nextBtnPt1.addEventListener('click', async ()=>{
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
    } else {
        divStep2.classList = ""
        nextBtnPt1.classList = "disable"
    }
})

// Función Listener Check btn is alumno
checkIsAlumno.addEventListener('change', async () => {
    if(checkIsAlumno.checked){
        if(checkIsApoderado.checked || checkIsProfesor.checked){
            alert("Un alumno no puede ser Profesor o Apoderado, porfavor verifique los datos.") 
        }

        divStep3.classList = ""
        nextBtnPt2.classList = "disable"
        const apoderados = await obtenerTodosLosApoderados();
        console.log(apoderados)
        apoderados.forEach(apoderado => {
            const newOption = document.createElement('option');
            newOption.value = apoderado.username;
            newOption.innerText = apoderado.first_name ? `${apoderado.first_name} ${apoderado.last_name}` : apoderado.username;
            selectTutorAsociado.appendChild(newOption);
        });
    } else {
        divStep3.classList = "disable"
        nextBtnPt2.classList = ""
        selectTutorAsociado.innerHTML = '<option value="Seleccione">Seleccione</option>'
    }
})


