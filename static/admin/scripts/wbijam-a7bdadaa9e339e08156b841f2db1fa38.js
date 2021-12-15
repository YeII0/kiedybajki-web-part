// Contain code execution for edit wbijam page.

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
        const titleInSite = editedRow.querySelector('input[name="title_in_site"]');
        const titleInSiteError = editedRow.querySelector('input[name="title_in_site"] + .validation-error');        
        const url = editedRow.querySelector('input[name="source_link"]');
        const urlError = editedRow.querySelector('input[name="source_link"] + .validation-error');
        const crNumberingDiff = editedRow.querySelector('input[name="cr_numbering_diff"]');
        const crNumberingDiffError = editedRow.querySelector('input[name="cr_numbering_diff"] + .validation-error');     
        const crDiffTitle = editedRow.querySelector('input[name="cr_diff_title"]');
        const crDiffTitleError = editedRow.querySelector('input[name="cr_diff_title"] + .validation-error');                 

        
        // Client form validation
        const isTitleInSiteValid = valValueMissing(titleInSite, titleInSiteError, true);       
        const isUrlValid = valUrl(url, urlError, true);
        const isCrNumberingDiffValid = valCrNumberingDiff(crNumberingDiff, crNumberingDiffError, false, true);
        const isCrDiffTitleValid = valCrDiffTitle(crDiffTitle, crDiffTitleError, true, parseInt(crNumberingDiff.value));

        // Submit if client validation is passed
        if (isTitleInSiteValid && isUrlValid && isCrNumberingDiffValid && isCrDiffTitleValid)
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