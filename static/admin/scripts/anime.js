// Contain code execution for edit anime page.




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
        const title = editedRow.querySelector(`input[name="title"]`);
        const titleError = editedRow.querySelector(`input[name="title"] + .validation-error`);
        const season = editedRow.querySelector(`select[name="season"]`);
        const malLink = editedRow.querySelector('input[name="mal_link"]');
        const malLinkError = editedRow.querySelector('input[name="mal_link"] + .validation-error');
        const coverLink = editedRow.querySelector('input[name="cover_link"]');
        const coverLinkError = editedRow.querySelector('input[name="cover_link"] + .validation-error');        

        // Client form validation
        const isTitleValid = valValueMissing(title, titleError, true);
        const isMalLinkValid = valUrl(malLink, malLinkError, true);
        let isCoverLinkValid;
        if (coverLink.value === "")
        {
            isCoverLinkValid = true;
        }
        else
        {
            isCoverLinkValid = valUrl(coverLink, coverLinkError, true)
        }

        // Submit if client validation is passed
        if (isTitleValid && isMalLinkValid && isCoverLinkValid)
        {
            const isSuccessSubmit = await submit(e.target, submitBtn, true);
            // If submitted with success move row if needed and scroll to it if it's not visible
            if (isSuccessSubmit)
            {
                moveRow(title, season);
            }
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