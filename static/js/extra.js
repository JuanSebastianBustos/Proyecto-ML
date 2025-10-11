document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const predictBtn = document.getElementById('predictBtn');
    
    // Custom form validation
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Reset previous validation states
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
        });
        
        let isValid = true;
        
        // Validate horas_practica
        const horasPractica = document.getElementById('horas_practica');
        if (!horasPractica.value || horasPractica.value < 0 || horasPractica.value > 168) {
            horasPractica.classList.add('is-invalid');
            isValid = false;
        }
        
        // Validate experiencia_previa
        const experienciaPrevia = document.querySelector('input[name="experiencia_previa"]:checked');
        if (!experienciaPrevia) {
            document.querySelectorAll('input[name="experiencia_previa"]').forEach(input => {
                input.classList.add('is-invalid');
            });
            isValid = false;
        }
        
        // Validate nota_media
        const notaMedia = document.getElementById('nota_media');
        if (!notaMedia.value || notaMedia.value < 0 || notaMedia.value > 5) {
            notaMedia.classList.add('is-invalid');
            isValid = false;
        }
        
        // Validate asistencia
        const asistencia = document.getElementById('asistencia');
        if (!asistencia.value || asistencia.value < 0 || asistencia.value > 100) {
            asistencia.classList.add('is-invalid');
            isValid = false;
        }
        
        if (isValid) {
            setLoadingState('predictBtn', true);
            form.submit();
        } else {
            showToast('Por favor, complete todos los campos correctamente', 'danger');
        }
    });
    
    // Real-time validation feedback
    const numericInputs = ['horas_practica', 'nota_media', 'asistencia'];
    numericInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            if (this.value && this.checkValidity()) {
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
            }
        });
    });
    
    // Radio button validation
    document.querySelectorAll('input[name="experiencia_previa"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.querySelectorAll('input[name="experiencia_previa"]').forEach(r => {
                r.classList.remove('is-invalid');
            });
        });
    });
});