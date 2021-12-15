const jsonCacheManifestPromise = loadCacheManifest();


// jsonCacheManifestPromise
// .then(manifestCache =>
// {
//     if (manifestCache)
//     {
//         /*
//         versioned_real_sw_url stores real relative url to the service worker file.
//         But we want use additional route which points to the service worker and is placed in root,
//         cuz we want have in scope all pages.
//         Route is: /service_worker-[hash].js or if versioned version not exist it is /service_worker.js
//         We created this additional route in flask.
//         */
//         let versioned_real_sw_url = manifestCache['general/scripts/service_worker.js'];
//         return '/' + versioned_real_sw_url.split('/').pop();
//     }
//     else
//     {
//         throw Error('Cache manifest not exist. Service worker registration failed.');
//     }  
// })
// .then(swUrl =>
// {
//     navigator.serviceWorker.register(swUrl,
//     {
//         updateViaCache: 'all'
//     })
//     .then(register =>
//     {
//         console.log('Register service worker');
//         console.log('Service worker scope: ' + register.scope);
//     });        
// });


if ('serviceWorker' in navigator)
{
    navigator.serviceWorker.register("/service_worker.js")
    .then(register =>
    {
        console.log('Register service worker.');
        console.log('Service worker scope: ' + register.scope);
    });  
}
    