// Contain functions for subscriptions and subscribe pages.

/*
Sends form data to server and update UI accordingly to response.
Subscriptions and not subscribe page have different functions for removing row
so it's passed here as a second parameter.
To third parameter pass param in array for noContentResponse function.
*/
async function updateSub(form, rmRowFn, noContentResponseParams)
{
    const submitBtn = document.querySelector(`input[type="submit"][form="${form.id}"]`);
    submitBtn.classList.add('btn-loading');
    let response;

    formData = new FormData(form);
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
        setButtonStyle(submitBtn, 'btn-danger', 1000);
        showFloatAlert('Nie udało połączyć się z serwerem. Spróbuj później.', 'error', true);
        return;
    }
    if (!response.ok)
    {
        setButtonStyle(submitBtn, 'btn-danger', 1000);
        showFloatAlert('Błąd serwera. Spróbuj ponownie.', 'error', true);
        return;
    }

    rData = await response.json();
    submitBtn.classList.remove('btn-loading');
    if (rData.isSuccess)
    {
        setButtonStyle(submitBtn, 'btn-success', 500);
        // We want to remove row only when subscription was updated
        // so functions below are invoked here.
        rmRowFn(submitBtn);
        await noContentResponse(
            noContentResponseParams[0], 
            noContentResponseParams[1], 
            noContentResponseParams[2]
        );
    }
    else
    {
        setButtonStyle(submitBtn, 'btn-danger', 1000);
        showFloatAlert(rData.errorMsg, 'error', true);
    }
}


/*
Remove row with title. When row will be remove depends on second parameter.
When rmWhenSel is true row is remove when any checkbox is selected (add_subscription page use case).
When rmWhenSel is false row is remove when all checkboxes are deselected (subscription page use case).
*/
function rmTitle(submitBtn, rmWhenSel)
{
    const row = submitBtn.closest('tr');
    const checkboxes = row.querySelectorAll('input[type="checkbox"]');
    let anySelected = false;

    for (let checkbox of checkboxes)
    {
        if (checkbox.checked)
        {
            anySelected = true;
            break;
        }
    }

    if (anySelected && rmWhenSel)
    {
        rmRow(row);
    }
    else if (!anySelected && !rmWhenSel)
    {
        rmRow(row);
    }
}
 
/*
Shows emote with message when everything is removed from subscription list.
In other word when there any table left in main element.
*/
async function noContentResponse(emoteUrl, imgAltAttribute, paraText)
{
    // Prefetch emote
    const tables = document.querySelectorAll('table');
    if (tables && tables.length === 1)
    {
        const tbody = tables[0].querySelector('tbody');
        if (tbody.childElementCount <= 2)
        {
            fetch(emoteUrl);
        }
    }

    if (tables.length)
    {
        return;
    }

    // Remove h1 element
    if (main.querySelector('h1'))
    {
        main.querySelector('h1').remove();
    }

    const img = document.createElement('img');
    img.src = emoteUrl;
    img.alt = imgAltAttribute;

    const para = document.createElement('p');
    para.setAttribute('class', 'center-text');
    para.textContent = `${paraText} `;
    para.appendChild(img);

    main.appendChild(para);
}


/* Cover functions
========================================================================== */

/*
Cover showing and hiding.
*/
let lastLinks = {};
function showHideCovers()
{
    // Cover handling for devices with hover capability like mouse.
    if (window.matchMedia('screen and (hover: hover)').matches)
    {
        main.addEventListener("mouseover", e =>
        {
            if (e.target.matches('table a'))
            {
                _showCover(e.target);
            }
        });
        main.addEventListener("mouseout", e =>
        {
            if (e.target.matches('table a'))
            {
                _hideCover(e.target);
            }
        });
    }
    // Cover handling for devices without hover capability like phones with touch screens.
    else if (window.matchMedia('screen and (hover: none)').matches)
    {
        main.addEventListener("touchstart", e =>
        {
            for (href in lastLinks)
            {
                _hideCover(lastLinks[href]);
            }
            lastLinks = {};

            if (
                e.target.matches('tbody td:first-child') ||
                e.target.matches('tbody td:first-child *')
            )
            {
                let malLinkElem;
                if (e.target.nodeName == 'A')
                {
                    malLinkElem = e.target;
                }
                else
                {
                    malLinkElem = e.target.querySelector('a');
                }

                _showCover(malLinkElem);
                lastLinks[malLinkElem.href] = malLinkElem;
            }
        });
        main.addEventListener("touchend", e =>
        {
            for (href in lastLinks)
            {
                _hideCover(lastLinks[href]);
            }
            lastLinks = {};
        });
    }
}


function _showCover(malLinkElem)
{
    let link = malLinkElem;
    let linkRect = link.getBoundingClientRect();
    let linkHeight = linkRect.height;

    let coverContainer = link.closest('div').querySelector('.cover-container');
    if (!coverContainer)
    {
        return;
    }
     
    coverContainer.style.visibility = 'hidden';
    coverContainer.classList.remove('display-none');

    let coverContainerHeight = coverContainer.getBoundingClientRect().height;
    let viewportHeight = window.innerHeight;
    let cover = coverContainer.querySelector('img');

    // Scale down cover if viewport height is too small to size specified by main.css. 
    if (coverContainerHeight + linkHeight + 32 > viewportHeight)
    {
        cover.style.maxHeight = coverContainerHeight - 
            (coverContainerHeight + linkHeight + 32 - viewportHeight) - 16 + 'px';
    }
    // Positioning absolute cover cointainer.
    if ((viewportHeight - linkRect.bottom) > coverContainerHeight + 32)
    {
        coverContainer.style.top = `${(linkHeight / 10) + 0.8}rem`;
        coverContainer.style.bottom = 'auto';
    }
    else
    {
        coverContainer.style.bottom = `${(linkHeight / 10) + 0.8}rem`;
        coverContainer.style.top = 'auto';
    }
    coverContainer.style.visibility = 'visible';
}


function _hideCover(malLinkElem)
{
    let link = malLinkElem;
    let coverContainer = link.closest('div').querySelector('.cover-container');
    if (!coverContainer)
    {
        return;
    }

    coverContainer.classList.add('display-none');    
    let cover = coverContainer.querySelector('img');
    cover.style.maxHeight = 'initial';
}


/*
Handling img error which can occurs while loading image from src url.
When error occurs cover container will be removed from DOM.
*/
function handleCoverLoadError()
{
    document.querySelectorAll('.cover-container img').forEach(img =>
    {
        img.addEventListener('error', e =>
        {
            let coverContainer = e.target.closest('.cover-container');
            coverContainer.remove();
        });
    });
}