const offlineFallbackPage = "bienvenue.html";

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

self.addEventListener('install', async (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.add(offlineFallbackPage))
  );
});

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

// Register event listener for the 'push' event.
self.addEventListener('push', function(event) {
  // Retrieve the textual payload from event.data (a PushMessageData object).
  // Other formats are supported (ArrayBuffer, Blob, JSON), check out the documentation
  // on https://developer.mozilla.org/en-US/docs/Web/API/PushMessageData.
  let payload = event.data ? event.data.text() : {"head": "No Content", "body": "No Content", "icon": ""},
    data = JSON.parse(payload),
    head = data.head,
    body = data.body,
    icon = data.icon;
    // If no url was received, it opens the home page of the website that sent the notification
    // Whitout this, it would open undefined or the service worker file.
    url = data.url ? data.url: self.location.origin;

  // Keep the service worker alive until the notification is created.
  event.waitUntil(
    // Show a notification with title 'ServiceWorker Cookbook' and use the payload
    // as the body.
    self.registration.showNotification(head, {
      body: body,
      icon: icon,
      data: {url: url}	
    })
  );
});


//user clicked / tapped a push notification
self.addEventListener('notificationclick', function(event) {
    const clickedNotification = event.notification;
    clickedNotification.close();

    //exit if the url could not be found
    if (!event.notification.data || !event.notification.data.url) return;

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
            }
        })
    );
});