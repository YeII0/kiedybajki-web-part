// Contains functions for admin blueprint

/* Row specific
========================================================================== */

// Check if row is visible on screen
function isRowVisible(row)
{
    let isVisible;

    /*
    True when big screen table layout media query is active.
    Note: tr element is excluded from DOOM in this query.
    */
    if (window.matchMedia('screen and (min-width: 62.5em)').matches)
    {
        const firstTdRect = row.firstElementChild.getBoundingClientRect();
        const thHeight = document.querySelector('th').offsetHeight;
        /*
        top value need to be greater or equal to thHeight 
        cuz we consider td element as not visible when is overlapped by sticky th.
        */
        isVisible = (
            firstTdRect.top >= thHeight &&
            firstTdRect.left >= 0 &&
            firstTdRect.bottom <= (window.innerHeight) &&
            firstTdRect.right <= (window.innerWidth)
        );
    }
    // Execute when mobile table layout media query is active.
    else
    {
        const rowRect = row.getBoundingClientRect();
        isVisible = (
            rowRect.top >= 0 &&
            rowRect.left >= 0 &&
            rowRect.bottom <= (window.innerHeight) &&
            rowRect.right <= (window.innerWidth)
        );
    }


    return isVisible;
}

/*
Scroll vertically to show row in viewport.
For desktop table layout row is showed in a center of screen.
For mobile table layout row will be centered in viewport if possible.
If viewport will be too small top of row will be aligned the the top of viewport.
*/
function scrollToRow(row)
{
    /* 
    True when big screen table layout media query is active.
    Note: tr element is excluded from DOOM in this query.
    */
    if (window.matchMedia('screen and (min-width: 62.5em)').matches)
    {
        const firstTdRect = row.firstElementChild;
        window.scrollBy(
            0,
            firstTdRect.getBoundingClientRect().top - 
            (window.innerHeight / 2) + 
            (firstTdRect.height / 2)
        );
    } 
    // Execute when mobile table layout media query is active.
    else
    {
        const rowRect = row.getBoundingClientRect();
        /*
        When row height will be greater than viewport height row will be centered.
        Otherwise to edge of row will be aligned to the top of viewport.
        */
        if (rowRect.height < window.innerHeight)
        {
            window.scrollBy(0, rowRect.top - (window.innerHeight / 2) + (rowRect.height / 2));
        }
        else
        {
            window.scrollBy(0, rowRect.top);
        }
    }   

}


/* Select
========================================================================== */

function rmSelectedOption(select)
{
    select.selectedOptions[0].remove();
}


function selectOptionsToJson(select)
{
    let json = []
    for (option of select.children)
    {
        let pair = {};
        pair[String((option.value))] = option.textContent;
        json.push(pair);
    }
    return json;
}


/* Specific validators
========================================================================== */

function valSelect(input, inputError, msg, isToggleErrorDisplay)
{
    let isValid = false;
    if (input.value === "-1")
    {
        inputError.textContent = msg;
        input.classList.add('invalid-input');
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

// inputTip and isToggleErrorDisplay params are optional
function valCrNumberingDiff(input, inputError, inputTip, isToggleErrorDisplay)
{
    let isValid = false;
    if (!input.validity.valid)
    {
        inputError.textContent = '';
        input.classList.add('invalid-input')
        if (inputTip)
        {
            inputTip.insertAdjacentElement('beforebegin', inputError);
        }
        if (input.validity.valueMissing)
        {
            inputError.textContent = requiredMsg;
        }
        if (input.validity.badInput)
        {
            inputError.textContent = 'Podaj liczbę. '
        }
        if (input.validity.stepMismatch)
        {
            inputError.textContent += 'Podaj liczbę całkowitą. ';
        }
        if (input.validity.rangeUnderflow)
        {
            inputError.textContent += 'Liczba musi być większa od zera.';
        }
    }
    else
    {
        inputError.textContent = '\u200B';
        input.classList.remove('invalid-input')
        if (inputTip)
        {
            inputTip.insertAdjacentElement('afterend', inputError);
        }        
        isValid = true;
    }

    if (isToggleErrorDisplay)
    {
        toggleErrorDisplay(inputError, isValid);
    }

    return isValid;
}

function valCrDiffTitle(input, inputError, isToggleErrorDisplay, cr_numbering_diff)
{
    let isValid = false;

    if (input.value && cr_numbering_diff === 0)
    {   
        input.classList.add('invalid-input');
        inputError.textContent = 'Wypełnij tylko w wypadku różnicy w numeracji.';
    }
    else if(!input.value && cr_numbering_diff !== 0)
    {
        input.classList.add('invalid-input');
        inputError.textContent = 'Należy wypełnić jeśli wybrałeś inna numerację.';        
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

/* anime.html specific 
========================================================================== */

/*
When title is changed move row to keep title ordering,
additionaly if and/or different season that current is choosed move 
row to right table with keeping rows title ordering.
*/
let lastTitleInputValue = {};
function moveRow(titleInput, seasonInput)
{
    const srcTable = titleInput.closest('table');
    /* 
    When season is selected and is different than current season
    tr is moved to right table keeping row order sorted by title.
    */
    if (
        seasonInput.value !== '-1' &&
        srcTable.id !== seasonInput.value
    )
    {
        const destTable = document.querySelector(`table[id="${seasonInput.value}"]`);

        /* 
        Empty season table with heading are hidden so we need to show them 
        by removing display-none class.
        */
        if (destTable.classList.contains('display-none'))
        {
            destTable.classList.remove('display-none');
            // Show also hidden header
            destTable.previousElementSibling.classList.remove('display-none');
        }

        const titleInputs = destTable.querySelectorAll('input[name="title"]');
        _moveTr(titleInputs, titleInput, destTable);

        // Hide empty table
        if (!srcTable.querySelector('tbody').querySelector('tr'))
        {
            srcTable.classList.add('display-none');
            // Hide also header
            srcTable.previousElementSibling.classList.add('display-none');
        }
    }
    /*
    When title has changed, row is move to right 
    place keeping row order sorted by title.
    */
    else if (titleInput.value !== (lastTitleInputValue[titleInput.id] || titleInput.defaultValue))
    {
        lastTitleInputValue[titleInput.id] = titleInput.value;
        const titleInputs = srcTable.querySelectorAll('input[name="title"]');
        _moveTr(titleInputs, titleInput, srcTable);
    }
}


/*
Used in moveRow.
Check given titleInputs and move row to right place keeping right row order sorted
by title.
*/
function _moveTr(titleInputs, titleInput, destTable)
{
    const inputTr = titleInput.closest('tr');
    let isMoved = false;
    for (otherTitleInput of titleInputs)
    {
        /*
        Need to check if titleInput !== otherTitleInput cuz without that when we occur
        element to move in titleInputs it will just move itself before itself. 
        */
        if (
            titleInput.value.toLowerCase() <= otherTitleInput.value.toLowerCase() &&
            titleInput !== otherTitleInput
        )
        {
            const otherInputTr = otherTitleInput.closest('tr');
            otherInputTr.insertAdjacentElement('beforebegin', inputTr);
            isMoved = true;
            break;
        }
    }
    /*
    When titleInput value is not smaller than any of titleInputs above loop will not move row.
    Instead will set isMoved variable to true. Row will be moved at the end of destination table.
    */
    if (!isMoved)
    {
        if (titleInputs.length)
        {
            const lastTitleTr = titleInputs[titleInputs.length - 1].closest('tr');
            lastTitleTr.insertAdjacentElement('afterend', inputTr);
        }
        else
        {
            const tbody = destTable.querySelector('tbody');
            tbody.appendChild(inputTr);
        }
    }
}