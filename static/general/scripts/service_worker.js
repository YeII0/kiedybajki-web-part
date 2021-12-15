// Last update_service_worker command use: 2021-04-14 23:57:13. DON'T REMOVE THIS LINE.

const cachePrefix = 'assets'

async function loadCacheManifest()
{
    let jsonCacheManifest;
    try
    {
        let timestamp = Date.now();
        let response = await fetch("/static/cache_manifest.json?timestamp=" + timestamp);
        if (!response.ok)
        {
            throw new Error('Http error occur while fetching cache manifest.');
        }
        jsonCacheManifest = await response.json();
    }
    catch
    {
        return null;
    }
    return jsonCacheManifest;
}


async function findCacheNewestVersion()
{
    let cacheNames = await caches.keys();
    let maxVersion = 0;
    for (cacheName of cacheNames)
    {
        let version = parseInt(cacheName.split('-').pop().slice(1));
        if (version > maxVersion)
        {
            maxVersion = version;
        }
    }
    return maxVersion;
}


async function precache()
{
    let cacheManifest = await loadCacheManifest();
    if (!cacheManifest)
    {
        throw Error('Cache manifest not exist. Service worker installation failed.');
    }
    let newestCacheVersion = await findCacheNewestVersion();
    let cache = await caches.open(`${cachePrefix}-v${newestCacheVersion + 1}`);
    console.log('[oninstall] Cache assets.');
    cache.add('offline');

    for (origRelPath in cacheManifest)
    {
        cache.add('/static/' + cacheManifest[origRelPath]);
    }
    // Add covers to cache
    let response = await fetch('/cover_urls')
    if (!response.ok)
    {
        throw Error(`Can't fetch cover_urls. Service worker installation failed.`)
    }
    let cover_urls = await response.json();
    cache.addAll(cover_urls);
}


async function rmOldCaches()
{
    let cacheManifest = await loadCacheManifest();
    if (!cacheManifest)
    {
        throw Error('Cache manifest not exist. Service worker activation failed.');
    }
    let newestCacheVersion = await findCacheNewestVersion();
    let newestCacheName = `${cachePrefix}-v${newestCacheVersion}`;
    let cacheNames = await caches.keys();
    
    return Promise.all(
        cacheNames.map(cacheName =>
        {
            if (cacheName !== newestCacheName)
            {
                return caches.delete(cacheName);
            }
        })
    )
    .then(() => console.log('[onActivate] Old cache entries removed.'))
    .catch(err => 
    {
        console.log('[onactivate] Old cache entries remove attempt fail.\n' + err);
        throw new Error(err);
    });   
}


async function fetchRespond(e)
{
    let newestCacheVersion = await findCacheNewestVersion();
    let newestCacheName = `${cachePrefix}-v${newestCacheVersion}`;
    let cache = await caches.open(newestCacheName);
    let response = await cache.match(e.request);
    if (response)
    {
        return response;
    }
    try
    {
        response = await fetch(e.request);
    }
    catch (err)
    {
        console.error('[onfetch] Failed. Serving cached offline fallback.\n ' + err);
        return cache.match('offline');
    }
    // Want to cache here only response fonts
    let requestOrigin = new URL(e.request.url).origin;
    if (
        !response || 
        response.status !== 200 ||
        (
            requestOrigin !== 'https://fonts.gstatic.com' && 
            requestOrigin !== 'https://fonts.googleapis.com'
        ) 
    )
    {
        return response;
    }
    cache.put(e.request, response.clone());
    return response;    
}


self.addEventListener('install', e =>
{
    e.waitUntil(precache());
});

self.addEventListener('activate', e =>
{
    e.waitUntil(rmOldCaches());
});

self.addEventListener('fetch', e =>
{
    if (e.request.method === 'GET')
    {
        e.respondWith(fetchRespond(e));
    }
});