// Contain code execution for add_okami_subs page.



const form = document.querySelector('#main-form');
const title = document.querySelector('#title');
const titleError = document.querySelector('#title_error');
const titleOnSite = document.querySelector('#title_in_site');
const titleOnSiteError = document.querySelector('#title_in_site + .validation-error');
const seasonPageLink = document.querySelector('#season_page_link');
const seasonPageLinkError = document.querySelector('#season_page_link + .validation-error');
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
    const isSeasonPageLinkValid = valUrl(seasonPageLink, seasonPageLinkError);

    // If every input pass client validation data is sended to server in ajax manner.
    if (isTitleValid && isTitleOnSiteValid && isSeasonPageLinkValid)
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