// Contain code execution for add_animesub_forum page.



const form = document.querySelector('#main-form');
const title = document.querySelector('#title');
const titleError = document.querySelector('#title_error');
const sourceLink = document.querySelector('#source_link');
const sourceLinkError = document.querySelector('#source_link + .validation-error');
const author = document.querySelector('#author');
const authorError = document.querySelector('#author + .validation-error');
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
    const isSourceLinkValid = valUrl(sourceLink, sourceLinkError);
    const isAuthorValid = valValueMissing(author, authorError);
    const isCrNumberingDiffValid = valCrNumberingDiff(crNumberingDiff, crNumberingDiffError, crNumberingDiffTip);
    const isCrDiffTitleValid = valCrDiffTitle(crDiffTitle, crDiffTitleError, false, parseInt(crNumberingDiff.value));

    // If every input pass client validation data is sended to server in ajax manner.
    if (isTitleValid && isSourceLinkValid && isAuthorValid && isCrNumberingDiffValid && isCrDiffTitleValid)
    {
        let isSuccessSubmit = await submit(form, submitBtn);
        if (isSuccessSubmit)
        {
            form.reset();
        }
        else
        {
            moveErrorBeforeTip(crNumberingDiffError, crNumberingDiffTip);
        }
    }
    else
    {
        setButtonStyle(submitBtn, 'btn-danger', 1000);
    }
});