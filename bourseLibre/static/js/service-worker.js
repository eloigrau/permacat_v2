
// when the browser fetches a url
self.addEventListener('fetch', function(event) {
    // either respond with the cached object or go ahead and fetch the actual url
    event.respondWith(
        caches.match(event.request).then(function(response) {
            if (response) {
                // retrieve from cache
                return response;
            }
            // fetch as normal
            return fetch(event.request);
        })
    );
});

// Register event listener for the 'push' event.
self.addEventListener('push', function (event) {
    // Retrieve the textual payload from event.data (a PushMessageData object).
    // Other formats are supported (ArrayBuffer, Blob, JSON), check out the documentation
    // on https://developer.mozilla.org/en-US/docs/Web/API/PushMessageData.
    const eventInfo = event.data.text();
    const data = JSON.parse(eventInfo);
    const head = data.head || 'Nouvelle Notification';
    const body = data.body || 'Message mystérieux';

    // Keep the service worker alive until the notification is created.
    event.waitUntil(
        // Show a notification with title 'ServiceWorker Cookbook' and use the payload
        // as the body.
        self.registration.showNotification(head, {
            body: body,œ
        })
    );
});


self.addEventListener('notificationclick', function(event) {

    if (Notification.prototype.hasOwnProperty('data')) {
    console.log('Using Data');
    var url = event.notification.data.url;
    event.waitUntil(clients.openWindow(url));
    } else {
     event.waitUntil(
    clients.matchAll({
        type: "window"
    })
    .then(function(clientList) {
        for (var i = 0; i < clientList.length; i++) {
        var client = clientList[i];
        if (client.url == '/' && 'focus' in client)
            return client.focus();
        }
        if (clients.openWindow) {
        return clients.openWindow('/');
        }
    })
    );
    }));
    }
});