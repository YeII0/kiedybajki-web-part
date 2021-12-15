// Contain code execution for registration page.



const form = document.querySelector('#main-form');
const username = document.querySelector('#username');
const usernameError = document.querySelector('#username + .validation-error');
const email = document.querySelector('#email');
const emailError = document.querySelector('#email + .validation-error');
const passw = document.querySelector('#password');
const passwError = document.querySelector('#password + .validation-error')
const passwTip = document.querySelector('#password ~ small');
const passwConfirm = document.querySelector('#confirm_password');
const passwConfirmError = document.querySelector('#confirm_password + .validation-error');
const submitBtn = document.querySelector('input[type="submit"]');


/*
Custom submit behaviour.
Before sending forms we doing client-side form validation.
If everthing is okey form is send and response is handled in ajax manner.
UI is updated accordingly to response sended in json format.
*/
form.addEventListener('submit', e =>
{
    e.preventDefault();

    // Client-side validation.
    const isUsernameValid = valUsername(username, usernameError);
    const isEmailValid = valEmail(email, emailError);
    const isPasswValid = valNewPassw(passw, passwError, passwTip);
    const isConfirmPasswValid = valConfirmPassw(passwConfirm, passwConfirmError)

    if (!isPasswValid || !isConfirmPasswValid)
    {
        passw.value = '';
        passwConfirm.value = '';
    }

    // If every input pass client validation data is sended to server in ajax manner.
    if (
        isUsernameValid &&
        isEmailValid &&
        isPasswValid &&
        isConfirmPasswValid
    )
    {
        submit(form, submitBtn);
    }
    else
    {
        setButtonStyle(submitBtn, 'btn-danger', 1000);
    }  
});