// Contain code execution for add anime page.



const form = document.querySelector('#main-form');
const title = document.querySelector('#title');
const titleError = document.querySelector('#title + .validation-error');
const season = document.querySelector('#season');
const seasonError = document.querySelector('#season_error');
const malLink = document.querySelector('#mal_link');
const malLinkError = document.querySelector('#mal_link + .validation-error');
const coverLink = document.querySelector('#cover_link');
const coverLinkError = document.querySelector('#cover_link + .validation-error');
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
    const isTitleValid = valValueMissing(title, titleError);
    const isSeasonValid = valSelect(season, seasonError, 'Nie wybrałeś sezonu.');
    const isMalLinkValid = valUrl(malLink, malLinkError);
    const isCoverLinkValid = valUrl(coverLink, coverLinkError);

    // If every input pass client validation data is sended to server in ajax manner.
    if (isTitleValid && isSeasonValid && isMalLinkValid && isCoverLinkValid)
    {
        let isSuccessSubmit = await submit(form, submitBtn);
        // When record is added we remove choosed title from select element.
        if (isSuccessSubmit)
        {
            form.reset();
        }
    }
    else
    {
        setButtonStyle(submitBtn, 'btn-danger', 1000);
    }
});