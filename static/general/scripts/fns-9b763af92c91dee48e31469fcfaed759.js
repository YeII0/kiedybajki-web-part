// Contain universal functions that fit to more than one blueprint.

const floatAlert = document.querySelector('.float-alert');
const main = document.querySelector('main');
let alertTimeout;
let alertTransTimeout;
btnTransTimeouts = {};


/* Submit related functions
========================================================================== */

/*
Send data to server.
If sended form pass validation on server side and no other error occur
user is redirected to login page.
Otherwise page will be updated in ajax manner to show errors sended in response.
If form is in table pass true in third optional parameter.
In fourth optional parameter you can specify dictionary of additional json objects to send to server
in a format {key1: jsonObject1, key2: jsonObject2}
*/
async function submit(form, submitBtn, isTableForm, extraJsons)
{
    submitBtn.classList.add('btn-loading');
    let response;
    let isSuccessSubmit;
    let formData = new FormData(form);

    if (extraJsons)
    {
        for (key in extraJsons)
        {
            formData.append(key, JSON.stringify(extraJsons[key]));
        }
    }

    try
    {
        response = await fetch(form.action,
        {
            method: 'POST',
            body: formData
        });
    }
    catch
    {
        submitBtn.classList.remove('btn-loading');
        setButtonStyle(submitBtn, 'btn-danger', 1000);
        showFloatAlert('Nie udało połączyć się z serwerem. Spróbuj później.', 'error', true);
        isSuccessSubmit = false;
        return isSuccessSubmit;
    }

    if (!response.ok)
    {
        showFloatAlert('Błąd serwera. Spróbuj ponownie.', 'error', true);
        submitBtn.classList.remove('btn-loading');
        setButtonStyle(submitBtn, 'btn-danger', 1000);
        isSuccessSubmit = false;
        return isSuccessSubmit;
    }

    const responseData = await response.json();

    /*
    isSuccess indicate if form pass validation on server side.
    If yes we redirect user if there is redirection url.
    If not we update UI to show feedback from server on current page.
    */
    if (responseData.isSuccess)
    {
        isSuccessSubmit = true;
        if (responseData.redirectUrl)
        {
            window.location.replace(responseData.redirectUrl);
            return;
        }
        submitBtn.classList.remove('btn-loading');
        setButtonStyle(submitBtn, 'btn-success', 500);
    }
    else
    {
        isSuccessSubmit = false;
        submitBtn.classList.remove('btn-loading');
        setButtonStyle(submitBtn, 'btn-danger', 1000);

        /*
        errors store only server side form validation errors, it's possible that
        some other errors will be passed in alert property with error type.
        */
        if (responseData.errors)
        {

            if (isTableForm)
            {
                const row = submitBtn.closest('tr');
                showServerFormErrors(responseData.errors, row);
            }
            else
            {
                showServerFormErrors(responseData.errors);
            }
        }        
    }
    if (responseData.alert)
    {
        showFloatAlert(responseData.alert.msg, responseData.alert.type, true);
    }
    return isSuccessSubmit;
}


/*
Update UI to show on page server-side form errors.
errors store dictionary of server-side form validation errors.
Key is a id of html input in which error occur and value 
is a array of errors for given input.
*/
function showServerFormErrors(errors, row)
{
    // Loop through input id's with related errors
    for (input_id in errors)
    {
        let input;
        let inputError;
        // Assign inputs and input errors elements for no table forms
        if (!row)
        {
            input = document.querySelector(`#${input_id}`);
            inputError = document.querySelector(`#${input_id} + .validation-error`);

            /* 
            When there is a tip in small element between input and inputError
            selector above will not work. Selector below will work.
            */
            if (!inputError)
            {
                inputError = document.querySelector(`#${input_id} ~ .validation-error`);
            }

            /*
            Select input is placed in wrapper. 
            So there is a need to create another selector for this case.
            */
            else if (!inputError)
            {
                const selectWrapper = document.querySelector(`#${input_id}`).parentElement;
                const pairWrapper = selectWrapper.parentElement;
                inputError = pairWrapper.querySelector(`${selectWrapper.tagName} ~ .validation-error`)
            }
        }
        // Assign inputs and inputs errors elements for table forms
        else
        {
            input = row.querySelector(`[name="${input_id}"]`);
            inputError = row.querySelector(`[name="${input_id}"] + .validation-error`);

            /* 
            When there is a tip in small element between input and inputError
            selector above will not work. Selector below will work.
            */
            if (!inputError)
            {
                inputError = row.querySelector(`[name="${input_id}"] ~ .validation-error`);
            }

            /*
            Select input is placed in wrapper. 
            So there is a need to create another selector for this case.
            */
            else if (!inputError)
            {
                const selectWrapper = row.querySelector(`[name="${input_id}"]`).parentElement;
                const pairWrapper = selectWrapper.parentElement;
                inputError = pairWrapper.querySelector(`${selectWrapper.tagName} ~ .validation-error`)
            }            


            inputError.classList.remove('display-none');
        }


        input.classList.add('invalid-input');

        // Loop through input errors
        inputError.textContent = '';
        for (error of errors[input_id])
        {
            inputError.textContent += error + ' ';
        }
    }
}


/*
If input error don't have empty character which means that error is displayed
then inputError is moved before inputTip. Used after showServerFormErrors function for inputs in which this
behavior is needed. Cuz we want for example show in webhook input on account page error before tip.
In default tip is first cuz we don't want empty space between input and tip when errorInput is empty.
*/
function moveErrorBeforeTip(inputError, inputTip)
{
    if (inputError.textContent !== '\u200b')
    {
        inputTip.insertAdjacentElement('beforebegin', inputError);
    }
}


/* Validators
========================================================================== */

let requiredMsg = 'To pole jest wymagane.';


function toggleErrorDisplay(inputError, isValid)
{
    if (isValid)
    {
        inputError.classList.add('display-none');
    }
    else
    {
        inputError.classList.remove('display-none');
    }
}


/* 
Return true when valid and false when invalid.
Generic validator for checking only if input is not empty.
*/
function valValueMissing(input, inputError, isToggleErrorDisplay)
{
    let isValid = false;
    if (input.validity.valueMissing)
    {
        inputError.textContent = requiredMsg;
        input.classList.add('invalid-input');
    }
    else
    {
        input.classList.remove('invalid-input');
        inputError.textContent = '\u200B';
        isValid = true;
    }

    if (isToggleErrorDisplay)
    {
        toggleErrorDisplay(inputError, isValid);
    }

    return isValid;
}

function valExtraWebhook(input, inputError, main_webhook_input, isToggleErrorDisplay)
{
    let isValid = false;

    if (input.value && input.validity.typeMismatch)
    {
        input.classList.add('invalid-input');
        inputError.textContent = 'Nieprawidłowy URL.';
    }
    else if (input.value && input.value == main_webhook_input.value)
    {
        input.classList.add('invalid-input');
        inputError.textContent = 'Główny i dodatkowy webhook nie mogą być takie same.';
    }
    else
    {
        inputError.textContent = '\u200B';
        input.classList.remove('invalid-input');
        isValid = true;
    }

    if (isToggleErrorDisplay)
    {
        toggleErrorDisplay(inputError, isValid);
    }

    return isValid;
}


// Return true when valid and false when invalid.
function valUrl(input, inputError, isToggleErrorDisplay)
{
    let isValid = false;
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
    }
    else
    {
        inputError.textContent = '\u200B';
        input.classList.remove('invalid-input');
        isValid = true;
    }
    
    if (isToggleErrorDisplay)
    {
        toggleErrorDisplay(inputError, isValid);
    }

    return isValid;      
}


/* Float alert function
========================================================================== */

/*
Create click event listener attached to float-alert.
It hides alert after clicking on alert area.
*/
function hideAlertAfterClick()
{
    floatAlert.addEventListener('click', () => 
    {
        clearTimeout(alertTimeout);
        clearTimeout(alertTransTimeout);
        hideAlertAnimation();
    });
}


/*
Create submit event delegation to main element.
If any form in main element will be submitted it will
clear timeouts related to float alert and then hide float alert.
*/
function hideAlertWhenSubmit()
{
    main.addEventListener('submit', e =>
    {
        if (e.target.matches('form'))
        {
            clearTimeout(alertTimeout);
            clearTimeout(alertTransTimeout);
            floatAlert.setAttribute('class', 'float-alert invisible');        
        }
    });
}


/*
Shows float alert with specified msg styled accordingly to given type.
If third param isDuration is specified message will hide after time
that will depend on message length.
Without passing third param alert will be just showed.
*/
function showFloatAlert(msg, type, isDuration)
{
    /*
    Clear previous setTimeout function related to hiding alert
    cuz we don't want them to overlap with new one.
    */
    clearTimeout(alertTimeout);
    clearTimeout(alertTransTimeout);

    floatAlert.setAttribute('class', `float-alert alert-${type} show-alert`);
    floatAlert.innerHTML = msg;

    if (isDuration)
    {
        let showDuration = msg.length * 100;
        if (showDuration < 6000)
        {
            showDuration = 6000;
        }
        /*
        Hide alert after time given in third param by 
        changing transparency to 0 with transition.
        */
        alertTimeout = setTimeout(() =>
        {
            hideAlertAnimation();
        }, showDuration);
    }
}

function hideAlertAnimation()
{
    floatAlert.classList.add('hide-alert');
    // Set element visibility to hidden after transition.
    alertTransTimeout = setTimeout(() =>
    {
        floatAlert.setAttribute('class', 'float-alert invisible');
    }, 400);
}


/* Belt news notification functions
========================================================================== */

/*
Remove belt notification from DOM and set 
value of is_saw_news in db of current user to true.
*/
function hideNewsNotification()
{
    let notification = document.querySelector('.belt-notification');

    if (!notification)
    {
        return;
    }

    let exitForm = notification.querySelector('form');
    let exitBtn = exitForm.querySelector('div');

    exitBtn.addEventListener('click', async e =>
    {
        fetch(exitForm.action,
            {
                method: 'POST',
                body: new FormData(exitForm)
            });
        notification.remove();
    });
}


/* Button styling functions
========================================================================== */

/*
Sets button style to btnClass (which should be a transition) for time specific in styleDuration.
Then return with transition to default button style.
*/
let buttonStyles = {}
function setButtonStyle(btn, btnClass, styleDuration)
{
    /*
    Stores classlist state for clicked buttons before any changes done by this functions.
    Use to indicate if button have additional styling classes like btn-danger cuz we don't
    want to replace them by btn-transition-default in that case.
    */
    if (!buttonStyles[btn.id])
    {
        let classList = [];
        for (const cssClass of btn.classList)
        {
            classList.push(cssClass);
        }
        buttonStyles[btn.id] = classList;
    }
    // Clear previous setTimeout only for related button that will being clicked
    if (btnTransTimeouts[btn.id])
    {
        clearTimeout(btnTransTimeouts[btn.id]['transition']);
        clearTimeout(btnTransTimeouts[btn.id]['rmTransition']);
    }

    let alreadyContainsBtnClass = buttonStyles[btn.id].includes(btnClass);
    btn.classList.add(btnClass);
    // Transition to normal btn style
    btnTransTimeouts[btn.id] = {}
    btnTransTimeouts[btn.id]['transition'] = setTimeout(() =>
    {
        if (alreadyContainsBtnClass)
        {
            btn.classList.add('btn-transition-default');
        }
        else
        {
            btn.classList.replace(btnClass, 'btn-transition-default');
        }
        btnTransTimeouts[btn.id]['rmTransition'] = setTimeout(() =>
        {
            btn.classList.remove('btn-transition-default');
        }, 400);
    }, styleDuration);
}


/* Touch devices related
========================================================================== */

/*
Indicate clicking on elements with .btn class by changing background to darker
by using touchstart and touchend events.
*/
function showTouchClick()
{
    main.addEventListener('touchstart', e=>
    {
        if (e.target.matches('.btn'))
        {
            e.target.classList.add('touch');
        }
    });
    main.addEventListener('touchend', e =>
    {
        if (e.target.matches('.btn'))
        {
            e.target.classList.remove('touch');
        }
    });
}


/* Table related
========================================================================== */

/*
Remove tr element given as paramater.
Remove table if this is the only one row in tbody element and
related h2 element with season name.
*/
function rmRow(row)
{
    const tbody = row.closest('tbody');
    if (tbody.querySelectorAll('tr').length === 1)
    {
        const table = tbody.closest('table');
        // Remove related h2 elem with season name
        table.previousElementSibling.remove();
        table.remove();
        return;
    }
    row.remove();
}

/* Others
========================================================================== */

async function loadCacheManifest()
{
    let jsonCacheManifest;
    let url = document.querySelector('#cache_manifest').dataset.cacheManifestUrl;
    try
    {
        let response = await fetch(url);
        if (!response.ok)
        {
            throw new Error();
        }
        jsonCacheManifest = await response.json();
    }
    catch
    {
        return null;
    }
    return jsonCacheManifest;
}