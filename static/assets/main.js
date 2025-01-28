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
                window.location.href = './success.html';
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

document.addEventListener('DOMContentLoaded', () => {
    const registerButton = document.getElementById('registerButton');
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
            window.location.href = './success.html';
        }
    });

    window.closeModal = function () {
        document.getElementById('modal').style.display = 'none';
    };
});
const passwordField = document.getElementById('password');
const togglePasswordButton = document.getElementById('togglePassword');
const eyeIcon = document.getElementById('eyeIcon');

togglePasswordButton.addEventListener('click', () => {
    const isPasswordVisible = passwordField.type === 'text';
    passwordField.type = isPasswordVisible ? 'password' : 'text';

    eyeIcon.innerHTML = isPasswordVisible ?
        `<path fill-rule="evenodd" clip-rule="evenodd" d="M17.6744 14.763L20.4294 17.518L19.5804 18.366L2.85442 1.64001L3.70143 0.790009L6.55643 3.64501C7.93643 3.09301 9.43643 2.79001 11.0044 2.79001C15.8124 2.79001 19.9764 5.63801 22.0044 9.79001C21.0261 11.8013 19.532 13.5173 17.6744 14.763ZM7.49043 4.58001L9.15442 6.24401C9.90936 5.84934 10.7706 5.70599 11.6127 5.83485C12.4547 5.9637 13.2337 6.35803 13.836 6.96039C14.4384 7.56276 14.8327 8.34171 14.9616 9.18378C15.0904 10.0259 14.9471 10.8871 14.5524 11.642L16.8074 13.897C18.3814 12.897 19.7114 11.494 20.6524 9.79101C18.6904 6.24001 15.0384 3.99001 11.0044 3.99001C9.8085 3.99076 8.62101 4.19014 7.49043 4.58001ZM13.6424 10.732C13.8209 10.2327 13.8539 9.69301 13.7376 9.17569C13.6213 8.65837 13.3606 8.1847 12.9857 7.80978C12.6107 7.43485 12.1371 7.17409 11.6197 7.05782C11.1024 6.94155 10.5627 6.97456 10.0634 7.15301L13.6424 10.732ZM15.4524 15.936C14.0724 16.488 12.5724 16.791 11.0044 16.791C6.19642 16.791 2.03243 13.943 0.00442505 9.79101C0.982746 7.7797 2.47684 6.06374 4.33442 4.81801L5.20143 5.68501C3.59592 6.70941 2.27373 8.12101 1.35643 9.79001C3.31843 13.34 6.97043 15.59 11.0044 15.59C12.2003 15.5893 13.3878 15.3899 14.5184 15L15.4524 15.936ZM7.45743 7.94001L8.36643 8.85001C8.18798 9.3493 8.15497 9.889 8.27124 10.4063C8.3875 10.9236 8.64827 11.3973 9.02319 11.7722C9.39812 12.1472 9.87179 12.4079 10.3891 12.5242C10.9064 12.6405 11.4461 12.6075 11.9454 12.429L12.8554 13.337C12.1005 13.7317 11.2393 13.875 10.3972 13.7462C9.55512 13.6173 8.77618 13.223 8.17381 12.6206C7.57144 12.0183 7.17712 11.2393 7.04826 10.3972C6.91941 9.55516 7.06275 8.69494 7.45743 7.94001Z" fill="white"/>` :
        `<path fill-rule="evenodd" clip-rule="evenodd" d="M11.0044 13.59C15.0384 13.59 18.6904 11.34 20.6524 7.79001C18.6904 4.24001 15.0384 1.99001 11.0044 1.99001C6.97043 1.99001 3.31843 4.24001 1.35643 7.79001C3.31843 11.34 6.97043 13.59 11.0044 13.59ZM11.0044 0.790009C15.8124 0.790009 19.9764 3.63801 22.0044 7.79001C19.9764 11.942 15.8124 14.79 11.0044 14.79C6.19642 14.79 2.03243 11.942 0.00442505 7.79001C2.03243 3.63801 6.19642 0.790009 11.0044 0.790009ZM11.0044 10.59C11.747 10.59 12.4592 10.295 12.9843 9.76991C13.5094 9.24481 13.8044 8.53261 13.8044 7.79001C13.8044 7.0474 13.5094 6.33521 12.9843 5.81011C12.4592 5.28501 11.747 4.99001 11.0044 4.99001C10.2618 4.99001 9.54963 5.28501 9.02453 5.81011C8.49942 6.33521 8.20442 7.0474 8.20442 7.79001C8.20442 8.53261 8.49942 9.24481 9.02453 9.76991C9.54963 10.295 10.2618 10.59 11.0044 10.59ZM11.0044 11.79C9.94356 11.79 8.92614 11.3686 8.176 10.6184C7.42585 9.86829 7.00443 8.85087 7.00443 7.79001C7.00443 6.72914 7.42585 5.71173 8.176 4.96158C8.92614 4.21144 9.94356 3.79001 11.0044 3.79001C12.0653 3.79001 13.0827 4.21144 13.8329 4.96158C14.583 5.71173 15.0044 6.72914 15.0044 7.79001C15.0044 8.85087 14.583 9.86829 13.8329 10.6184C13.0827 11.3686 12.0653 11.79 11.0044 11.79Z"/>`;
});

const confirmPasswordField = document.getElementById('confirmPassword');
const toggleConfirmPasswordButton = document.getElementById('toggleConfirmPassword');
const confirmEyeIcon = document.getElementById('confirmEyeIcon');

toggleConfirmPasswordButton.addEventListener('click', () => {
    const isConfirmPasswordVisible = confirmPasswordField.type === 'text';
    confirmPasswordField.type = isConfirmPasswordVisible ? 'password' : 'text';

    confirmEyeIcon.innerHTML = isConfirmPasswordVisible ?
        `<path fill-rule="evenodd" clip-rule="evenodd" d="M17.6744 14.763L20.4294 17.518L19.5804 18.366L2.85442 1.64001L3.70143 0.790009L6.55643 3.64501C7.93643 3.09301 9.43643 2.79001 11.0044 2.79001C15.8124 2.79001 19.9764 5.63801 22.0044 9.79001C21.0261 11.8013 19.532 13.5173 17.6744 14.763ZM7.49043 4.58001L9.15442 6.24401C9.90936 5.84934 10.7706 5.70599 11.6127 5.83485C12.4547 5.9637 13.2337 6.35803 13.836 6.96039C14.4384 7.56276 14.8327 8.34171 14.9616 9.18378C15.0904 10.0259 14.9471 10.8871 14.5524 11.642L16.8074 13.897C18.3814 12.897 19.7114 11.494 20.6524 9.79101C18.6904 6.24001 15.0384 3.99001 11.0044 3.99001C9.8085 3.99076 8.62101 4.19014 7.49043 4.58001ZM13.6424 10.732C13.8209 10.2327 13.8539 9.69301 13.7376 9.17569C13.6213 8.65837 13.3606 8.1847 12.9857 7.80978C12.6107 7.43485 12.1371 7.17409 11.6197 7.05782C11.1024 6.94155 10.5627 6.97456 10.0634 7.15301L13.6424 10.732ZM15.4524 15.936C14.0724 16.488 12.5724 16.791 11.0044 16.791C6.19642 16.791 2.03243 13.943 0.00442505 9.79101C0.982746 7.7797 2.47684 6.06374 4.33442 4.81801L5.20143 5.68501C3.59592 6.70941 2.27373 8.12101 1.35643 9.79001C3.31843 13.34 6.97043 15.59 11.0044 15.59C12.2003 15.5893 13.3878 15.3899 14.5184 15L15.4524 15.936ZM7.45743 7.94001L8.36643 8.85001C8.18798 9.3493 8.15497 9.889 8.27124 10.4063C8.3875 10.9236 8.64827 11.3973 9.02319 11.7722C9.39812 12.1472 9.87179 12.4079 10.3891 12.5242C10.9064 12.6405 11.4461 12.6075 11.9454 12.429L12.8554 13.337C12.1005 13.7317 11.2393 13.875 10.3972 13.7462C9.55512 13.6173 8.77618 13.223 8.17381 12.6206C7.57144 12.0183 7.17712 11.2393 7.04826 10.3972C6.91941 9.55516 7.06275 8.69494 7.45743 7.94001Z" fill="white"/>` :
        `<path fill-rule="evenodd" clip-rule="evenodd" d="M11.0044 13.59C15.0384 13.59 18.6904 11.34 20.6524 7.79001C18.6904 4.24001 15.0384 1.99001 11.0044 1.99001C6.97043 1.99001 3.31843 4.24001 1.35643 7.79001C3.31843 11.34 6.97043 13.59 11.0044 13.59ZM11.0044 0.790009C15.8124 0.790009 19.9764 3.63801 22.0044 7.79001C19.9764 11.942 15.8124 14.79 11.0044 14.79C6.19642 14.79 2.03243 11.942 0.00442505 7.79001C2.03243 3.63801 6.19642 0.790009 11.0044 0.790009ZM11.0044 10.59C11.747 10.59 12.4592 10.295 12.9843 9.76991C13.5094 9.24481 13.8044 8.53261 13.8044 7.79001C13.8044 7.0474 13.5094 6.33521 12.9843 5.81011C12.4592 5.28501 11.747 4.99001 11.0044 4.99001C10.2618 4.99001 9.54963 5.28501 9.02453 5.81011C8.49942 6.33521 8.20442 7.0474 8.20442 7.79001C8.20442 8.53261 8.49942 9.24481 9.02453 9.76991C9.54963 10.295 10.2618 10.59 11.0044 10.59ZM11.0044 11.79C9.94356 11.79 8.92614 11.3686 8.176 10.6184C7.42585 9.86829 7.00443 8.85087 7.00443 7.79001C7.00443 6.72914 7.42585 5.71173 8.176 4.96158C8.92614 4.21144 9.94356 3.79001 11.0044 3.79001C12.0653 3.79001 13.0827 4.21144 13.8329 4.96158C14.583 5.71173 15.0044 6.72914 15.0044 7.79001C15.0044 8.85087 14.583 9.86829 13.8329 10.6184C13.0827 11.3686 12.0653 11.79 11.0044 11.79Z"/>`;
});