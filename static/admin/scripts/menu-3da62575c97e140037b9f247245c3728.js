// Contain code execution for menu page.



main.addEventListener('submit', async e =>
{
    e.preventDefault();
    let submitBtn = e.target.querySelector('input[type="submit"]')
    submit(e.target, submitBtn);
});