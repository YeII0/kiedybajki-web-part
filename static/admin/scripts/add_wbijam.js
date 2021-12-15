// Contain code execution for add_wbijam and add_anime_odcinki pages.

const form = document.querySelector('#main-form');
const title = document.querySelector('#title');
const titleError = document.querySelector('#title_error');
const sourceLink = document.querySelector('#source_link');
const sourceLinkError = document.querySelector('#source_link + .validation-error');

const titleOnSite = document.querySelector('#title_in_site');
const titleOnSiteError = document.querySelector('#title_in_site + .validation-error');
const crNumberingDiff = document.querySelector('#cr_numbering_diff');
const crNumberingDiffError = document.querySelector('#cr_numbering_diff ~ .validation-error');
const crNumberingDiffTip = document.querySelector('#cr_numbering_diff ~ small');
const crDiffTitle = document.querySelector('#cr_diff_title');
const crDiffTitleError = document.querySelector('#cr_diff_title + .validation-error');

const submitBtn = document.querySelector('input[type="submit"]');

/*
Custom submit behaviour.
Before sending forms we doing client-side form validation.
If everthing is okey form is send and response is handled in ajax manner.
UI is updated accordingly to response sended in json format.
*/
form.addEventListener('submit', async e =>
{
    e.preventDefault();

    // Client-side validation.
    const isTitleValid = valSelect(title, titleError, 'Nie wybrałeś anime.');
    const isTitleOnSiteValid = valValueMissing(titleOnSite, titleOnSiteError);   
    const isSourceLinkValid = valUrl(sourceLink, sourceLinkError);
    const isCrNumberingDiffValid = valCrNumberingDiff(crNumberingDiff, crNumberingDiffError, crNumberingDiffTip);
    const isCrDiffTitleValid = valCrDiffTitle(crDiffTitle, crDiffTitleError, false, parseInt(crNumberingDiff.value));

    // If every input pass client validation data is sended to server in ajax manner.
    if (isTitleValid && isTitleOnSiteValid && isSourceLinkValid && isCrNumberingDiffValid && isCrDiffTitleValid)
    {
        let isSuccessSubmit = await submit(form, submitBtn);
        // When record is added we remove choosed title from select element.
        if (isSuccessSubmit)
        {
            rmSelectedOption(title);
            form.reset();
        }
    }
    else
    {
        setButtonStyle(submitBtn, 'btn-danger', 1000);
    }
});