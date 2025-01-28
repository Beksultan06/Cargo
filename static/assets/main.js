document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input, select').forEach((field) => {
        field.addEventListener('blur', () => {
            if (field.value.trim() !== '') {
                field.classList.add('filled');
            } else {
                field.classList.remove('filled');
            }
        });

        field.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault(); 

                let nextField = field.nextElementSibling;

                while (nextField && !(nextField.tagName === 'INPUT' || nextField.tagName === 'SELECT')) {
                    nextField = nextField.nextElementSibling;
                }

                if (nextField) {
                    nextField.focus();
                }
            }
        });
    });

    document.querySelectorAll('.toggle-password').forEach((toggle) => {
        toggle.addEventListener('click', () => {
            const input = toggle.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
            } else {
                input.type = 'password';
            }
        });
    });

    const registerButton = document.getElementById('registerButton');
    if (registerButton) {
        registerButton.addEventListener('click', function (event) {
            event.preventDefault(); 

            const fullName = document.getElementById('fullName').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const pvz = document.getElementById('pvz').value.trim();
            const address = document.getElementById('address').value.trim();
            const password = document.getElementById('password').value.trim();
            const confirmPassword = document.getElementById('confirmPassword').value.trim();

            if (!fullName || !phone || !pvz || !address || !password || !confirmPassword) {
                document.getElementById('modal').style.display = 'flex'; 
            } else {
                window.location.href = './succes.html';
            }
        });
    }

    const closeButton = document.getElementById('closeButton');
    if (closeButton) {
        closeButton.addEventListener('click', function () {
            document.getElementById('modal').style.display = 'none';
        });
    }

    const finishButton = document.getElementById('finishButton');
    if (finishButton) {
        finishButton.addEventListener('click', function () {
            window.location.href = './Cargopart.html';
        });
    } else {
        console.error('Button with ID "finishButton" not found');
    }
});


const menuButton = document.getElementById('menuButton');
const sidebar = document.getElementById('sidebar');

menuButton.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach((button) => {
    button.addEventListener('click', () => {
        tabButtons.forEach((btn) => btn.classList.remove('active'));
        tabContents.forEach((tab) => tab.classList.remove('active'));

        button.classList.add('active');
        document.getElementById(button.dataset.tab).classList.add('active');
    });
});



