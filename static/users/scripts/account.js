// Contain code execution for account page.

accInfoForm = document.querySelector('#account-form');
settingsForm = document.querySelector('#settings-form');;

// Account info form inputs
const username = document.querySelector('#username');
const usernameError = document.querySelector('#username + .validation-error');
const email = document.querySelector('#email');
const emailError = document.querySelector('#email + .validation-error');
const accountInfoSubmit = document.querySelector('#account_info_submit');

// Settings form inputs
const url = document.querySelector('#webhook');
const urlError = document.querySelector('#webhook ~ .validation-error');
const urlTip = document.querySelector('#webhook ~ small');
const notificationCheckbox = document.querySelector('#is_db_entry_notification');
const extraUrl = document.querySelector('#extra_webhook');
const extraUrlError = document.querySelector('#extra_webhook + .validation-error')
const extraUrlWrapper = extraUrl.closest('div')
const settingsSubmit = document.querySelector('#account_settings_submit');


// Toggle extra_webhook field depending on notificationCheckbox state
notificationCheckbox.addEventListener('change', e =>
{
    if (notificationCheckbox.checked)
    {
        extraUrlWrapper.classList.remove('display-none');
    }
    else
    {
        extraUrlWrapper.classList.add('display-none');
    }
});


// Account info submit
accInfoForm.addEventListener('submit', e =>
{
    e.preventDefault();

    // Client-side validation.
    const isUsernameValid = valUsername(username, usernameError);
    const isEmailValid = valEmail(email, emailError);

    // If every input pass client validation data is sended to server in ajax manner.
    if (isUsernameValid && isEmailValid)
    {
        submit(accInfoForm, accountInfoSubmit);
    }
    else
    {
        setButtonStyle(accountInfoSubmit, 'btn-danger', 1000)
    }
});


// Account settings submit
settingsForm.addEventListener('submit', async e =>
{
    e.preventDefault();

    // Client-side validation.
    const isUrlValid = valWebhook(url, urlError, urlTip, extraUrl);
    const isExtraUrlValid = valExtraWebhook(extraUrl, extraUrlError, url);
    
    // If every input pass client validation data is sended to server in ajax manner.
    if (isUrlValid && isExtraUrlValid)
    {
        /*
        Button will be disabled for time of processing submit by server and for 4s after that
        to prevent abusing discord server which is used to validate given by user webhook.
        */
        settingsSubmit.disabled = true;
        await submit(settingsForm, settingsSubmit);
        setTimeout(() => 
        {
            settingsSubmit.disabled = false;
            settingsSubmit.classList.add("enabled-transition");
            setTimeout(() =>
            {
                settingsSubmit.classList.remove("enabled-transition");
            }, 400);
        }, 4000);
    }
    else
    {
        setButtonStyle(settingsSubmit, 'btn-danger', 1000)
    }    

    // Move error before tip if error is displayed.
    moveErrorBeforeTip(urlError, urlTip);
});