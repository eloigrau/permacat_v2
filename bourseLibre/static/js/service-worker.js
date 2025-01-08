self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const preloadResp = await event.preloadResponse;

        if (preloadResp) {
          return preloadResp;
        }

        const networkResp = await fetch(event.request);
        return networkResp;
      } catch (error) {

        const cache = await caches.open(CACHE);
        const cachedResp = await cache.match(offlineFallbackPage);
        return cachedResp;
      }
    })());
  }
});


//user clicked / tapped a push notification
self.addEventListener('notificationclick', function(event) {
    const clickedNotification = event.notification;
    clickedNotification.close();

    //exit if the url could not be found
    if (!event.notification.data || !event.notification.data.url) return clients.openWindow("/");

    //get url from event
    var url = event.notification.data.url;
    //if the url contains a #, remove it and everything after it
    var cleanedUrl = url.indexOf('#') ? url.substring(0, url.indexOf('#')) :url;

    event.waitUntil(
        self.clients.matchAll({type: 'window', includeUncontrolled: true}).then( windowClients => {
            console.log('opening window', windowClients.length, 'windows')
            // Check if there is already a window/tab open with the target URL
            for (var i = 0; i < windowClients.length; i++) {
                var client = windowClients[i];

                //if the page url contains a #, remove it and everything after it
                var cleanedClientUrl;
                if (client.url.indexOf('#') !== -1)
                    cleanedClientUrl = client.url.substring(0, client.url.indexOf('#'));
                else cleanedClientUrl = client.url;

                // if the cleaned URLs match
                if (cleanedClientUrl === cleanedUrl && 'focus' in client) {
                    //focus and reload the window that has this page open
                    client.focus();

                    //if the url had a # in it, first navigate to the cleaned url (otherwise it wont refresh)
                    if (url.indexOf('#')) {
                      return client.navigate(cleanedUrl)
                      .then(() => client.navigate(url));
                    } else {
                      return client.navigate(url);
                    }

                    client.navigate(url);

                    return;
                }
            }
            // If not, then open the target URL in a new window/tab.
            if (self.clients.openWindow) {
                return self.clients.openWindow(url);
            }else{
                return self.clients.openWindow("/");
            }
        })
    );
});
