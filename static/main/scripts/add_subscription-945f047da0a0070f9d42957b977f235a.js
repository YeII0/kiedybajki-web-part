// Contain code execution for subscriptions page.


showHideCovers();
handleCoverLoadError();

/*
Submit event delegation for form element.
Handler is custom submit with UI update accordingly to response from server.
*/
main.addEventListener('submit', async e =>
{
    if (e.target.matches('form[id^="form-anime-"]'))
    {
        e.preventDefault();

        let cacheManifest = await jsonCacheManifestPromise;
        let url;
        if (cacheManifest)
        {
            url = '/static/' + cacheManifest['general/media/emotes/pogchamp.png'];
        }
        else
        {
            url = '/static/general/media/emotes/pogchamp.png';
        }
        

        updateSub(
            e.target,
            submitBtn => rmTitle(submitBtn, true),
            [url, 'pogchamp', 'Subskrybujesz wszystko']
        ).catch(console.log);
    }
});
