/**
 * Service Worker for MedLab Pro PWA
 * Handles caching, offline functionality, and background sync
 */

const CACHE_NAME = 'medlab-pro-v1.0.0';
const DYNAMIC_CACHE = 'medlab-pro-dynamic-v1';

// Core files to cache for offline functionality
const CORE_CACHE_FILES = [
    '/',
    '/static/css/tailwind.min.css',
    '/static/js/app.js',
    '/static/js/language-system.js',
    '/static/js/smart-notifications.js',
    '/static/js/mobile-app-companion.js',
    '/static/img/logo.png',
    '/static/img/icon-192.png',
    '/static/img/icon-512.png'
];

// Install event - cache core files
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Service Worker: Caching core files');
                return cache.addAll(CORE_CACHE_FILES);
            })
            .then(() => {
                console.log('Service Worker: Installation complete');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Service Worker: Installation failed', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME && cacheName !== DYNAMIC_CACHE) {
                            console.log('Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activation complete');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip chrome-extension and other non-http requests
    if (!url.protocol.startsWith('http')) {
        return;
    }

    // Handle API requests differently
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }

    // Handle static assets and pages
    event.respondWith(
        caches.match(request)
            .then((cachedResponse) => {
                // Return cached version if available
                if (cachedResponse) {
                    return cachedResponse;
                }

                // Otherwise fetch from network and cache dynamically
                return fetch(request)
                    .then((networkResponse) => {
                        // Don't cache if not successful
                        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                            return networkResponse;
                        }

                        // Cache successful responses
                        const responseToCache = networkResponse.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then((cache) => {
                                cache.put(request, responseToCache);
                            });

                        return networkResponse;
                    })
                    .catch(() => {
                        // Return offline page for navigation requests
                        if (request.mode === 'navigate') {
                            return caches.match('/offline.html');
                        }
                        
                        // Return cached version or offline indicator
                        return new Response('Offline', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
            })
    );
});

// Handle API requests with offline support
async function handleApiRequest(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        // Cache successful API responses for offline access
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        // Network failed, try cache
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response for API calls
        return new Response(JSON.stringify({
            error: 'Offline',
            message: 'This feature requires an internet connection'
        }), {
            status: 503,
            statusText: 'Service Unavailable',
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Background sync for data when coming back online
self.addEventListener('sync', (event) => {
    console.log('Service Worker: Background sync triggered', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(syncData());
    }
});

async function syncData() {
    try {
        // Get pending data from IndexedDB or localStorage
        const pendingData = await getPendingData();
        
        if (pendingData.length > 0) {
            console.log('Service Worker: Syncing pending data', pendingData.length, 'items');
            
            for (const item of pendingData) {
                try {
                    await syncDataItem(item);
                    await removePendingData(item.id);
                } catch (error) {
                    console.error('Service Worker: Failed to sync item', item.id, error);
                }
            }
        }
    } catch (error) {
        console.error('Service Worker: Background sync failed', error);
    }
}

async function getPendingData() {
    // In a real implementation, this would read from IndexedDB
    const pending = localStorage.getItem('pendingSync');
    return pending ? JSON.parse(pending) : [];
}

async function syncDataItem(item) {
    const response = await fetch(item.url, {
        method: item.method,
        headers: item.headers,
        body: item.body
    });
    
    if (!response.ok) {
        throw new Error(`Sync failed: ${response.status}`);
    }
    
    return response;
}

async function removePendingData(itemId) {
    const pending = await getPendingData();
    const filtered = pending.filter(item => item.id !== itemId);
    localStorage.setItem('pendingSync', JSON.stringify(filtered));
}

// Push notifications
self.addEventListener('push', (event) => {
    console.log('Service Worker: Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from MedLab Pro',
        icon: '/static/img/icon-192.png',
        badge: '/static/img/badge.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'view',
                title: 'View',
                icon: '/static/img/icon-view.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/img/icon-close.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('MedLab Pro', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Service Worker: Notification clicked', event);
    
    event.notification.close();
    
    if (event.action === 'view') {
        // Open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker: Message received', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_UPDATE') {
        // Force cache update
        event.waitUntil(updateCache());
    }
});

async function updateCache() {
    console.log('Service Worker: Updating cache');
    
    const cache = await caches.open(CACHE_NAME);
    const requests = await cache.keys();
    
    // Update all cached resources
    await Promise.all(
        requests.map(async (request) => {
            try {
                const response = await fetch(request);
                if (response.ok) {
                    await cache.put(request, response);
                }
            } catch (error) {
                console.warn('Service Worker: Failed to update cached resource', request.url);
            }
        })
    );
    
    console.log('Service Worker: Cache update complete');
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'background-fetch-data') {
        event.waitUntil(fetchLatestData());
    }
});

async function fetchLatestData() {
    try {
        // Fetch latest critical data in background
        const response = await fetch('/api/critical-updates');
        if (response.ok) {
            const data = await response.json();
            
            // Store in cache for immediate access
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put('/api/critical-updates', new Response(JSON.stringify(data)));
            
            // Notify main thread if needed
            const clients = await self.clients.matchAll();
            clients.forEach(client => {
                client.postMessage({
                    type: 'CRITICAL_UPDATE',
                    data: data
                });
            });
        }
    } catch (error) {
        console.error('Service Worker: Background fetch failed', error);
    }
}