// Contain code execution for for activation_request page.



const form = document.querySelector('#main-form');
const email = document.querySelector('#email');
const emailError = document.querySelector('#email + .validation-error');
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
    const isEmailValid = valEmail(email, emailError);

    // If every input pass client validation data is sended to server in ajax manner.
    if (isEmailValid)
    {
        submit(form, submitBtn);
    }
    else
    {
        setButtonStyle(submitBtn, 'btn-danger', 1000);
    }
});