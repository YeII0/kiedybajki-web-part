// Contain code execution for edit anime-odcinki page.

main.addEventListener('submit', async e =>
{
    /*
    If target form has id it means that is form for editing
    because form for deleting doesn't have id.
    */
    if (e.target.matches('form[id^="form-anime-"]'))
    {
        e.preventDefault();

        const submitBtn = document.querySelector(`input[form="${e.target.id}"][type="submit"]`);
        const editedRow = submitBtn.closest('tr');
        const url = editedRow.querySelector('input[name="source_link"]');
        const urlError = editedRow.querySelector('input[name="source_link"] + .validation-error');

        // Client form validation
        const isUrlValid = valUrl(url, urlError, true);

        // Submit if client validation is passed
        if (isUrlValid)
        {
            await submit(e.target, submitBtn, true);
        }
        else
        {
            setButtonStyle(submitBtn, 'btn-danger', 1000);
        }
    }
    // Matches delete form.
    else if (e.target.matches('form[id^="del-anime-form-"]'))
    {
        e.preventDefault();

        const rmButton = e.target.firstElementChild;
        const isSuccessSubmit = await submit(e.target, rmButton, true);
        if (isSuccessSubmit)
        {
            rmRow(rmButton.closest('tr'));
        }
    }
});