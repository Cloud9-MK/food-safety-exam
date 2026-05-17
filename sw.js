/* ========================================================================
 *  Costco Food Safety Exam — Service Worker
 *  オフライン対応 / アプリ更新ハンドリング
 *  ----------------------------------------------------------------------
 *  キャッシュ戦略：
 *    - HTML（試験本体・index）  : Network First（最新を優先・失敗時はキャッシュ）
 *    - 画像・manifest・アイコン : Cache First（高速）
 *    - その他                    : Cache First
 *  バージョン更新時は CACHE_VERSION を上げると古いキャッシュが破棄されます。
 *  ====================================================================== */

const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME    = `food-safety-exam-${CACHE_VERSION}`;

/* オフラインで最初から動くようにプリキャッシュするリソース */
const PRECACHE_URLS = [
  './',
  './index.html',
  './food_safety_exam_vol1.html',
  './food_safety_exam_vol2.html',
  './food_safety_exam_vol3.html',
  './food_safety_exam_vol4.html',
  './food_safety_exam_vol5.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-180.png',
  './icons/icon-192-maskable.png',
  './icons/icon-512-maskable.png'
];

/* インストール時：プリキャッシュ */
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      /* 個別に addAll するとどれか一つでも失敗するとすべて失敗するので、
         1件ずつ try して可能な限りキャッシュする */
      return Promise.all(
        PRECACHE_URLS.map((url) =>
          cache.add(url).catch((err) => {
            console.warn('[SW] precache miss:', url, err);
          })
        )
      );
    }).then(() => self.skipWaiting())
  );
});

/* 有効化時：古いキャッシュを削除 */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k.startsWith('food-safety-exam-') && k !== CACHE_NAME)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

/* リクエスト処理 */
self.addEventListener('fetch', (event) => {
  const req = event.request;

  /* GET 以外はキャッシュしない */
  if (req.method !== 'GET') return;

  /* 同一オリジン外は通常通り */
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  const isHTML =
    req.mode === 'navigate' ||
    (req.headers.get('accept') || '').includes('text/html');

  if (isHTML) {
    /* HTML: Network First */
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(() =>
          caches.match(req).then(
            (cached) => cached || caches.match('./index.html')
          )
        )
    );
    return;
  }

  /* その他: Cache First */
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        /* 200 OK のみキャッシュ */
        if (res && res.status === 200 && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
        }
        return res;
      }).catch(() => cached);
    })
  );
});

/* 手動アップデート用メッセージ */
self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});
