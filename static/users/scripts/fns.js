// Contains form validation functions

/* Specific validators
========================================================================== */

// Return true when valid and false when invalid.
function valUsername(input, inputError)
{
    if (input.validity.valueMissing)
    {
        inputError.textContent = requiredMsg;
        input.classList.add('invalid-input');
    }
    else if (input.validity.tooShort || input.validity.tooLong)
    {
        inputError.textContent = 'Pole musi zawierać od 2 do 20 znaków.';
        input.classList.add('invalid-input');
    }
    else
    {
        inputError.textContent = '\u200B';
        input.classList.remove('invalid-input');
        return true;
    }
    return false;
}


// Return true when valid and false when invalid.
function valEmail(input, inputError)
{
    if (input.validity.valueMissing)
    {
        inputError.textContent = requiredMsg;
        input.classList.add('invalid-input');
    }
    else if (input.validity.typeMismatch)
    {
        inputError.textContent = 'Nieprawidłowy adres e-mail.';
        input.classList.add('invalid-input');
    }
    else
    {
        inputError.textContent = '\u200B';
        input.classList.remove('invalid-input');
        return true;
    }
    return false;
}


/* 
Return true when valid and false when invalid.
Use in registration and in setting new password form.
*/
function valNewPassw(input, inputError, inputTip)
{
    inputError.textContent = '\u200B';
    inputTip.classList.remove('validation-error');
    if (input.validity.valueMissing)
    {
        inputError.textContent = requiredMsg + '\u00A0';
        input.classList.add('invalid-input');
    }
    else if (input.validity.tooShort)
    {
        input.classList.add('invalid-input');
        inputTip.classList.add('validation-error');
    }
    else
    {
        input.classList.remove('invalid-input');
        return true;
    }    
    return false;
}


// Return true when valid and false when invalid.
function valConfirmPassw(input, inputError)
{
    if (input.validity.valueMissing)
    {
        inputError.textContent = requiredMsg;
        input.classList.add('invalid-input');
    }
    else if (input.value !== passw.value)
    {
        inputError.textContent = 'Hasła się nie zgadzają.';
        input.classList.add('invalid-input');
    }
    else
    {
        inputError.textContent = '\u200B';
        input.classList.remove('invalid-input');
        return true;
    }
    return false 
}

/*
Validator specific for webhook in account page.
When is invalid it additionally move inputError before inputTip.
Otherwise it moves inputError after inputTip.
This prevents blank space between inputTip and input when there is no error to show.
And when there is a error to show inputTip will shown before inputTip.
It will just looks better.
*/
function valWebhook(input, inputError, inputTip, extra_webhook)
{
    if (!input.validity.valid)
    {
        input.classList.add('invalid-input');
        if (input.validity.valueMissing)
        {
            inputError.textContent = requiredMsg;
        }
        else if (input.validity.typeMismatch)
        {
            inputError.textContent = 'Nieprawidłowy URL.';
        }
        inputTip.insertAdjacentElement('beforebegin', inputError);
    }
    else if (input.value == extra_webhook.value)
    {
        input.classList.add('invalid-input');
        inputError.textContent = 'Główny i dodatkowy webhook nie mogą być takie same.';
        inputTip.insertAdjacentElement('beforebegin', inputError);
    }    
    else
    {
        inputTip.insertAdjacentElement('afterend', inputError);
        inputError.textContent = '\u200B';
        input.classList.remove('invalid-input');
        return true;
    }
    return false;    
}