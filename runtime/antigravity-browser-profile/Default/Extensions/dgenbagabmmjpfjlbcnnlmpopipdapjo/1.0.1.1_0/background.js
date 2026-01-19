var he = Object.defineProperty;
var me = (n, t, e) => t in n ? he(n, t, { enumerable: !0, configurable: !0, writable: !0, value: e }) : n[t] = e;
var z = (n, t, e) => me(n, typeof t != "symbol" ? t + "" : t, e);
var Z = { exports: {} }, fe = Z.exports, ne;
function pe() {
  return ne || (ne = 1, function(n, t) {
    (function(e, r) {
      r(n);
    })(typeof globalThis < "u" ? globalThis : typeof self < "u" ? self : fe, function(e) {
      if (!(globalThis.chrome && globalThis.chrome.runtime && globalThis.chrome.runtime.id))
        throw new Error("This script should only be loaded in a browser extension.");
      if (globalThis.browser && globalThis.browser.runtime && globalThis.browser.runtime.id)
        e.exports = globalThis.browser;
      else {
        const r = "The message port closed before a response was received.", s = (o) => {
          const a = {
            alarms: {
              clear: {
                minArgs: 0,
                maxArgs: 1
              },
              clearAll: {
                minArgs: 0,
                maxArgs: 0
              },
              get: {
                minArgs: 0,
                maxArgs: 1
              },
              getAll: {
                minArgs: 0,
                maxArgs: 0
              }
            },
            bookmarks: {
              create: {
                minArgs: 1,
                maxArgs: 1
              },
              get: {
                minArgs: 1,
                maxArgs: 1
              },
              getChildren: {
                minArgs: 1,
                maxArgs: 1
              },
              getRecent: {
                minArgs: 1,
                maxArgs: 1
              },
              getSubTree: {
                minArgs: 1,
                maxArgs: 1
              },
              getTree: {
                minArgs: 0,
                maxArgs: 0
              },
              move: {
                minArgs: 2,
                maxArgs: 2
              },
              remove: {
                minArgs: 1,
                maxArgs: 1
              },
              removeTree: {
                minArgs: 1,
                maxArgs: 1
              },
              search: {
                minArgs: 1,
                maxArgs: 1
              },
              update: {
                minArgs: 2,
                maxArgs: 2
              }
            },
            browserAction: {
              disable: {
                minArgs: 0,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              enable: {
                minArgs: 0,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              getBadgeBackgroundColor: {
                minArgs: 1,
                maxArgs: 1
              },
              getBadgeText: {
                minArgs: 1,
                maxArgs: 1
              },
              getPopup: {
                minArgs: 1,
                maxArgs: 1
              },
              getTitle: {
                minArgs: 1,
                maxArgs: 1
              },
              openPopup: {
                minArgs: 0,
                maxArgs: 0
              },
              setBadgeBackgroundColor: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              setBadgeText: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              setIcon: {
                minArgs: 1,
                maxArgs: 1
              },
              setPopup: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              setTitle: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              }
            },
            browsingData: {
              remove: {
                minArgs: 2,
                maxArgs: 2
              },
              removeCache: {
                minArgs: 1,
                maxArgs: 1
              },
              removeCookies: {
                minArgs: 1,
                maxArgs: 1
              },
              removeDownloads: {
                minArgs: 1,
                maxArgs: 1
              },
              removeFormData: {
                minArgs: 1,
                maxArgs: 1
              },
              removeHistory: {
                minArgs: 1,
                maxArgs: 1
              },
              removeLocalStorage: {
                minArgs: 1,
                maxArgs: 1
              },
              removePasswords: {
                minArgs: 1,
                maxArgs: 1
              },
              removePluginData: {
                minArgs: 1,
                maxArgs: 1
              },
              settings: {
                minArgs: 0,
                maxArgs: 0
              }
            },
            commands: {
              getAll: {
                minArgs: 0,
                maxArgs: 0
              }
            },
            contextMenus: {
              remove: {
                minArgs: 1,
                maxArgs: 1
              },
              removeAll: {
                minArgs: 0,
                maxArgs: 0
              },
              update: {
                minArgs: 2,
                maxArgs: 2
              }
            },
            cookies: {
              get: {
                minArgs: 1,
                maxArgs: 1
              },
              getAll: {
                minArgs: 1,
                maxArgs: 1
              },
              getAllCookieStores: {
                minArgs: 0,
                maxArgs: 0
              },
              remove: {
                minArgs: 1,
                maxArgs: 1
              },
              set: {
                minArgs: 1,
                maxArgs: 1
              }
            },
            devtools: {
              inspectedWindow: {
                eval: {
                  minArgs: 1,
                  maxArgs: 2,
                  singleCallbackArg: !1
                }
              },
              panels: {
                create: {
                  minArgs: 3,
                  maxArgs: 3,
                  singleCallbackArg: !0
                },
                elements: {
                  createSidebarPane: {
                    minArgs: 1,
                    maxArgs: 1
                  }
                }
              }
            },
            downloads: {
              cancel: {
                minArgs: 1,
                maxArgs: 1
              },
              download: {
                minArgs: 1,
                maxArgs: 1
              },
              erase: {
                minArgs: 1,
                maxArgs: 1
              },
              getFileIcon: {
                minArgs: 1,
                maxArgs: 2
              },
              open: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              pause: {
                minArgs: 1,
                maxArgs: 1
              },
              removeFile: {
                minArgs: 1,
                maxArgs: 1
              },
              resume: {
                minArgs: 1,
                maxArgs: 1
              },
              search: {
                minArgs: 1,
                maxArgs: 1
              },
              show: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              }
            },
            extension: {
              isAllowedFileSchemeAccess: {
                minArgs: 0,
                maxArgs: 0
              },
              isAllowedIncognitoAccess: {
                minArgs: 0,
                maxArgs: 0
              }
            },
            history: {
              addUrl: {
                minArgs: 1,
                maxArgs: 1
              },
              deleteAll: {
                minArgs: 0,
                maxArgs: 0
              },
              deleteRange: {
                minArgs: 1,
                maxArgs: 1
              },
              deleteUrl: {
                minArgs: 1,
                maxArgs: 1
              },
              getVisits: {
                minArgs: 1,
                maxArgs: 1
              },
              search: {
                minArgs: 1,
                maxArgs: 1
              }
            },
            i18n: {
              detectLanguage: {
                minArgs: 1,
                maxArgs: 1
              },
              getAcceptLanguages: {
                minArgs: 0,
                maxArgs: 0
              }
            },
            identity: {
              launchWebAuthFlow: {
                minArgs: 1,
                maxArgs: 1
              }
            },
            idle: {
              queryState: {
                minArgs: 1,
                maxArgs: 1
              }
            },
            management: {
              get: {
                minArgs: 1,
                maxArgs: 1
              },
              getAll: {
                minArgs: 0,
                maxArgs: 0
              },
              getSelf: {
                minArgs: 0,
                maxArgs: 0
              },
              setEnabled: {
                minArgs: 2,
                maxArgs: 2
              },
              uninstallSelf: {
                minArgs: 0,
                maxArgs: 1
              }
            },
            notifications: {
              clear: {
                minArgs: 1,
                maxArgs: 1
              },
              create: {
                minArgs: 1,
                maxArgs: 2
              },
              getAll: {
                minArgs: 0,
                maxArgs: 0
              },
              getPermissionLevel: {
                minArgs: 0,
                maxArgs: 0
              },
              update: {
                minArgs: 2,
                maxArgs: 2
              }
            },
            pageAction: {
              getPopup: {
                minArgs: 1,
                maxArgs: 1
              },
              getTitle: {
                minArgs: 1,
                maxArgs: 1
              },
              hide: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              setIcon: {
                minArgs: 1,
                maxArgs: 1
              },
              setPopup: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              setTitle: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              },
              show: {
                minArgs: 1,
                maxArgs: 1,
                fallbackToNoCallback: !0
              }
            },
            permissions: {
              contains: {
                minArgs: 1,
                maxArgs: 1
              },
              getAll: {
                minArgs: 0,
                maxArgs: 0
              },
              remove: {
                minArgs: 1,
                maxArgs: 1
              },
              request: {
                minArgs: 1,
                maxArgs: 1
              }
            },
            runtime: {
              getBackgroundPage: {
                minArgs: 0,
                maxArgs: 0
              },
              getPlatformInfo: {
                minArgs: 0,
                maxArgs: 0
              },
              openOptionsPage: {
                minArgs: 0,
                maxArgs: 0
              },
              requestUpdateCheck: {
                minArgs: 0,
                maxArgs: 0
              },
              sendMessage: {
                minArgs: 1,
                maxArgs: 3
              },
              sendNativeMessage: {
                minArgs: 2,
                maxArgs: 2
              },
              setUninstallURL: {
                minArgs: 1,
                maxArgs: 1
              }
            },
            sessions: {
              getDevices: {
                minArgs: 0,
                maxArgs: 1
              },
              getRecentlyClosed: {
                minArgs: 0,
                maxArgs: 1
              },
              restore: {
                minArgs: 0,
                maxArgs: 1
              }
            },
            storage: {
              local: {
                clear: {
                  minArgs: 0,
                  maxArgs: 0
                },
                get: {
                  minArgs: 0,
                  maxArgs: 1
                },
                getBytesInUse: {
                  minArgs: 0,
                  maxArgs: 1
                },
                remove: {
                  minArgs: 1,
                  maxArgs: 1
                },
                set: {
                  minArgs: 1,
                  maxArgs: 1
                }
              },
              managed: {
                get: {
                  minArgs: 0,
                  maxArgs: 1
                },
                getBytesInUse: {
                  minArgs: 0,
                  maxArgs: 1
                }
              },
              sync: {
                clear: {
                  minArgs: 0,
                  maxArgs: 0
                },
                get: {
                  minArgs: 0,
                  maxArgs: 1
                },
                getBytesInUse: {
                  minArgs: 0,
                  maxArgs: 1
                },
                remove: {
                  minArgs: 1,
                  maxArgs: 1
                },
                set: {
                  minArgs: 1,
                  maxArgs: 1
                }
              }
            },
            tabs: {
              captureVisibleTab: {
                minArgs: 0,
                maxArgs: 2
              },
              create: {
                minArgs: 1,
                maxArgs: 1
              },
              detectLanguage: {
                minArgs: 0,
                maxArgs: 1
              },
              discard: {
                minArgs: 0,
                maxArgs: 1
              },
              duplicate: {
                minArgs: 1,
                maxArgs: 1
              },
              executeScript: {
                minArgs: 1,
                maxArgs: 2
              },
              get: {
                minArgs: 1,
                maxArgs: 1
              },
              getCurrent: {
                minArgs: 0,
                maxArgs: 0
              },
              getZoom: {
                minArgs: 0,
                maxArgs: 1
              },
              getZoomSettings: {
                minArgs: 0,
                maxArgs: 1
              },
              goBack: {
                minArgs: 0,
                maxArgs: 1
              },
              goForward: {
                minArgs: 0,
                maxArgs: 1
              },
              highlight: {
                minArgs: 1,
                maxArgs: 1
              },
              insertCSS: {
                minArgs: 1,
                maxArgs: 2
              },
              move: {
                minArgs: 2,
                maxArgs: 2
              },
              query: {
                minArgs: 1,
                maxArgs: 1
              },
              reload: {
                minArgs: 0,
                maxArgs: 2
              },
              remove: {
                minArgs: 1,
                maxArgs: 1
              },
              removeCSS: {
                minArgs: 1,
                maxArgs: 2
              },
              sendMessage: {
                minArgs: 2,
                maxArgs: 3
              },
              setZoom: {
                minArgs: 1,
                maxArgs: 2
              },
              setZoomSettings: {
                minArgs: 1,
                maxArgs: 2
              },
              update: {
                minArgs: 1,
                maxArgs: 2
              }
            },
            topSites: {
              get: {
                minArgs: 0,
                maxArgs: 0
              }
            },
            webNavigation: {
              getAllFrames: {
                minArgs: 1,
                maxArgs: 1
              },
              getFrame: {
                minArgs: 1,
                maxArgs: 1
              }
            },
            webRequest: {
              handlerBehaviorChanged: {
                minArgs: 0,
                maxArgs: 0
              }
            },
            windows: {
              create: {
                minArgs: 0,
                maxArgs: 1
              },
              get: {
                minArgs: 1,
                maxArgs: 2
              },
              getAll: {
                minArgs: 0,
                maxArgs: 1
              },
              getCurrent: {
                minArgs: 0,
                maxArgs: 1
              },
              getLastFocused: {
                minArgs: 0,
                maxArgs: 1
              },
              remove: {
                minArgs: 1,
                maxArgs: 1
              },
              update: {
                minArgs: 2,
                maxArgs: 2
              }
            }
          };
          if (Object.keys(a).length === 0)
            throw new Error("api-metadata.json has not been included in browser-polyfill");
          class i extends WeakMap {
            constructor(k, y = void 0) {
              super(y), this.createItem = k;
            }
            get(k) {
              return this.has(k) || this.set(k, this.createItem(k)), super.get(k);
            }
          }
          const l = (w) => w && typeof w == "object" && typeof w.then == "function", c = (w, k) => (...y) => {
            o.runtime.lastError ? w.reject(new Error(o.runtime.lastError.message)) : k.singleCallbackArg || y.length <= 1 && k.singleCallbackArg !== !1 ? w.resolve(y[0]) : w.resolve(y);
          }, d = (w) => w == 1 ? "argument" : "arguments", u = (w, k) => function(x, ...U) {
            if (U.length < k.minArgs)
              throw new Error(`Expected at least ${k.minArgs} ${d(k.minArgs)} for ${w}(), got ${U.length}`);
            if (U.length > k.maxArgs)
              throw new Error(`Expected at most ${k.maxArgs} ${d(k.maxArgs)} for ${w}(), got ${U.length}`);
            return new Promise((O, R) => {
              if (k.fallbackToNoCallback)
                try {
                  x[w](...U, c({
                    resolve: O,
                    reject: R
                  }, k));
                } catch {
                  x[w](...U), k.fallbackToNoCallback = !1, k.noCallback = !0, O();
                }
              else k.noCallback ? (x[w](...U), O()) : x[w](...U, c({
                resolve: O,
                reject: R
              }, k));
            });
          }, p = (w, k, y) => new Proxy(k, {
            apply(x, U, O) {
              return y.call(U, w, ...O);
            }
          });
          let b = Function.call.bind(Object.prototype.hasOwnProperty);
          const m = (w, k = {}, y = {}) => {
            let x = /* @__PURE__ */ Object.create(null), U = {
              has(R, L) {
                return L in w || L in x;
              },
              get(R, L, $) {
                if (L in x)
                  return x[L];
                if (!(L in w))
                  return;
                let C = w[L];
                if (typeof C == "function")
                  if (typeof k[L] == "function")
                    C = p(w, w[L], k[L]);
                  else if (b(y, L)) {
                    let B = u(L, y[L]);
                    C = p(w, w[L], B);
                  } else
                    C = C.bind(w);
                else if (typeof C == "object" && C !== null && (b(k, L) || b(y, L)))
                  C = m(C, k[L], y[L]);
                else if (b(y, "*"))
                  C = m(C, k[L], y["*"]);
                else
                  return Object.defineProperty(x, L, {
                    configurable: !0,
                    enumerable: !0,
                    get() {
                      return w[L];
                    },
                    set(B) {
                      w[L] = B;
                    }
                  }), C;
                return x[L] = C, C;
              },
              set(R, L, $, C) {
                return L in x ? x[L] = $ : w[L] = $, !0;
              },
              defineProperty(R, L, $) {
                return Reflect.defineProperty(x, L, $);
              },
              deleteProperty(R, L) {
                return Reflect.deleteProperty(x, L);
              }
            }, O = Object.create(w);
            return new Proxy(O, U);
          }, f = (w) => ({
            addListener(k, y, ...x) {
              k.addListener(w.get(y), ...x);
            },
            hasListener(k, y) {
              return k.hasListener(w.get(y));
            },
            removeListener(k, y) {
              k.removeListener(w.get(y));
            }
          }), A = new i((w) => typeof w != "function" ? w : function(y) {
            const x = m(y, {}, {
              getContent: {
                minArgs: 0,
                maxArgs: 0
              }
            });
            w(x);
          }), P = new i((w) => typeof w != "function" ? w : function(y, x, U) {
            let O = !1, R, L = new Promise((G) => {
              R = function(_) {
                O = !0, G(_);
              };
            }), $;
            try {
              $ = w(y, x, R);
            } catch (G) {
              $ = Promise.reject(G);
            }
            const C = $ !== !0 && l($);
            if ($ !== !0 && !C && !O)
              return !1;
            const B = (G) => {
              G.then((_) => {
                U(_);
              }, (_) => {
                let X;
                _ && (_ instanceof Error || typeof _.message == "string") ? X = _.message : X = "An unexpected error occurred", U({
                  __mozWebExtensionPolyfillReject__: !0,
                  message: X
                });
              }).catch((_) => {
              });
            };
            return B(C ? $ : L), !0;
          }), N = ({
            reject: w,
            resolve: k
          }, y) => {
            o.runtime.lastError ? o.runtime.lastError.message === r ? k() : w(new Error(o.runtime.lastError.message)) : y && y.__mozWebExtensionPolyfillReject__ ? w(new Error(y.message)) : k(y);
          }, I = (w, k, y, ...x) => {
            if (x.length < k.minArgs)
              throw new Error(`Expected at least ${k.minArgs} ${d(k.minArgs)} for ${w}(), got ${x.length}`);
            if (x.length > k.maxArgs)
              throw new Error(`Expected at most ${k.maxArgs} ${d(k.maxArgs)} for ${w}(), got ${x.length}`);
            return new Promise((U, O) => {
              const R = N.bind(null, {
                resolve: U,
                reject: O
              });
              x.push(R), y.sendMessage(...x);
            });
          }, v = {
            devtools: {
              network: {
                onRequestFinished: f(A)
              }
            },
            runtime: {
              onMessage: f(P),
              onMessageExternal: f(P),
              sendMessage: I.bind(null, "sendMessage", {
                minArgs: 1,
                maxArgs: 3
              })
            },
            tabs: {
              sendMessage: I.bind(null, "sendMessage", {
                minArgs: 2,
                maxArgs: 3
              })
            }
          }, q = {
            clear: {
              minArgs: 1,
              maxArgs: 1
            },
            get: {
              minArgs: 1,
              maxArgs: 1
            },
            set: {
              minArgs: 1,
              maxArgs: 1
            }
          };
          return a.privacy = {
            network: {
              "*": q
            },
            services: {
              "*": q
            },
            websites: {
              "*": q
            }
          }, m(o, v, a);
        };
        e.exports = s(chrome);
      }
    });
  }(Z)), Z.exports;
}
pe();
class we {
  constructor(t = 1e5, e = 3, r = 1e3) {
    this.defaultTimeout = t, this.defaultMaxRetries = e, this.defaultRetryDelay = r;
  }
  async executeWithTimeout(t, e = this.defaultTimeout) {
    const r = new Promise(
      (s, o) => setTimeout(() => o(new Error("API request timeout")), e)
    );
    return Promise.race([t, r]);
  }
  async executeWithRetry(t, e = {}) {
    const {
      maxRetries: r = this.defaultMaxRetries,
      timeoutMs: s = this.defaultTimeout,
      retryDelay: o = this.defaultRetryDelay,
      shouldRetry: a = (c) => !c.message.includes("authorization") && !c.message.includes("sign in") && !c.message.includes("Please sign in"),
      cancelToken: i
    } = e;
    let l;
    for (let c = 1; c <= r; c++)
      try {
        if (i && i.isCancelled())
          throw new Error("Operation was cancelled");
        return await this.executeWithTimeout(t(), s);
      } catch (d) {
        if (l = d instanceof Error ? d : new Error("Unknown error"), i && i.isCancelled())
          throw new Error("Operation was cancelled");
        if (!a(l) || c === r)
          throw l;
        const u = o * c;
        await new Promise((p) => setTimeout(p, u));
      }
    throw l;
  }
}
function M(n) {
  try {
    const t = n.split(`
`);
    let e = "";
    for (let o = 2; o < t.length; o++) {
      const a = t[o].trim();
      if (a.startsWith("[")) {
        e = a;
        break;
      }
    }
    if (!e)
      throw new Error("No JSON line found in response");
    const r = JSON.parse(e), s = [];
    for (const o of r) {
      if (o[0] !== "wrb.fr")
        continue;
      const a = o[6] === "generic" ? 1 : parseInt(o[6], 10), i = o[1], l = JSON.parse(o[2]);
      s.push({ index: a, rpcId: i, data: l });
    }
    return s;
  } catch {
    return null;
  }
}
function ke(n) {
  try {
    const t = n[1], e = [];
    for (let r = 0; r < (t == null ? void 0 : t.length); r++) {
      const s = t[r];
      if (!s || !Array.isArray(s) || s.length < 3)
        continue;
      const o = s[0] && s[0][0] ? s[0][0] : `link_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, a = s[1] || "Untitled";
      let i = "", l = "unknown";
      const c = {};
      if (s[2] && Array.isArray(s[2])) {
        const d = s[2][4];
        switch (d) {
          case 1:
            l = "google-docs", s[2][0] && Array.isArray(s[2][0]) && (i = `https://docs.google.com/document/d/${s[2][0][0]}`, c.docId = s[2][0][0]);
            break;
          case 2:
            l = "google-slides", i = "google-presentation://", c.type = "Google Slides";
            break;
          case 4:
            l = "pasted-text", i = "text://pasted-content", typeof s[2][1] == "number" && (c.size = s[2][1], c.sizeFormatted = `${Math.round(s[2][1] / 1024 * 10) / 10} KB`);
            break;
          case 5:
            if (l = "web-page", s[2][7] && Array.isArray(s[2][7])) {
              i = s[2][7][0];
              try {
                c.origin = new URL(i).hostname;
              } catch {
              }
            }
            break;
          case 9:
            if (l = "youtube", c.isYouTube = !0, s[2][5] && Array.isArray(s[2][5]))
              i = s[2][5][0], c.videoId = s[2][5][1], c.channel = s[2][5][2];
            else if (s[2][9] && Array.isArray(s[2][9]))
              i = s[2][9][0], c.videoId = s[2][9][1], c.channel = s[2][9][2];
            else if (a && a.includes("youtube.com/shorts/")) {
              i = a, c.isShort = !0;
              const u = i.match(/\/shorts\/([^/?&]+)/);
              u && u[1] && (c.videoId = u[1]);
            }
            break;
          default:
            if (l = `type-${d || "unknown"}`, s[2][7] && Array.isArray(s[2][7]) ? i = s[2][7][0] : s[2][5] && Array.isArray(s[2][5]) ? i = s[2][5][0] : s[2][9] && Array.isArray(s[2][9]) && (i = s[2][9][0]), a && typeof a == "string" && a.includes("youtube.com")) {
              l = "youtube", c.isYouTube = !0, i || (i = a);
              const u = i.match(/(?:v=|\/v\/|\/embed\/|\/watch\?v=|\/shorts\/)([^&?/]+)/);
              u && u[1] && (c.videoId = u[1]);
            }
        }
      }
      !i && l !== "unknown" && (i = `notebooklm://${l}/${o}`), e.push({
        id: o,
        sourceId: o,
        url: i || `notebooklm://resource/${o}`,
        title: a,
        contentType: l,
        sourceInfo: c
      });
    }
    return e;
  } catch {
    return [];
  }
}
function be(n, t) {
  try {
    const e = t.find((r) => r.id === n);
    if (!e)
      throw new Error("Notebook not found in cache");
    return {
      id: e.id,
      links: e.links || []
    };
  } catch (e) {
    throw e;
  }
}
async function Ae(n) {
  var i, l, c, d, u, p, b, m, f, A, P, N, I, v, q, w, k;
  const t = await fetch(n, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
  });
  if (!t.ok)
    throw new Error(`Failed to load playlist. HTTP status: ${t.status}`);
  const r = (await t.text()).match(/var ytInitialData = ({.+?});/);
  if (!r)
    throw new Error("Failed to find playlist data on page");
  let s;
  try {
    s = JSON.parse(r[1]);
  } catch (y) {
    throw new Error("Failed to parse playlist data", { cause: y });
  }
  const o = (I = (N = (P = (A = (f = (m = (b = (p = (u = (d = (c = (l = (i = s == null ? void 0 : s.contents) == null ? void 0 : i.twoColumnBrowseResultsRenderer) == null ? void 0 : l.tabs) == null ? void 0 : c[0]) == null ? void 0 : d.tabRenderer) == null ? void 0 : u.content) == null ? void 0 : p.sectionListRenderer) == null ? void 0 : b.contents) == null ? void 0 : m[0]) == null ? void 0 : f.itemSectionRenderer) == null ? void 0 : A.contents) == null ? void 0 : P[0]) == null ? void 0 : N.playlistVideoListRenderer) == null ? void 0 : I.contents;
  if (!o || !Array.isArray(o))
    throw new Error("Failed to find video list in playlist. This might be a private playlist or Mix playlist.");
  const a = [];
  for (const y of o) {
    const x = y == null ? void 0 : y.playlistVideoRenderer;
    if (!x || !x.videoId)
      continue;
    const U = x.videoId, O = ((w = (q = (v = x.title) == null ? void 0 : v.runs) == null ? void 0 : q[0]) == null ? void 0 : w.text) || ((k = x.title) == null ? void 0 : k.simpleText) || `Video ${U}`;
    if (x.isPlayable === !1)
      continue;
    const R = `https://www.youtube.com/watch?v=${U}`;
    a.push({
      url: R,
      title: O,
      videoId: U
    });
  }
  return a;
}
function ae(n) {
  try {
    return new URL(n).pathname === "/playlist";
  } catch {
    return !1;
  }
}
class H extends Error {
  constructor(e) {
    super(e);
    z(this, "isAuthenticated", !1);
    this.name = "AuthenticationError";
  }
}
class ye {
  constructor() {
    z(this, "cachedTokens", null);
    z(this, "lastTokenUpdate", 0);
    z(this, "TOKEN_VALIDITY_TIME", 20 * 60 * 1e3);
    z(this, "retryService", new we());
  }
  // === API METHODS WITH CONTRACTS ===
  /**
   * Adds multiple sources in batch using unified method
   * @returns Array of added sources with their IDs from server
   */
  async addSources(t, e) {
    return this.retryService.executeWithRetry(async () => {
      const r = await this.ensureValidTokens();
      if (!t)
        throw new Error("Invalid notebook ID in request");
      if (!e || e.length === 0)
        throw new Error("No sources provided");
      const s = e.map((m) => typeof m == "string" ? m.includes("youtube.com") ? { youtubeUrl: m } : { url: m } : m), o = s.map((m) => {
        let f = m.youtubeUrl || m.url || "";
        return f.includes("www.youtube.com/shorts/") && (f = f.replace("/shorts/", "/watch?v=")), m.youtubeUrl || f.includes("youtube.com") ? [null, null, null, null, null, null, null, [f], null, null, 1] : [null, null, [f], null, null, null, null, null, null, null, 1];
      }), a = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      a.searchParams.append("rpcids", "izAoDd"), a.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), a.searchParams.append("bl", r.bl);
      const i = [1, null, null, null, null, null, null, null, null, null, [1]], l = new URLSearchParams();
      l.append("at", r.at), l.append(
        "f.req",
        JSON.stringify([[["izAoDd", JSON.stringify([o, t, [2], i]), null, "generic"]]])
      );
      const c = await fetch(a.toString(), {
        method: "POST",
        headers: {
          "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
          "x-same-domain": "1"
        },
        body: l,
        credentials: "include"
      });
      if (!c.ok)
        throw new Error(`Error adding sources. Status: ${c.status}`);
      const d = await c.text(), u = M(d);
      if (!u || !u[0] || !u[0].data)
        throw new Error("Invalid response from NotebookLM when adding sources");
      const b = u[0].data.map((m, f) => {
        var I, v;
        const A = (I = m[0]) == null ? void 0 : I[0], P = (v = m[0]) == null ? void 0 : v[1], N = !!A;
        return {
          sourceId: A || `failed_source_${f}`,
          url: s[f].url || s[f].youtubeUrl,
          title: P || "Unknown",
          success: N
        };
      });
      return {
        success: !0,
        data: {
          addedSources: b,
          notebookId: t,
          totalAdded: b.filter((m) => m.success).length,
          totalFailed: b.filter((m) => !m.success).length
        }
      };
    }).catch((r) => ({
      success: !1,
      error: r instanceof Error ? r.message : "Unknown error"
    }));
  }
  /**
   * Adds multiple files in batch using unified method
   * @param notebookId - The ID of the notebook to add files to
   * @param files - Array of files to add (can be BatchFile objects or file names as strings)
   * @returns Array of added files with their IDs from server
   */
  async addFiles(t, e) {
    return this.retryService.executeWithRetry(async () => {
      const r = await this.ensureValidTokens();
      if (!t)
        throw new Error("Invalid notebook ID in request");
      if (!e || e.length === 0)
        throw new Error("No files provided");
      const s = e.map((f) => typeof f == "string" ? { fileName: f } : f), o = s.map((f) => [f.fileName]), a = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      a.searchParams.append("rpcids", "o4cbdc"), a.searchParams.append("source-path", `/notebook/${t}`), a.searchParams.append("bl", r.bl), a.searchParams.append("f.sid", String(Math.floor(Math.random() * 9e9) + 1e9)), a.searchParams.append("hl", "en"), a.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), a.searchParams.append("rt", "c");
      const i = [1, null, null, null, null, null, null, null, null, null, [1]], l = new URLSearchParams();
      l.append("at", r.at), l.append(
        "f.req",
        JSON.stringify([[["o4cbdc", JSON.stringify([o, t, [2], i]), null, "generic"]]])
      );
      const c = await fetch(a.toString(), {
        method: "POST",
        headers: {
          "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
          "x-same-domain": "1"
        },
        body: l,
        credentials: "include"
      });
      if (!c.ok)
        throw new Error(`Error adding files. Status: ${c.status}`);
      const d = await c.text(), u = M(d);
      if (!u || !u[0] || !u[0].data)
        throw new Error("Invalid response from NotebookLM when adding files");
      const m = u[0].data[0].map((f, A) => {
        var v;
        const P = (v = f[0]) == null ? void 0 : v[0], N = f[1], I = !!P;
        return {
          fileId: P || `failed_file_${A}`,
          fileName: N || s[A].fileName,
          success: I
        };
      });
      return {
        success: !0,
        data: {
          addedFiles: m,
          notebookId: t,
          totalAdded: m.filter((f) => f.success).length,
          totalFailed: m.filter((f) => !f.success).length
        }
      };
    }).catch((r) => ({
      success: !1,
      error: r instanceof Error ? r.message : "Unknown error"
    }));
  }
  async createNotebook(t, e) {
    return this.retryService.executeWithRetry(async () => {
      const r = await this.ensureValidTokens(), s = "CCqFvf", o = Math.floor(Math.random() * 9e5) + 1e5, a = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      a.searchParams.append("rpcids", s), a.searchParams.append("_reqid", String(o)), a.searchParams.append("bl", r.bl);
      const i = new URLSearchParams();
      i.append("at", r.at), i.append("f.req", JSON.stringify([[["CCqFvf", JSON.stringify([t, e]), null, "generic"]]]));
      const l = await fetch(a.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: i,
        credentials: "include"
      });
      if (!l.ok)
        throw new Error(`Error creating notebook. Status: ${l.status}`);
      const c = await l.text(), d = M(c);
      if (!d || !d[0] || !d[0].data)
        throw new Error("Invalid response from NotebookLM");
      const u = d[0].data[2];
      return {
        success: !0,
        data: {
          notebookId: u,
          notebook: {
            id: u,
            title: t,
            emoji: e,
            links: []
          }
        }
      };
    }).catch((r) => ({
      success: !1,
      error: r instanceof Error ? r.message : "Unknown error"
    }));
  }
  /**
   * Retrieves list of notebooks
   * @returns List of notebooks with their sources/links
   */
  async getNotebooks() {
    return this.retryService.executeWithRetry(async () => {
      const t = await this.ensureValidTokens(), e = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      e.searchParams.append("rpcids", "wXbhsf"), e.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), e.searchParams.append("bl", t.bl);
      const r = new URLSearchParams();
      r.append("at", t.at), r.append("f.req", JSON.stringify([[["wXbhsf", JSON.stringify([null, 500]), null, "generic"]]]));
      const s = await fetch(e.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: r,
        credentials: "include"
      });
      if (!s.ok)
        throw new Error(`Error getting notebook list. Status: ${s.status}`);
      const o = await s.text(), a = M(o);
      if (!a || !a[0] || !a[0].data)
        throw new Error("Invalid response from NotebookLM");
      return {
        success: !0,
        data: {
          notebooks: (a[0].data[0] || []).map((c) => {
            const d = c[2], u = c[0], p = c[3], b = ke(c) || [];
            return {
              id: d,
              title: u,
              emoji: p,
              links: b
            };
          })
        }
      };
    }).catch((t) => ({
      success: !1,
      error: t instanceof Error ? t.message : "Unknown error"
    }));
  }
  /**
   * Gets account information including language settings and other account data
   * @returns Full account data from server
   */
  async getAccount() {
    return this.retryService.executeWithRetry(async () => {
      let t = null;
      try {
        t = await this.ensureValidTokens();
      } catch {
        throw new H("User not authenticated - no Google account or not signed in to NotebookLM");
      }
      const e = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      e.searchParams.append("rpcids", "ZwVcOc"), e.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), e.searchParams.append("bl", t.bl);
      const r = new URLSearchParams();
      r.append("at", t.at), r.append("f.req", JSON.stringify([[["ZwVcOc", JSON.stringify([]), null, "generic"]]]));
      const s = await fetch(e.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: r,
        credentials: "include"
      });
      if (!s.ok)
        throw new Error(`Error getting account info. Status: ${s.status}`);
      const o = await s.text(), a = M(o);
      if (!a || !a[0] || !a[0].data)
        throw new Error("Invalid response from NotebookLM when getting account");
      const i = a[0].data[0], l = i[2], c = l && l.length > 0 ? l[l.length - 1][0] : "en", d = i[5] === "true";
      return {
        success: !0,
        data: {
          language: c,
          isAuthenticated: d,
          // Return full account data for potential future use
          rawAccountData: i
        }
      };
    }).catch((t) => ({
      success: !1,
      error: t instanceof Error ? t : "Unknown error"
    }));
  }
  /**
   * Adds a text source to notebook using unified method
   * @returns Source ID from server response
   */
  async addTextSource(t, e) {
    return this.retryService.executeWithRetry(async () => {
      if (!e.content)
        throw new Error("Text content is required");
      const r = await this.ensureValidTokens(), s = [
        null,
        [e.title || "Pasted Text", e.content],
        null,
        2,
        null,
        null,
        null,
        null,
        null,
        null,
        1
      ], o = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      o.searchParams.append("rpcids", "izAoDd"), o.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), o.searchParams.append("bl", r.bl);
      const a = [1, null, null, null, null, null, null, null, null, null, [1]], i = new URLSearchParams();
      i.append("at", r.at), i.append(
        "f.req",
        JSON.stringify([[["izAoDd", JSON.stringify([[[s]], t, [2], a]), null, "generic"]]])
      );
      const l = await fetch(o.toString(), {
        method: "POST",
        headers: {
          "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
          "x-same-domain": "1"
        },
        body: i,
        credentials: "include"
      });
      if (!l.ok)
        throw new Error(`Error adding text source. Status: ${l.status}`);
      const c = await l.text(), d = M(c);
      if (!d || !d[0] || !d[0].data)
        throw new Error("Invalid response from NotebookLM when adding text source");
      const u = d[0].data[0], p = u[0][0], b = u[0][1] || e.title || "Pasted Text";
      return {
        success: !0,
        data: {
          sourceId: p,
          sourceTitle: b,
          notebookId: t,
          success: !0
        }
      };
    }).catch((r) => ({
      success: !1,
      error: r instanceof Error ? r.message : "Unknown error"
    }));
  }
  /**
   * Deletes a source from notebook
   * Server returns empty response, we return success status
   */
  async deleteSource(t) {
    return this.retryService.executeWithRetry(async () => {
      const e = await this.ensureValidTokens();
      if (!t)
        throw new Error("Invalid source ID in request");
      const r = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      r.searchParams.append("rpcids", "tGMBJ"), r.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), r.searchParams.append("bl", e.bl);
      const s = new URLSearchParams();
      s.append("at", e.at), s.append("f.req", JSON.stringify([[["tGMBJ", JSON.stringify([[[t]], [2]]), null, "generic"]]]));
      const o = await fetch(r.toString(), {
        method: "POST",
        headers: {
          "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
          "x-same-domain": "1"
        },
        body: s,
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error deleting source. Status: ${o.status}`);
      return {
        success: !0,
        data: {
          sourceId: t,
          success: !0
        }
      };
    }).catch((e) => ({
      success: !1,
      error: e instanceof Error ? e.message : "Unknown error"
    }));
  }
  /**
   * Deletes a notebook
   * Server returns empty response, we return success status
   */
  async deleteNotebook(t) {
    return this.retryService.executeWithRetry(async () => {
      const e = await this.ensureValidTokens();
      if (!t)
        throw new Error("Invalid notebook ID in request");
      const r = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      r.searchParams.append("rpcids", "WWINqb"), r.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), r.searchParams.append("bl", e.bl);
      const s = new URLSearchParams();
      s.append("at", e.at), s.append("f.req", JSON.stringify([[["WWINqb", JSON.stringify([[t], [2]]), null, "generic"]]]));
      const o = await fetch(r.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: s,
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error deleting notebook. Status: ${o.status}`);
      return {
        success: !0,
        data: {
          notebookId: t,
          success: !0
        }
      };
    }).catch((e) => ({
      success: !1,
      error: e instanceof Error ? e.message : "Unknown error"
    }));
  }
  // === CONTENT AND NOTES METHODS ===
  /**
   * Discovers sources based on query
   * @returns List of discovered sources with URLs and descriptions
   */
  async discoverSources(t, e) {
    return this.retryService.executeWithRetry(async () => {
      var b;
      const r = await this.ensureValidTokens(), s = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      s.searchParams.append("rpcids", "Es3dTe"), s.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), s.searchParams.append("bl", r.bl);
      const o = new URLSearchParams();
      o.append("at", r.at), o.append(
        "f.req",
        JSON.stringify([[["Es3dTe", JSON.stringify([[t, 1], null, 1, e]), null, "generic"]]])
      );
      const a = await fetch(s.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: o,
        credentials: "include"
      });
      if (!a.ok)
        throw new Error(`Error discovering sources. Status: ${a.status}`);
      const i = await a.text(), l = M(i);
      if (!l || !l[0] || !l[0].data)
        throw new Error("Invalid response from NotebookLM when discovering sources");
      const c = l[0].data[0] || [], d = l[0].data[1] || "", u = ((b = l[0].data[2]) == null ? void 0 : b[0]) || "";
      return {
        success: !0,
        data: {
          sources: c.map((m) => ({
            url: m[0],
            title: m[1],
            description: m[2],
            relevance: m[3] || 0
          })),
          summary: d,
          discoveryId: u
        }
      };
    }).catch((r) => ({
      success: !1,
      error: r instanceof Error ? r.message : "Unknown error"
    }));
  }
  /**
   * Creates a new note in notebook using unified addSource method
   * @returns Note ID from server response
   */
  async createNote(t, e, r = "") {
    return this.retryService.executeWithRetry(async () => {
      const s = await this.ensureValidTokens(), o = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      o.searchParams.append("rpcids", "CYK0Xb"), o.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), o.searchParams.append("bl", s.bl);
      const a = new URLSearchParams();
      a.append("at", s.at), a.append(
        "f.req",
        JSON.stringify([[["CYK0Xb", JSON.stringify([t, r, [1], null, e]), null, "generic"]]])
      );
      const i = await fetch(o.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: a,
        credentials: "include"
      });
      if (!i.ok)
        throw new Error(`Error creating note. Status: ${i.status}`);
      const l = await i.text(), c = M(l);
      if (!c || !c[0] || !c[0].data)
        throw new Error("Invalid response from NotebookLM when creating note");
      const d = c[0].data[0], u = d[0], p = d[1], b = d[4];
      return {
        success: !0,
        data: {
          noteId: u,
          title: b,
          content: p,
          notebookId: t
        }
      };
    }).catch((s) => ({
      success: !1,
      error: s instanceof Error ? s.message : "Unknown error"
    }));
  }
  /**
   * Edits an existing note
   * NOTE: This uses a different endpoint 'cYAfTb' - not unified with addSource
   */
  async editNote(t, e, r, s) {
    return this.retryService.executeWithRetry(async () => {
      const o = await this.ensureValidTokens(), a = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      a.searchParams.append("rpcids", "cYAfTb"), a.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), a.searchParams.append("bl", o.bl);
      const i = new URLSearchParams();
      i.append("at", o.at), i.append(
        "f.req",
        JSON.stringify([
          [["cYAfTb", JSON.stringify([t, e, [[[r, s, [], 0]]]]), null, "generic"]]
        ])
      );
      const l = await fetch(a.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: i,
        credentials: "include"
      });
      if (!l.ok)
        throw new Error(`Error editing note. Status: ${l.status}`);
      const c = await l.text(), d = M(c);
      if (!d || !d[0] || !d[0].data)
        throw new Error("Invalid response from NotebookLM when editing note");
      const u = d[0].data[0];
      return {
        success: !0,
        data: {
          noteId: u[0],
          content: u[1],
          title: u[4],
          success: !0
        }
      };
    }).catch((o) => ({
      success: !1,
      error: o instanceof Error ? o.message : "Unknown error"
    }));
  }
  /**
   * Deletes a note from notebook
   * Server returns empty response, we return success status
   */
  async deleteNote(t, e) {
    return this.retryService.executeWithRetry(async () => {
      const r = await this.ensureValidTokens(), s = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      s.searchParams.append("rpcids", "AH0mwd"), s.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), s.searchParams.append("bl", r.bl);
      const o = new URLSearchParams();
      o.append("at", r.at), o.append(
        "f.req",
        JSON.stringify([[["AH0mwd", JSON.stringify([t, null, [e]]), null, "generic"]]])
      );
      const a = await fetch(s.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: o,
        credentials: "include"
      });
      if (!a.ok)
        throw new Error(`Error deleting note. Status: ${a.status}`);
      return {
        success: !0,
        data: {
          noteId: e,
          success: !0
        }
      };
    }).catch((r) => ({
      success: !1,
      error: r instanceof Error ? r.message : "Unknown error"
    }));
  }
  /**
   * Changes output language for AI responses
   * Server returns settings confirmation, we just confirm success
   */
  async changeOutputLanguage(t) {
    return this.retryService.executeWithRetry(async () => {
      const e = await this.ensureValidTokens(), r = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      r.searchParams.append("rpcids", "hT54vc"), r.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), r.searchParams.append("bl", e.bl);
      const s = new URLSearchParams();
      s.append("at", e.at), s.append(
        "f.req",
        JSON.stringify([
          [["hT54vc", JSON.stringify([[null, [[null, null, null, null, [t]]]]]), null, "generic"]]
        ])
      );
      const o = await fetch(r.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: s,
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error changing language. Status: ${o.status}`);
      return {
        success: !0,
        data: {
          language: t,
          success: !0
        }
      };
    }).catch((e) => ({
      success: !1,
      error: e instanceof Error ? e.message : "Unknown error"
    }));
  }
  /**
   * Gets transcript by source ID
   * @returns Transcript with properly typed suggested questions
   */
  async getTranscriptBySourceId(t) {
    return this.retryService.executeWithRetry(async () => {
      var u, p, b;
      const e = await this.ensureValidTokens(), r = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      r.searchParams.append("rpcids", "VfAZjd"), r.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), r.searchParams.append("bl", e.bl);
      const s = new URLSearchParams();
      s.append("at", e.at), s.append("f.req", JSON.stringify([[["VfAZjd", JSON.stringify([t, [2]]), null, "generic"]]]));
      const o = await fetch(r.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: s,
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error getting transcript. Status: ${o.status}`);
      const a = await o.text(), i = M(a);
      if (!i || !i[0] || !i[0].data)
        throw new Error("Invalid response from NotebookLM when getting transcript");
      const l = ((u = i[0].data[0]) == null ? void 0 : u[0]) || "", d = (((b = (p = i[0].data[0]) == null ? void 0 : p[1]) == null ? void 0 : b[0]) || []).map((m) => ({
        question: m[0],
        prompt: m[1]
      }));
      return {
        success: !0,
        data: {
          transcript: l,
          suggestedQuestions: d
        }
      };
    }).catch((e) => ({
      success: !1,
      error: e instanceof Error ? e.message : "Unknown error"
    }));
  }
  /**
   * Generates content based on sources (chat with sources)
   * @param sourceIds - Array of source IDs to use for generation
   * @param query - The user's question/prompt
   * @returns AI-generated response with properly typed citations
   */
  async generateContent(t, e) {
    return this.retryService.executeWithRetry(async () => {
      const r = await this.ensureValidTokens(), s = new URL(
        "https://notebooklm.google.com/_/LabsTailwindUi/data/google.internal.labs.tailwind.orchestration.v1.LabsTailwindOrchestrationService/GenerateFreeFormStreamed"
      );
      s.searchParams.append("bl", r.bl), s.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5));
      const o = t.map((m) => [[m]]), a = new URLSearchParams();
      a.append("at", r.at), a.append("f.req", JSON.stringify([null, `[${JSON.stringify(o)}, "${e}", null, [2]]`]));
      const i = await fetch(s.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: a,
        credentials: "include"
      });
      if (!i.ok)
        throw new Error(`Error generating content. Status: ${i.status}`);
      const c = (await i.text()).split(`
`);
      let d = "", u = [], p = "", b = "";
      for (const m of c)
        if (m.startsWith('[["wrb.fr"'))
          try {
            const f = JSON.parse(m);
            if (f[0] && f[0][2]) {
              const A = JSON.parse(f[0][2]);
              A[0] && (d = A[0]), A[5] && Array.isArray(A[5]) && (u = A[5]), A[2] && (p = A[2][0] || "", b = A[2][1] || "");
            }
          } catch {
          }
      return {
        success: !0,
        data: {
          content: d,
          citations: u,
          query: e,
          conversationId: p,
          messageId: b
        }
      };
    }).catch((r) => ({
      success: !1,
      error: r instanceof Error ? r.message : "Unknown error"
    }));
  }
  /**
   * Creates a report/document from sources
   * @returns Generated report content
   */
  async createReport(t, e, r) {
    return this.retryService.executeWithRetry(async () => {
      var m, f;
      const s = await this.ensureValidTokens(), o = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      o.searchParams.append("rpcids", "yyryJe"), o.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), o.searchParams.append("bl", s.bl);
      const a = t.map((A) => [[A]]), i = e.map((A) => [[A]]), l = new URLSearchParams();
      l.append("at", s.at), l.append(
        "f.req",
        JSON.stringify([
          [
            [
              "yyryJe",
              JSON.stringify([
                a.concat(i),
                null,
                null,
                null,
                null,
                [r, [["[CONTEXT]", ""]], ""],
                null,
                [2]
              ]),
              null,
              "generic"
            ]
          ]
        ])
      );
      const c = await fetch(o.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: l,
        credentials: "include"
      });
      if (!c.ok)
        throw new Error(`Error creating report. Status: ${c.status}`);
      const d = await c.text(), u = M(d);
      if (!u || !u[0] || !u[0].data)
        throw new Error("Invalid response from NotebookLM when creating report");
      const p = ((m = u[0].data[0]) == null ? void 0 : m[0]) || "", b = (f = u[0].data[0]) == null ? void 0 : f[2];
      return {
        success: !0,
        data: {
          content: p,
          type: r,
          metadata: b
        }
      };
    }).catch((s) => ({
      success: !1,
      error: s instanceof Error ? s.message : "Unknown error"
    }));
  }
  // === AUDIO/VIDEO METHODS ===
  /**
   * Creates basic audio overview for entire notebook
   * Uses AHyHrd endpoint for simple overview without customization
   * @returns Only status, no audio ID returned by this endpoint
   */
  async createAudioOverview(t, e = "en") {
    return this.retryService.executeWithRetry(async () => {
      var N, I;
      const r = await this.ensureValidTokens();
      if (!t)
        throw new Error("Invalid notebook ID in request");
      const s = await this.getNotebooks();
      if (!s.success || !s.data)
        throw new Error("Failed to get notebooks for audio overview");
      const o = s.data.notebooks.find((v) => v.id === t);
      if (!o)
        throw new Error("Notebook not found");
      const a = [], i = [];
      if (o.links && o.links.forEach((v) => {
        v.id && a.push(v.id);
      }), a.length === 0 && i.length === 0)
        throw new Error("Notebook has no sources or notes for audio overview");
      const l = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      l.searchParams.append("rpcids", "R7cb6c"), l.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), l.searchParams.append("bl", r.bl);
      const c = a.map((v) => [[v]]), d = i.map((v) => [[v]]), u = c.concat(d), p = new URLSearchParams();
      p.append("at", r.at), p.append(
        "f.req",
        JSON.stringify([
          [
            [
              "R7cb6c",
              JSON.stringify([
                [2],
                t,
                [
                  null,
                  null,
                  1,
                  u,
                  null,
                  null,
                  [null, [null, null, null, [...a, ...i], e]]
                ]
              ]),
              null,
              "generic"
            ]
          ]
        ])
      );
      const b = await fetch(l.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: p,
        credentials: "include"
      });
      if (!b.ok)
        throw new Error(`Error creating audio overview. Status: ${b.status}`);
      const m = await b.text(), f = M(m);
      if (!f || !f[0] || !f[0].data)
        throw new Error("Invalid response from NotebookLM when creating audio overview");
      const A = (N = f[0].data[0]) == null ? void 0 : N[0], P = ((I = f[0].data[0]) == null ? void 0 : I[1]) || "Audio Overview";
      return {
        success: !0,
        data: {
          audioId: A,
          title: P,
          notebookId: t,
          status: "initiated"
        }
      };
    }).catch((r) => ({
      success: !1,
      error: r instanceof Error ? r.message : "Unknown error"
    }));
  }
  /**
   * Creates customized audio overview with selected sources and format
   * Uses R7cb6c endpoint for customized generation with source selection
   * @param format 1 = shorter (~5 min), 3 = longer (~10 min)
   * @returns Audio ID and title from server
   */
  async createCustomAudioOverview(t, e, r, s, o = "en") {
    return this.retryService.executeWithRetry(async () => {
      var A, P;
      const a = await this.ensureValidTokens(), i = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      i.searchParams.append("rpcids", "R7cb6c"), i.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), i.searchParams.append("bl", a.bl);
      const l = e.map((N) => [[N]]), c = r.map((N) => [[N]]), d = new URLSearchParams();
      d.append("at", a.at), d.append(
        "f.req",
        JSON.stringify([
          [
            [
              "R7cb6c",
              JSON.stringify([
                [2],
                t,
                [
                  null,
                  null,
                  1,
                  l.concat(c),
                  null,
                  null,
                  [null, [null, s, null, [...e, ...r], o, null, 1]]
                ]
              ]),
              null,
              "generic"
            ]
          ]
        ])
      );
      const u = await fetch(i.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: d,
        credentials: "include"
      });
      if (!u.ok)
        throw new Error(`Error creating custom audio overview. Status: ${u.status}`);
      const p = await u.text(), b = M(p);
      if (!b || !b[0] || !b[0].data)
        throw new Error("Invalid response from NotebookLM when creating custom audio overview");
      const m = (A = b[0].data[0]) == null ? void 0 : A[0], f = (P = b[0].data[0]) == null ? void 0 : P[1];
      return {
        success: !0,
        data: {
          audioId: m,
          title: f,
          notebookId: t,
          status: "initiated"
        }
      };
    }).catch((a) => ({
      success: !1,
      error: a instanceof Error ? a.message : "Unknown error"
    }));
  }
  /**
   * Deletes audio overview
   * Server returns empty response, we return success status
   */
  async deleteAudioOverview(t) {
    return this.retryService.executeWithRetry(async () => {
      const e = await this.ensureValidTokens(), r = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      r.searchParams.append("rpcids", "V5N4be"), r.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), r.searchParams.append("bl", e.bl);
      const s = new URLSearchParams();
      s.append("at", e.at), s.append("f.req", JSON.stringify([[["V5N4be", JSON.stringify([[2], t]), null, "generic"]]]));
      const o = await fetch(r.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: s,
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error deleting audio overview. Status: ${o.status}`);
      return {
        success: !0,
        data: {
          audioId: t,
          success: !0
        }
      };
    }).catch((e) => ({
      success: !1,
      error: e instanceof Error ? e.message : "Unknown error"
    }));
  }
  /**
   * Creates video overview
   * @returns Video overview details
   */
  async createVideoOverview(t, e, r, s = "en") {
    return this.retryService.executeWithRetry(async () => {
      var f, A;
      const o = await this.ensureValidTokens(), a = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      a.searchParams.append("rpcids", "R7cb6c"), a.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), a.searchParams.append("bl", o.bl);
      const i = e.map((P) => [[P]]), l = r.map((P) => [[P]]), c = new URLSearchParams();
      c.append("at", o.at), c.append(
        "f.req",
        JSON.stringify([
          [
            [
              "R7cb6c",
              JSON.stringify([
                [2],
                t,
                [
                  null,
                  null,
                  3,
                  i.concat(l),
                  null,
                  null,
                  null,
                  null,
                  [null, null, [...e, ...r], s]
                ]
              ]),
              null,
              "generic"
            ]
          ]
        ])
      );
      const d = await fetch(a.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: c,
        credentials: "include"
      });
      if (!d.ok)
        throw new Error(`Error creating video overview. Status: ${d.status}`);
      const u = await d.text(), p = M(u);
      if (!p || !p[0] || !p[0].data)
        throw new Error("Invalid response from NotebookLM when creating video overview");
      const b = (f = p[0].data[0]) == null ? void 0 : f[0], m = (A = p[0].data[0]) == null ? void 0 : A[1];
      return {
        success: !0,
        data: {
          videoId: b,
          title: m,
          notebookId: t,
          status: "initiated"
        }
      };
    }).catch((o) => ({
      success: !1,
      error: o instanceof Error ? o.message : "Unknown error"
    }));
  }
  /**
   * Gets audio overview status
   */
  async getAudioOverviewStatus(t) {
    return this.retryService.executeWithRetry(async () => {
      var d;
      const e = await this.ensureValidTokens();
      if (!t)
        throw new Error("Invalid notebook ID in request");
      const r = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      r.searchParams.append("rpcids", "VUsiyb"), r.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), r.searchParams.append("bl", e.bl);
      const s = new URLSearchParams();
      s.append("at", e.at), s.append("f.req", JSON.stringify([[["VUsiyb", JSON.stringify([t, 0, [2]]), null, "generic"]]]));
      const o = await fetch(r.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: s,
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error getting audio overview status. Status: ${o.status}`);
      const a = await o.text(), i = M(a);
      if (!i || !i[0] || !i[0].data)
        throw new Error("Invalid response from NotebookLM when getting audio overview status");
      const l = (d = i[0].data[2]) == null ? void 0 : d[0];
      let c = "none";
      return l === 2 ? c = "generating" : l === 3 && (c = "ready"), {
        success: !0,
        data: {
          status: c,
          notebookId: t
        }
      };
    }).catch((e) => ({
      success: !1,
      error: e instanceof Error ? e.message : "Unknown error"
    }));
  }
  /**
   * Downloads audio overview as Blob
   */
  async getAudioOverview(t) {
    return this.retryService.executeWithRetry(async () => {
      const e = await this.ensureValidTokens();
      if (!t)
        throw new Error("Invalid notebook ID in request");
      const r = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      r.searchParams.append("rpcids", "VUsiyb"), r.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), r.searchParams.append("bl", e.bl);
      const s = new URLSearchParams();
      s.append("at", e.at), s.append("f.req", JSON.stringify([[["VUsiyb", JSON.stringify([t, 1, [2]]), null, "generic"]]]));
      const o = await fetch(r.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: s,
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error getting audio overview. Status: ${o.status}`);
      const a = await o.text(), i = M(a);
      if (!i || !i[0] || !i[0].data || !i[0].data[2])
        throw new Error("Invalid response from NotebookLM when getting audio overview");
      const l = i[0].data[2][1];
      if (!l)
        throw new Error("No audio data in response");
      const c = atob(l), d = new Uint8Array(c.length);
      for (let p = 0; p < c.length; p++)
        d[p] = c.charCodeAt(p);
      return {
        success: !0,
        data: {
          audioBlob: new Blob([d.buffer], { type: "audio/wav" }),
          notebookId: t
        }
      };
    }).catch((e) => ({
      success: !1,
      error: e instanceof Error ? e.message : "Unknown error"
    }));
  }
  /**
   * Gets audio overview URLs for streaming
   */
  async getAudioOverviewUrls(t) {
    return this.retryService.executeWithRetry(async () => {
      const e = await this.ensureValidTokens();
      if (!t)
        throw new Error("Invalid notebook ID in request");
      const r = new URL("https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute");
      r.searchParams.append("rpcids", "gArtLc"), r.searchParams.append("_reqid", String(Math.floor(Math.random() * 9e5) + 1e5)), r.searchParams.append("bl", e.bl);
      const s = new URLSearchParams();
      s.append("at", e.at), s.append("f.req", JSON.stringify([[["gArtLc", JSON.stringify([[[2]], t]), null, "generic"]]]));
      const o = await fetch(r.toString(), {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded;charset=utf-8" },
        body: s,
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error getting audio overview URLs. Status: ${o.status}`);
      const a = await o.text(), i = M(a);
      if (!i || !i[0] || !i[0].data || !i[0].data[0])
        throw new Error("Invalid response from NotebookLM when getting audio overview URLs");
      const l = i[0].data[0].filter((p) => p[2] === 1);
      if (!l || l.length === 0)
        throw new Error("No audio overview found for this notebook");
      const c = l[0][6];
      if (!c)
        throw new Error("Invalid audio data structure");
      const d = c[2], u = c[3];
      if (!d || !u)
        throw new Error("Missing audio URLs in response");
      return {
        success: !0,
        data: {
          playUrl: d,
          downloadUrl: u
        }
      };
    }).catch((e) => ({
      success: !1,
      error: e instanceof Error ? e.message : "Unknown error"
    }));
  }
  /**
   * Gets upload ID for resumable file upload
   * @param projectId - The notebook/project ID
   * @param sourceName - The name of the file to upload
   * @param sourceId - The source ID for the file
   * @param contentLength - The size of the file in bytes
   * @returns Upload ID and URLs for resumable upload
   */
  async getUploadId(t, e, r, s) {
    return this.retryService.executeWithRetry(async () => {
      if (await this.ensureValidTokens(), !t)
        throw new Error("Invalid project ID in request");
      if (!e)
        throw new Error("Source name is required");
      if (!r)
        throw new Error("Source ID is required");
      if (!s || s <= 0)
        throw new Error("Content length must be greater than 0");
      const o = await fetch("https://notebooklm.google.com/upload/_/?authuser=0", {
        method: "POST",
        headers: {
          accept: "*/*",
          "accept-language": "en-US,en;q=0.9,ru;q=0.8",
          "content-type": "application/json",
          "x-goog-authuser": "0",
          "x-goog-upload-command": "start",
          "x-goog-upload-header-content-length": String(s),
          "x-goog-upload-protocol": "resumable"
        },
        referrer: "https://notebooklm.google.com/",
        body: JSON.stringify({
          PROJECT_ID: t,
          SOURCE_NAME: e,
          SOURCE_ID: r
        }),
        credentials: "include"
      });
      if (!o.ok)
        throw new Error(`Error getting upload ID. Status: ${o.status}`);
      const a = o.headers.get("x-guploader-uploadid"), i = o.headers.get("x-goog-upload-url"), l = o.headers.get("x-goog-upload-control-url"), c = parseInt(o.headers.get("x-goog-upload-chunk-granularity") || "262144");
      if (!a || !i || !l)
        throw new Error("Missing upload information in response headers");
      return {
        success: !0,
        data: {
          uploadId: a,
          uploadUrl: i,
          controlUrl: l,
          chunkGranularity: c,
          projectId: t,
          sourceName: e,
          sourceId: r
        }
      };
    }).catch((o) => ({
      success: !1,
      error: o instanceof Error ? o.message : "Unknown error"
    }));
  }
  /**
   * Uploads file data using resumable upload protocol
   * @param uploadUrl - The upload URL from getUploadId
   * @param uploadId - The upload ID from getUploadId
   * @param fileContent - The file content as string or ArrayBuffer
   * @param fileName - The name of the file being uploaded
   * @param offset - The byte offset for resumable upload (default: 0)
   * @returns Upload result with success status and bytes uploaded
   */
  async uploadData(t, e, r, s, o = 0) {
    return this.retryService.executeWithRetry(async () => {
      if (!t)
        throw new Error("Upload URL is required");
      if (!e)
        throw new Error("Upload ID is required");
      if (!r)
        throw new Error("File content is required");
      if (!s)
        throw new Error("File name is required");
      let a;
      typeof r == "string" ? a = new TextEncoder().encode(r) : a = new Uint8Array(r);
      const i = await fetch(
        `https://notebooklm.google.com/upload/_/?authuser=0&upload_id=${e}&upload_protocol=resumable`,
        {
          method: "POST",
          headers: {
            accept: "*/*",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8",
            "content-type": "application/x-www-form-urlencoded;charset=utf-8",
            priority: "u=1, i",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-goog-upload-command": "upload, finalize",
            "x-goog-upload-offset": String(o)
          },
          referrer: "https://notebooklm.google.com/",
          body: a.slice(),
          credentials: "include"
        }
      );
      if (!i.ok)
        throw new Error(`Error uploading data. Status: ${i.status}`);
      return {
        success: !0,
        data: {
          success: !0,
          uploadId: e,
          bytesUploaded: a.byteLength,
          fileName: s
        }
      };
    }).catch((a) => ({
      success: !1,
      error: a instanceof Error ? a.message : "Unknown error"
    }));
  }
  // === UTILITY METHODS ===
  getNotebookDetailsFromCache(t, e) {
    return be(t, e);
  }
  async getYouTubePlaylistLinks(t) {
    return Ae(t);
  }
  // === AUTH METHODS ===
  /**
   * Extract parameters from response text
   */
  extractParam(t, e) {
    const s = new RegExp(`"${t}":"([^"]+)"`).exec(e);
    return s ? s[1] : void 0;
  }
  /**
   * Get authorization tokens
   */
  async getAuthTokens() {
    try {
      const e = await fetch("https://notebooklm.google.com/", {
        credentials: "include",
        redirect: "error",
        headers: {
          "Cache-Control": "no-cache, no-store, must-revalidate",
          Pragma: "no-cache",
          Expires: "0"
        }
      });
      if (!e.ok)
        throw new Error("Failed to connect to NotebookLM. Status: " + e.status);
      const r = await e.text(), s = this.extractParam("SNlM0e", r), o = this.extractParam("cfb2h", r);
      if (!s || !o)
        throw new Error("Please sign in to notebooklm.google.com before using this extension. Authorization required.");
      return this.lastTokenUpdate = Date.now(), this.cachedTokens = { at: s, bl: o }, chrome.storage.local.remove("cached_token_nlm", function() {
      }), chrome.storage.local.set({ cached_token_nlm: this.cachedTokens }, function() {
      }), { at: s, bl: o };
    } catch {
      throw new H("User not authenticated - no Google account or not signed in to NotebookLM");
    }
  }
  /**
   * Check token validity period
   */
  areTokensValid() {
    return !this.cachedTokens || !this.lastTokenUpdate ? !1 : Date.now() - this.lastTokenUpdate < this.TOKEN_VALIDITY_TIME;
  }
  /**
   * Check and update tokens before request
   */
  async ensureValidTokens() {
    try {
      return this.areTokensValid() ? this.cachedTokens : await this.getAuthTokens();
    } catch (t) {
      throw t instanceof H ? new H("User not authenticated - no Google account or not signed in to NotebookLM") : t;
    }
  }
  /**
   * Logout (clear tokens)
   */
  logout() {
    this.cachedTokens = null, this.lastTokenUpdate = 0;
  }
  /**
   * Update tokens (force refresh)
   */
  async refreshTokens() {
    return this.cachedTokens = null, this.lastTokenUpdate = 0, await this.getAuthTokens();
  }
}
var de = /* @__PURE__ */ ((n) => (n.NOTEBOOKLM = "notebooklm", n))(de || {});
function Se(n) {
  switch (n) {
    case "notebooklm":
      return new ye();
    default:
      throw new Error(`Unknown API type: ${n}`);
  }
}
const V = 1e3, xe = "https://docs.google.com/forms/d/e/1FAIpQLSfns-t1iN7RhnCAUaohgq6F7vVwC_QUYD4nxCAW24fWVSxVvQ/viewform", h = {
  notebooks: [],
  authTokens: null,
  pendingNotifications: /* @__PURE__ */ new Map(),
  selectedNotebookId: "",
  currentLinks: [],
  isAuthenticated: !0,
  isInitialized: !1
}, g = {
  isActive: !1,
  selectedLinksByPage: {},
  totalSelectedCount: 0,
  isAddingLinks: !1,
  currentAddingRequestId: "",
  addingProgress: { added: 0, total: 0, percentage: 0 },
  cancelRequested: !1
}, S = {
  isDeletingLinks: !1,
  currentRequestId: "",
  deletingProgress: { deleted: 0, total: 0, percentage: 0 },
  cancelRequested: !1
}, T = {
  isCapturing: !1,
  currentRequestId: ""
}, D = Se(de.NOTEBOOKLM);
let K = null;
const Y = (n) => n != null && (n.startsWith("http:") || n.startsWith("https:")) && !n.includes("chrome://") && !n.includes("edge://") && !n.includes("chrome-extension://") && !n.includes("chrome.google.com/webstore") && !n.includes("chromewebstore.google.com") && !n.includes("addons.mozilla.org") && !n.includes("chrome://extensions/") && !n.includes("chrome://settings/") && !n.includes("chrome://newtab/") && !n.includes("chrome://history/") && !n.includes("chrome://downloads/") && !n.includes("chrome://bookmarks/") && !n.includes("chrome://omnibox/") && !n.includes("chrome://search/") && !n.includes("chrome://flags/") && !n.includes("chrome://inspect/") && !n.includes("chrome://devtools/") && !n.includes("chrome://version/") && !n.includes("chrome://help/") && !n.includes("chrome://about/") && !n.includes("chrome://accessibility/") && !n.includes("chrome://blob-interner/") && !n.includes("chrome://credits/") && !n.includes("chrome://dino/") && !n.includes("chrome://discards/") && !n.includes("chrome://domain-reliability/") && !n.includes("chrome://gpu/") && !n.includes("chrome://inducebrowsercrashforrealz/") && !n.includes("chrome://kill/") && !n.includes("chrome://media-internals/") && !n.includes("chrome://net-export/") && !n.includes("chrome://net-internals/") && !n.includes("chrome://policy/") && !n.includes("chrome://predictors/") && !n.includes("chrome://process-internals/") && !n.includes("chrome://quota-internals/") && !n.includes("chrome://serviceworker-internals/") && !n.includes("chrome://site-engagement/") && !n.includes("chrome://supervised-user-internals/") && !n.includes("chrome://sync-internals/") && !n.includes("chrome://system/") && !n.includes("chrome://terms/") && !n.includes("chrome://translate-internals/") && !n.includes("chrome://usb-internals/") && !n.includes("chrome://user-actions/") && !n.includes("chrome://webrtc-internals/") && !n.includes("chrome://webrtc-logs/"), j = /* @__PURE__ */ new Set(), F = (n, t) => chrome.tabs.get(n, (e) => {
  if (!chrome.runtime.lastError && Y(e.url))
    try {
      chrome.tabs.sendMessage(n, t, (r) => {
        var s, o;
        chrome.runtime.lastError ? (s = chrome.runtime.lastError.message) != null && s.includes("Could not establish connection") ? j.has(n) || Le(n, t) : (o = chrome.runtime.lastError.message) != null && o.includes("cannot be scripted") : j.add(n);
      });
    } catch {
    }
}), Le = (n, t) => {
  try {
    chrome.scripting.executeScript(
      {
        target: { tabId: n },
        files: ["content/all.iife.js"]
      },
      (e) => {
        chrome.runtime.lastError || !e || e.length === 0 || (j.add(n), setTimeout(() => {
          try {
            chrome.tabs.sendMessage(n, t, () => {
              chrome.runtime.lastError;
            });
          } catch {
          }
        }, 1e3));
      }
    );
  } catch {
  }
}, W = (n) => {
  chrome.tabs.query({}, (t) => {
    t.forEach((e) => {
      e.id && Y(e.url) && F(e.id, n);
    });
  });
}, re = () => {
  E({
    action: "linkSelectionStateUpdate",
    data: {
      isActive: g.isActive,
      selectedLinksCount: g.totalSelectedCount,
      isAddingLinks: g.isAddingLinks,
      addingProgress: g.addingProgress
    }
  });
}, E = (n) => {
  try {
    chrome.runtime.sendMessage(n, (t) => {
      var e;
      chrome.runtime.lastError && (e = chrome.runtime.lastError.message) != null && e.includes("message port closed");
    });
  } catch (t) {
    (t instanceof Error ? t.message : String(t)).includes("message port closed");
  }
}, se = (n) => btoa(n).slice(0, 16), ue = () => {
  const n = /* @__PURE__ */ new Set();
  let t = 0;
  Object.values(g.selectedLinksByPage).forEach((e) => {
    e.forEach((r) => {
      n.has(r.url) || (n.add(r.url), t++);
    });
  }), g.totalSelectedCount = t, re();
}, Ee = () => {
  const n = [], t = /* @__PURE__ */ new Set();
  return Object.values(g.selectedLinksByPage).forEach((e) => {
    e.forEach((r) => {
      t.has(r.url) || (t.add(r.url), n.push(r));
    });
  }), n;
}, Q = () => {
  g.selectedLinksByPage = {}, g.totalSelectedCount = 0, re();
}, Pe = (n, t) => {
  h.pendingNotifications || (h.pendingNotifications = /* @__PURE__ */ new Map());
  const e = h.pendingNotifications.get(n) || /* @__PURE__ */ new Set();
  return e.has(t) ? !1 : (e.add(t), h.pendingNotifications.set(n, e), setTimeout(() => {
    const r = h.pendingNotifications.get(n);
    r && (r.delete(t), r.size === 0 ? h.pendingNotifications.delete(n) : h.pendingNotifications.set(n, r));
  }, 3e3), !0);
}, Te = async (n, t) => {
  var e;
  try {
    const s = ((e = (await D.getNotebooks()).data) == null ? void 0 : e.notebooks) || [];
    if (!Array.isArray(s))
      throw new Error("Invalid notebooks data format");
    if (h.notebooks = s, s.length === 0) {
      h.selectedNotebookId = "", h.currentLinks = [], E({
        action: "notebooksLoaded",
        notebooks: [],
        selectedNotebookId: ""
      }), F(n, {
        action: "notebooksLoaded",
        notebooks: [],
        selectedNotebookId: ""
      }), t && t({
        success: !0,
        notebooks: [],
        selectedNotebookId: ""
      });
      return;
    }
    let o = h.selectedNotebookId;
    if ((!o && s.length > 0 || o && !s.some((i) => i.id === o) && s.length > 0) && (o = s[0].id), h.selectedNotebookId = o || "", o) {
      const a = s.find((i) => i.id === o);
      a ? h.currentLinks = a.links || [] : h.currentLinks = [];
    } else
      h.currentLinks = [];
    t && t({
      success: !0,
      notebooks: s,
      selectedNotebookId: h.selectedNotebookId
    });
  } catch (r) {
    t && t({
      success: !1,
      error: r instanceof Error ? r.message : "Failed to get notebooks"
    });
  }
}, ve = (n, t, e) => {
  try {
    if (!t.notebookId)
      throw new Error("Notebook ID not specified");
    if (!h.notebooks || h.notebooks.length === 0) {
      D.getNotebooks().then((s) => {
        var i;
        const o = ((i = s.data) == null ? void 0 : i.notebooks) || [];
        h.notebooks = o;
        const a = D.getNotebookDetailsFromCache(t.notebookId, h.notebooks);
        h.currentLinks = a.links || [], h.selectedNotebookId = t.notebookId, F(n, {
          action: "notebookDetailsLoaded",
          notebookId: t.notebookId,
          links: h.currentLinks || []
        }), e && e({
          success: !0,
          notebookId: t.notebookId,
          links: h.currentLinks || []
        });
      }).catch((s) => {
        e && e({
          success: !1,
          error: "Failed to load notebooks"
        });
      });
      return;
    }
    const r = D.getNotebookDetailsFromCache(t.notebookId, h.notebooks);
    h.currentLinks = r.links || [], h.selectedNotebookId = t.notebookId, F(n, {
      action: "notebookDetailsLoaded",
      notebookId: t.notebookId,
      links: h.currentLinks || []
    }), e && e({
      success: !0,
      notebookId: t.notebookId,
      links: h.currentLinks || []
    });
  } catch (r) {
    F(n, {
      action: "error",
      error: r instanceof Error ? r.message : "Failed to load notebook details."
    }), e && e({
      success: !1,
      error: r instanceof Error ? r.message : "Failed to load notebook details"
    });
  }
}, Ue = async (n, t, e) => {
  var r;
  try {
    if (!t.notebookId)
      throw new Error("Notebook ID not specified");
    if (!t.pageUrl)
      throw new Error("Page URL not specified");
    if (!Y(t.pageUrl))
      throw new Error("Cannot add links from system pages (chrome://, edge://, etc.)");
    if (h.currentLinks.length >= V)
      throw new Error(`Link limit reached (${V}) for notebook`);
    let s = [];
    if (ae(t.pageUrl)) {
      const d = await D.getYouTubePlaylistLinks(t.pageUrl);
      if (h.currentLinks.length + d.length > V)
        throw new Error(
          `Cannot add all videos from playlist. ${V - h.currentLinks.length} slots available out of ${V}`
        );
      s = d.map((p) => ({
        url: p.url,
        title: p.title || "YouTube video"
      }));
    } else
      s = [
        {
          url: t.pageUrl,
          title: t.pageTitle || "Untitled"
        }
      ];
    const a = ((r = (await D.addSources(
      t.notebookId,
      s.map((d) => ({ url: d.url }))
    )).data) == null ? void 0 : r.addedSources) || [];
    let i = 0;
    for (let d = 0; d < a.length; d++) {
      const u = a[d], p = s[d];
      u.success && (h.currentLinks.push({
        id: u.sourceId,
        url: u.url || p.url,
        title: u.title || p.title || "Untitled"
      }), i++);
    }
    const l = h.notebooks.findIndex((d) => d.id === t.notebookId);
    l !== -1 && (h.notebooks[l].links = h.currentLinks);
    const c = ae(t.pageUrl) ? `Added ${i} videos from playlist` : "Link added to notebook";
    E({
      action: "linkAdded",
      notebookId: t.notebookId,
      links: [...h.currentLinks],
      message: c
    }), e && e({
      success: !0,
      notebookId: t.notebookId,
      links: h.currentLinks,
      message: c
    }), g.isAddingLinks = !1;
  } catch (s) {
    F(n, {
      action: "error",
      error: s instanceof Error ? s.message : "Failed to add page to notebook."
    }), e && e({
      success: !1,
      error: s instanceof Error ? s.message : "Failed to add page to notebook"
    });
  }
}, Ne = async (n, t, e) => {
  var r, s;
  try {
    if (!t.title)
      throw new Error("Notebook title not specified");
    const a = (r = (await D.createNotebook(t.title, t.emoji || "📔")).data) == null ? void 0 : r.notebookId;
    if (!a)
      throw new Error("Failed to get notebook ID from API response");
    const i = [], c = ((s = (await D.getNotebooks()).data) == null ? void 0 : s.notebooks) || [];
    h.notebooks = c, h.selectedNotebookId = a, h.currentLinks = i;
    const d = c.findIndex((p) => p.id === a);
    d !== -1 && (c[d].links = i);
    const u = `create_success_${Date.now()}`;
    Pe(n, u) && F(n, {
      action: "notebookCreated",
      notebookId: a,
      notebooks: c,
      links: i,
      // Пустой массив
      isYouTubePlaylist: !1
      // Всегда false, так как ничего не добавляем
    }), e && e({
      success: !0,
      notebookId: a,
      notebooks: c,
      links: i
      // Пустой массив
    });
  } catch (o) {
    const a = o instanceof Error ? o.message : "Failed to create notebook.";
    F(n, {
      action: "error",
      error: a
    }), e && e({
      success: !1,
      error: a
    });
  }
}, Ie = (n, t) => {
  try {
    g.isActive = !0, g.selectedLinksByPage = {}, g.totalSelectedCount = 0, g.isAddingLinks = !1, g.cancelRequested = !1, W({
      action: "enableLinkPickingMode"
    }), E({
      action: "linkPickingModeEnabled"
    }), re(), t && t({ success: !0 });
  } catch (e) {
    t && t({
      success: !1,
      error: e instanceof Error ? e.message : "Error enabling link picking mode"
    });
  }
}, oe = (n, t) => {
  try {
    g.isActive = !1, Q(), W({
      action: "disableLinkPickingMode"
    }), W({
      action: "clearLinkHighlights"
    }), E({
      action: "linkPickingModeDisabled"
    }), t && t({ success: !0 });
  } catch (e) {
    t && t({
      success: !1,
      error: e instanceof Error ? e.message : "Error disabling link picking mode"
    });
  }
}, Ce = (n, t) => {
  const e = se(t.pageUrl);
  g.selectedLinksByPage[e] || (g.selectedLinksByPage[e] = []), g.selectedLinksByPage[e].some((s) => s.url === t.link.url) || (g.selectedLinksByPage[e].push(t.link), ue());
}, Me = (n, t) => {
  const e = se(t.pageUrl);
  g.selectedLinksByPage[e] && (g.selectedLinksByPage[e] = g.selectedLinksByPage[e].filter(
    (r) => r.url !== t.linkUrl
  ), g.selectedLinksByPage[e].length === 0 && delete g.selectedLinksByPage[e], ue());
}, Oe = (n, t, e) => {
  const r = se(t.pageUrl), s = g.selectedLinksByPage[r] || [];
  e({
    links: s
  });
}, De = (n, t) => {
  t({
    isActive: g.isActive,
    selectedLinksCount: g.totalSelectedCount
  });
}, Re = async (n, t, e) => {
  try {
    const { notebookId: r, requestId: s } = t;
    if (!r) throw new Error("Notebook ID not specified");
    if (g.isAddingLinks && g.currentAddingRequestId !== s)
      throw new Error("Another link addition process is already running");
    const o = Ee();
    if (o.length === 0) throw new Error("No links selected");
    const a = V - h.currentLinks.length;
    if (a <= 0)
      throw new Error(`Notebook reached link limit of ${V}`);
    const i = o.slice(0, a);
    i.length < o.length, g.isAddingLinks = !0, g.currentAddingRequestId = s, g.addingProgress = {
      added: 0,
      total: i.length,
      percentage: 0
    }, g.cancelRequested = !1, e == null || e({
      success: !0,
      status: "started",
      message: "Link addition started"
    }), $e({
      linksToAdd: i,
      requestId: s,
      tabId: n,
      notebookId: r
    });
  } catch (r) {
    const s = r instanceof Error ? r.message : "Request validation error";
    e == null || e({ success: !1, error: s }), E({
      action: "error",
      error: s
    });
  }
};
function $e({
  linksToAdd: n,
  requestId: t,
  tabId: e,
  notebookId: r
}) {
  (async () => {
    var s;
    try {
      if (g.cancelRequested) {
        ee(e, t, 0, 0, n.length, [], []);
        return;
      }
      if (g.currentAddingRequestId !== t) {
        ee(e, t, 0, 0, n.length, [], []);
        return;
      }
      if (!g.isAddingLinks) {
        ee(e, t, 0, 0, n.length, [], []);
        return;
      }
      E({
        action: "addingProgressUpdate",
        message: "Adding links...",
        progress: 0,
        addedCount: 0,
        failedCount: 0,
        totalCount: n.length,
        requestId: t
      });
      const o = [], a = [];
      for (const m of n) {
        const { url: f, title: A } = m, P = Ze(f) ? Qe(f) : f;
        h.currentLinks.some((N) => N.url === P) || (o.push({ url: P }), a.push({
          url: P,
          title: A || "Untitled",
          originalUrl: f
        }));
      }
      if (o.length === 0) {
        ie(e, t, 0, 0, n.length, [], [], r);
        return;
      }
      const l = ((s = (await D.addSources(r, o)).data) == null ? void 0 : s.addedSources) || [];
      let c = 0, d = 0;
      const u = [], p = [];
      for (let m = 0; m < l.length; m++) {
        const f = l[m], A = a[m];
        f.success ? (h.currentLinks.push({
          id: f.sourceId,
          url: f.url || A.url,
          title: f.title || A.title
        }), c++, u.push(A.url)) : (d++, p.push(A.url));
      }
      const b = h.notebooks.findIndex((m) => m.id === r);
      b !== -1 && (h.notebooks[b].links = [...h.currentLinks]), ie(
        e,
        t,
        c,
        d,
        n.length,
        u,
        p,
        r
      );
    } catch (o) {
      Fe(e, t, o, 0, 0, n.length, [], []);
    }
  })();
}
const ie = (n, t, e, r, s, o, a, i) => {
  g.isAddingLinks = !1, g.isActive = !1, g.currentAddingRequestId = "", g.cancelRequested = !1, g.addingProgress = { added: 0, total: 0, percentage: 0 }, Q(), W({
    action: "disableLinkPickingMode"
  }), W({
    action: "clearLinkHighlights"
  }), E({
    action: "linksAdded",
    notebookId: i,
    links: [...h.currentLinks],
    message: "Links added to notebook",
    addedCount: e,
    failedCount: r,
    requestId: t
  });
}, ee = (n, t, e, r, s, o, a) => {
  g.isAddingLinks = !1, g.isActive = !0, g.cancelRequested = !1, g.currentAddingRequestId = "", g.addingProgress = { added: 0, total: 0, percentage: 0 }, Q(), W({
    action: "highlightLinksWithStatus",
    data: {
      successUrls: o,
      failedUrls: a
    }
  }), E({
    action: "linkAddingCancelled",
    message: `Operation cancelled. Added ${e} of ${s}.`,
    addedCount: e,
    failedCount: r,
    totalCount: s,
    requestId: t
  });
}, Fe = (n, t, e, r, s, o, a, i) => {
  g.isAddingLinks = !1, g.isActive = !0, W({
    action: "highlightLinksWithStatus",
    data: {
      successUrls: a,
      failedUrls: i
    }
  }), E({
    action: "error",
    error: e instanceof Error ? e.message : "Unhandled link processing error"
  });
}, te = () => `link_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`, _e = async (n, t, e) => {
  try {
    const { requestId: r } = t;
    if (!r) {
      e && e({
        success: !1,
        error: "Request ID is required for cancellation"
      });
      return;
    }
    if (!g.isAddingLinks) {
      e && e({
        success: !0,
        message: "No active process found"
      });
      return;
    }
    g.currentAddingRequestId && g.currentAddingRequestId, g.cancelRequested = !0, e && e({
      success: !0,
      message: "Cancellation request registered"
    }), setTimeout(() => {
      g.isAddingLinks && g.cancelRequested && (g.isAddingLinks = !1, g.cancelRequested = !1, g.currentAddingRequestId = "", g.addingProgress = { added: 0, total: 0, percentage: 0 }, g.isActive = !0, E({
        action: "linkAddingCancelled",
        message: "Operation was cancelled",
        addedCount: 0,
        failedCount: 0,
        totalCount: 0,
        requestId: r
      }));
    }, 2e3);
  } catch (r) {
    e && e({
      success: !1,
      error: r instanceof Error ? r.message : "Failed to cancel operation"
    });
  }
}, qe = async (n, t, e) => {
  try {
    if (!t.notebookId)
      throw new Error("Notebook ID not specified");
    if (!t.linkIds || !Array.isArray(t.linkIds) || t.linkIds.length === 0)
      throw new Error("No links selected for deletion");
    const { notebookId: r, linkIds: s, requestId: o } = t;
    if (S.isDeletingLinks && S.currentRequestId !== (o || ""))
      throw new Error("Another link deletion process is already running");
    S.isDeletingLinks = !0, S.currentRequestId = o || te(), S.deletingProgress = {
      deleted: 0,
      total: s.length,
      percentage: 0
    }, S.cancelRequested = !1, e == null || e({
      success: !0,
      status: "started",
      message: "Link deletion started"
    }), Be({
      linksToDelete: s,
      requestId: o || te(),
      tabId: n,
      notebookId: r
    });
  } catch (r) {
    e && e({
      success: !1,
      error: r instanceof Error ? r.message : "Failed to start link deletion"
    }), E({
      action: "error",
      error: r instanceof Error ? r.message : "Failed to start link deletion"
    });
  }
}, We = (n, t) => {
  const e = {
    success: !0,
    addingLinks: g.isAddingLinks,
    addingRequestId: g.currentAddingRequestId,
    addingProgress: g.addingProgress,
    deletingLinks: S.isDeletingLinks,
    deletingRequestId: S.currentRequestId,
    deletingProgress: S.deletingProgress
  };
  t == null || t(e);
}, Je = async (n, t, e) => {
  try {
    const { requestId: r } = t;
    if (!r) {
      e && e({
        success: !1,
        error: "Request ID is required for cancellation"
      });
      return;
    }
    if (!S.isDeletingLinks) {
      e && e({
        success: !0,
        message: "No active process found"
      });
      return;
    }
    S.currentRequestId && S.currentRequestId, S.cancelRequested = !0, e && e({
      success: !0,
      message: "Cancellation request registered"
    }), setTimeout(() => {
      S.isDeletingLinks && S.cancelRequested && (S.isDeletingLinks = !1, S.cancelRequested = !1, S.currentRequestId = "", S.deletingProgress = { deleted: 0, total: 0, percentage: 0 }, E({
        action: "linkDeletingCancelled",
        message: "Deletion was cancelled",
        deletedCount: 0,
        failedCount: 0,
        totalCount: 0,
        requestId: r,
        clearSelection: !0
        // Флаг для очистки выделения
      }));
    }, 2e3);
  } catch (r) {
    e && e({
      success: !1,
      error: r instanceof Error ? r.message : "Failed to cancel deletion operation"
    });
  }
}, Ve = (n, t, e, r, s) => {
  S.isDeletingLinks = !1, S.currentRequestId = "", S.cancelRequested = !1, S.deletingProgress = { deleted: 0, total: 0, percentage: 0 }, E({
    action: "linkDeletingCancelled",
    message: `Deletion cancelled. Deleted ${e} of ${s}${r > 0 ? ` (${r} failed)` : ""}.`,
    deletedCount: e,
    failedCount: r,
    totalCount: s,
    requestId: t,
    clearSelection: !0
    // Добавить флаг для очистки выделения
  });
};
function Be({
  linksToDelete: n,
  requestId: t,
  tabId: e,
  notebookId: r
}) {
  (async () => {
    S.isDeletingLinks = !0, S.currentRequestId = t, S.cancelRequested = !1;
    let s = 0, o = 0;
    const a = n.length;
    try {
      for (let l = 0; l < n.length; l++) {
        if (S.cancelRequested || S.currentRequestId !== t) {
          Ve(e, t, s, o, a);
          return;
        }
        const c = n[l];
        try {
          await D.deleteSource(c), s++, h.currentLinks = h.currentLinks.filter((u) => u.id !== c);
        } catch {
          o++;
        }
        const d = s + o;
        (d % 1 === 0 || d === a) && Ge(e, t, s, o, a);
      }
      const i = h.notebooks.findIndex((l) => l.id === r);
      i !== -1 && (h.notebooks[i].links = [...h.currentLinks]), ze(e, t, s, o, a, r);
    } catch (i) {
      je(e, t, i, s, o, a);
    }
  })();
}
const ze = (n, t, e, r, s, o) => {
  S.isDeletingLinks = !1, S.currentRequestId = "", S.cancelRequested = !1, S.deletingProgress = { deleted: 0, total: 0, percentage: 0 }, E({
    action: "linksDeleted",
    notebookId: o,
    links: [...h.currentLinks],
    message: `Deleted ${e} link${e > 1 ? "s" : ""}${r ? ` (${r} failed)` : ""}`,
    deletedCount: e,
    failedCount: r,
    requestId: t,
    clearSelection: !0
  });
}, je = (n, t, e, r, s, o) => {
  S.isDeletingLinks = !1, S.currentRequestId = "", S.cancelRequested = !1, E({
    action: "error",
    error: e instanceof Error ? e.message : "Unhandled link deletion error",
    deletedCount: r,
    failedCount: s,
    totalCount: o,
    requestId: t
  });
}, Ge = (n, t, e, r, s) => {
  E({
    action: "deletingProgressUpdate",
    message: `Deleted ${e} of ${s} links${r > 0 ? ` (${r} failed)` : ""}`,
    progress: (e + r) / s,
    deletedCount: e,
    failedCount: r,
    totalCount: s,
    requestId: t
  });
}, Ye = async (n, t) => {
  var e, r;
  try {
    const s = await D.getAccount(), { isAuthenticated: o } = ge(((r = (e = s.data) == null ? void 0 : e.rawAccountData) == null ? void 0 : r.toString()) || "");
    h.isAuthenticated = o, h.isInitialized = !0;
  } catch {
    h.isAuthenticated = !1, h.isInitialized = !0;
  }
  t && t({
    success: !0,
    isAuthenticated: h.isAuthenticated,
    isInitialized: h.isInitialized
  });
}, ce = (n, t, e, r) => {
  if (!e)
    return t && "requestId" in n && n.requestId ? E({
      action: "apiResponse",
      requestId: n.requestId,
      response: { error: "Tab ID not determined" }
    }) : r && r({ error: "Tab ID not determined" }), !0;
  if (t && "requestId" in n && n.requestId) {
    const s = n.requestId, a = ((i) => (l) => {
      try {
        E({
          action: "apiResponse",
          requestId: i,
          response: l
        });
      } catch {
      }
    })(s);
    switch (n.action) {
      case "getAuthStatus":
        return Ye(e, a), !0;
      case "getNotebooks":
      case "refreshNotebooks":
        return Te(e, a), !0;
      case "getNotebookDetails":
        return ve(e, n, a), !0;
      case "addToNotebook":
        return Ue(e, n, a), !0;
      case "createNotebook":
        return Ne(e, n, a), !0;
      case "enableLinkPicking":
        return Ie(e, a), !0;
      case "disableLinkPicking":
        return oe(e, a), !0;
      case "addSelectedLinks":
        return g.isAddingLinks && g.currentAddingRequestId !== s ? (a({
          success: !1,
          error: "Another link addition process is already running"
        }), !0) : (Re(e, n, a), !0);
      case "cancelAddingLinks":
        return _e(e, n, a), !0;
      case "deleteLinks":
        return S.isDeletingLinks && S.currentRequestId !== s ? (a({
          success: !1,
          error: "Another link deletion process is already running"
        }), !0) : (qe(e, n, a), !0);
      case "cancelDeletingLinks":
        return Je(e, n, a), !0;
      case "getActiveProcesses":
        return We(e, a), !0;
      case "getUserProfile":
        return He(e, a), !0;
      case "startScreenshotCapture":
        return Xe(e, n, a), !0;
      case "screenshotCaptureCancelled":
        return le(e, a), !0;
      case "addFiles":
        return tt(e, n, a), !0;
      default:
        return E({
          action: "apiResponse",
          requestId: s,
          response: { error: "Unknown action" }
        }), !0;
    }
  }
  return n.action === "addLinkToSelection" ? (n.data && Ce(e, n.data), r && r({ success: !0 })) : n.action === "removeLinkFromSelection" ? (n.data && Me(e, n.data), r && r({ success: !0 })) : n.action === "getSelectedLinksForPage" ? n.data && r && Oe(e, n.data, r) : n.action === "getLinkPickingState" ? r && De(e, r) : n.action === "clearSelectedLinks" ? (Q(), r && r({ success: !0 })) : n.action === "disableLinkPickingMode" ? oe(e, r) : n.action === "captureScreenshotArea" ? et(e, n, r) : n.action === "screenshotCaptureCancelled" ? le(e, r) : r && r({}), !0;
}, He = async (n, t) => {
  try {
    const e = await chrome.tabs.create({
      url: "https://notebooklm.google.com/",
      active: !0
      // Устанавливаем active: true для отображения вкладки пользователю
    });
    if (!e.id)
      throw new Error("Failed to open NotebookLM tab");
    await new Promise((a, i) => {
      const l = (c, d) => {
        c === e.id && d.status === "complete" && (chrome.tabs.onUpdated.removeListener(l), a());
      };
      chrome.tabs.onUpdated.addListener(l), setTimeout(() => {
        chrome.tabs.onUpdated.removeListener(l), i(new Error("Page load timeout"));
      }, 2e4);
    }), await new Promise((a) => setTimeout(a, 5e3));
    const s = await (async () => new Promise((a) => {
      chrome.tabs.sendMessage(e.id, { action: "ping", source: "background" }, (i) => {
        if (chrome.runtime.lastError || !i)
          try {
            chrome.scripting.executeScript(
              {
                target: { tabId: e.id },
                files: ["content/all.iife.js"]
              },
              () => {
                chrome.runtime.lastError ? a(!1) : setTimeout(() => a(!0), 2e3);
              }
            );
          } catch {
            a(!1);
          }
        else
          a(!0);
      });
    }))(), o = async (a = 3) => {
      let i = 0;
      for (; i < a; )
        try {
          return await new Promise((l, c) => {
            const d = setTimeout(() => {
              c(new Error("Request timeout"));
            }, 1e4);
            chrome.tabs.sendMessage(
              e.id,
              {
                action: "getAccountInfo",
                source: "background"
              },
              (u) => {
                if (clearTimeout(d), chrome.runtime.lastError) {
                  c(new Error(chrome.runtime.lastError.message));
                  return;
                }
                if (!u || !u.success) {
                  c(new Error((u == null ? void 0 : u.error) || "Failed to get account data"));
                  return;
                }
                l(u);
              }
            );
          });
        } catch (l) {
          if (i++, i >= a)
            throw l;
          await new Promise((c) => setTimeout(c, 3e3));
        }
    };
    try {
      const a = await o();
      E({
        action: "userProfileLoaded",
        success: !0,
        data: a.data
      }), t && t({
        success: !0,
        data: a.data
      });
    } catch (a) {
      E({
        action: "userProfileLoaded",
        success: !1,
        error: a instanceof Error ? a.message : "Failed to get account data after multiple attempts"
      }), t && t({
        success: !1,
        error: a instanceof Error ? a.message : "Failed to get account data"
      });
    }
  } catch (e) {
    E({
      action: "userProfileLoaded",
      success: !1,
      error: e instanceof Error ? e.message : "Failed to load user profile"
    }), t && t({
      success: !1,
      error: e instanceof Error ? e.message : "Failed to load user profile"
    });
  }
}, Ke = async (n) => {
  var t;
  try {
    let e;
    if (n)
      try {
        e = await chrome.tabs.get(n);
      } catch (o) {
        const a = o instanceof Error ? o.message : String(o);
        return j.delete(n), {
          title: "Tab Not Found",
          url: "",
          favicon: "",
          tabId: null
        };
      }
    else
      e = (await chrome.tabs.query({ active: !0, currentWindow: !0 }))[0];
    if (!e)
      return {
        title: "No Active Tab",
        url: "",
        favicon: "",
        tabId: null
      };
    if ((t = e.url) != null && t.includes("youtube.com")) {
      await new Promise((o) => setTimeout(o, 200));
      try {
        e = await chrome.tabs.get(e.id);
      } catch {
      }
    }
    return {
      title: !Y(e.url || "") ? "System Page (Cannot add links)" : e.title || "Untitled",
      url: e.url || "",
      favicon: e.favIconUrl || "",
      tabId: e.id || null
    };
  } catch {
    return {
      title: "Error",
      url: "",
      favicon: "",
      tabId: null
    };
  }
}, J = async (n) => {
  const t = await Ke(n);
  E({
    action: "pageInfo",
    title: t.title,
    url: t.url,
    favicon: t.favicon,
    source: "background"
  });
}, Ze = (n) => {
  const t = n.match(/[?&]list=([^&]+)/);
  if (!t) return !1;
  const e = t[1];
  return e.startsWith("RD") || e.startsWith("WL") || e.startsWith("LL");
}, Qe = (n) => {
  try {
    const t = new URL(n);
    return t.searchParams.delete("list"), t.searchParams.delete("index"), t.toString();
  } catch {
    return n;
  }
}, Xe = async (n, t, e) => {
  try {
    const r = t.requestId || te();
    T.isCapturing = !0, T.currentRequestId = r;
    const o = ((c) => {
      let d = 1e4;
      return chrome.tabs.get(c, (u) => {
        u && u.url && (u.url.includes("youtube.com") ? d = 15e3 : u.url.includes("google.com") ? d = 12e3 : (u.url.includes("localhost") || u.url.includes("127.0.0.1")) && (d = 5e3));
      }), d;
    })(n), a = setTimeout(() => {
      T.isCapturing = !1, T.currentRequestId = "", e && e({
        success: !1,
        error: `Content script response timeout (${o}ms)`
      });
    }, o), l = (await chrome.storage.local.get(["theme"])).theme || "light";
    chrome.tabs.sendMessage(
      n,
      {
        action: "startScreenshotCapture",
        source: "background",
        requestId: r,
        theme: l
      },
      (c) => {
        if (clearTimeout(a), chrome.runtime.lastError) {
          T.isCapturing = !1, T.currentRequestId = "", e && e({
            success: !1,
            error: chrome.runtime.lastError.message || "Failed to start screenshot capture"
          });
          return;
        }
        c && c.success ? (E({
          action: "screenshotCaptureStarted",
          requestId: r,
          message: "Screenshot capture started. Select an area on the page."
        }), e && e({
          success: !0,
          requestId: r,
          message: "Screenshot capture started"
        })) : (T.isCapturing = !1, T.currentRequestId = "", e && e({
          success: !1,
          error: (c == null ? void 0 : c.error) || "Failed to start screenshot capture"
        }));
      }
    );
  } catch (r) {
    T.isCapturing = !1, T.currentRequestId = "", e && e({
      success: !1,
      error: r instanceof Error ? r.message : "Failed to start screenshot capture"
    });
  }
}, le = async (n, t) => {
  T.isCapturing = !1, T.currentRequestId = "";
  try {
    E({
      action: "screenshotCaptureReset",
      message: "Screenshot capture cancelled by user",
      timestamp: (/* @__PURE__ */ new Date()).toISOString()
    });
  } catch {
  }
  try {
    chrome.tabs.sendMessage(
      n,
      {
        action: "resetScreenshotCapture",
        source: "background",
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      },
      (e) => {
        chrome.runtime.lastError;
      }
    );
  } catch {
  }
  t && t({
    success: !0,
    message: "Screenshot capture cancelled",
    timestamp: (/* @__PURE__ */ new Date()).toISOString()
  });
}, et = async (n, t, e) => {
  try {
    const r = await chrome.tabs.get(n);
    if (!r || !r.windowId)
      throw new Error("Unable to get tab information for screenshot capture");
    const s = await chrome.tabs.captureVisibleTab(r.windowId, { format: "png" });
    T.isCapturing = !1, T.currentRequestId = "", E({
      action: "screenshotReady",
      imageData: s,
      filename: t.filename,
      selection: t.selection,
      timestamp: t.timestamp,
      message: "Screenshot captured successfully. Processing..."
    }), e && e({
      success: !0,
      message: "Screenshot processed successfully"
    });
  } catch (r) {
    T.isCapturing = !1, T.currentRequestId = "", E({
      action: "screenshotError",
      error: r instanceof Error ? r.message : "Failed to capture screenshot"
    }), e && e({
      success: !1,
      error: r instanceof Error ? r.message : "Failed to capture screenshot"
    });
  }
}, tt = async (n, t, e) => {
  try {
    const { notebookId: r, files: s, requestId: o } = t;
    if (!r)
      throw new Error("Notebook ID not specified");
    if (!s || s.length === 0)
      throw new Error("No files provided");
    const a = s.map((p) => ({ fileName: p.fileName })), i = await D.addFiles(r, a);
    if (!i.success || !i.data)
      throw new Error(`Failed to register files: ${i.error}`);
    const l = i.data.addedFiles, c = [];
    let d = 0, u = 0;
    for (let p = 0; p < s.length; p++) {
      const b = s[p], m = l[p];
      if (!m || !m.fileId) {
        c.push({
          fileName: b.fileName,
          success: !1,
          error: "No file ID received from addFiles"
        }), u++;
        continue;
      }
      try {
        const f = b.filecontent.replace(/[^A-Za-z0-9+/=]/g, ""), A = atob(f), P = new Uint8Array(A.length);
        for (let k = 0; k < A.length; k++)
          P[k] = A.charCodeAt(k);
        const N = P.length, I = await D.getUploadId(r, b.fileName, m.fileId, N);
        if (!I.success || !I.data)
          throw new Error(`Failed to get upload ID: ${I.error}`);
        const { uploadId: v, uploadUrl: q } = I.data, w = await D.uploadData(q, v, P.buffer, b.fileName);
        if (!w.success || !w.data)
          throw new Error(`Failed to upload file content: ${w.error}`);
        c.push({
          fileName: b.fileName,
          fileId: m.fileId,
          success: !0,
          bytesUploaded: w.data.bytesUploaded
        }), d++;
      } catch (f) {
        c.push({
          fileName: b.fileName,
          fileId: m.fileId,
          success: !1,
          error: f instanceof Error ? f.message : "Unknown error"
        }), u++;
      }
    }
    E({
      action: "filesAdded",
      notebookId: r,
      message: `Processed ${s.length} files: ${d} successful, ${u} failed`,
      totalAdded: d,
      totalFailed: u,
      files: c
    }), e && e({
      success: u === 0,
      message: `Processed ${s.length} files: ${d} successful, ${u} failed`,
      data: {
        results: c,
        successCount: d,
        failureCount: u,
        totalFiles: s.length,
        notebookId: r
      }
    });
  } catch (r) {
    e && e({
      success: !1,
      error: r instanceof Error ? r.message : "Failed to process files"
    });
  }
}, ge = (n) => {
  const t = n.split(","), e = t[5] === "true", r = {
    totalParts: t.length,
    rawData: n,
    maxNotebooks: t[2],
    maxLinks: t[3],
    maxWordsPerFiles: t[4],
    isAuthenticated: t[5]
  };
  return {
    isAuthenticated: e,
    accountInfo: r
  };
}, rt = () => {
  D.getAccount().then((n) => {
    var e, r;
    const { isAuthenticated: t } = ge(
      ((r = (e = n.data) == null ? void 0 : e.rawAccountData) == null ? void 0 : r.toString()) || ""
    );
    h.isAuthenticated = t, h.isInitialized = !0;
  }).catch((n) => {
    h.isAuthenticated = !1, h.isInitialized = !0;
  }), chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: !0 }).catch((n) => {
  }), chrome.runtime.setUninstallURL(xe), chrome.runtime.onInstalled.addListener((n) => {
    n.reason === chrome.runtime.OnInstalledReason.INSTALL && chrome.tabs.create({
      url: "https://www.notebook-lm.online/welcomepage"
    });
  }), chrome.tabs.onRemoved.addListener((n) => {
    h.pendingNotifications.has(n) && h.pendingNotifications.delete(n);
  }), chrome.tabs.onActivated.addListener(async (n) => {
    K = n.tabId, await J(n.tabId), g.isActive && F(n.tabId, {
      action: "loadSelectedLinksForPage"
    }), T.isCapturing && (T.isCapturing = !1, T.currentRequestId = "", W({
      action: "resetScreenshotCapture"
    }), E({
      action: "screenshotCaptureReset",
      message: "Screenshot capture cancelled due to tab switch"
    }));
  }), chrome.tabs.onRemoved.addListener((n) => {
    j.delete(n);
  }), chrome.tabs.onUpdated.addListener(async (n, t, e) => {
    var r;
    e.active && (t.url && j.delete(n), t.url && ((r = e.url) != null && r.includes("youtube.com")) ? (await J(n), setTimeout(async () => {
      await J(n);
    }, 500), setTimeout(async () => {
      await J(n);
    }, 1e3)) : (t.url || t.status === "complete" && Y(e.url)) && await J(n), g.isActive && t.status === "complete" && F(n, {
      action: "loadSelectedLinksForPage"
    }), T.isCapturing && t.url && (T.isCapturing = !1, T.currentRequestId = "", F(n, {
      action: "resetScreenshotCapture"
    }), E({
      action: "screenshotCaptureReset",
      message: "Screenshot capture cancelled due to page navigation"
    })));
  }), chrome.tabs.onUpdated.addListener(async (n, t, e) => {
    var r;
    e.active && t.title && ((r = e.url) != null && r.includes("youtube.com")) && (K = e.id ?? null, await J(n));
  }), chrome.runtime.onMessage.addListener((n, t, e) => {
    var o;
    const r = n.source === "sidepanel";
    let s = null;
    return n.action === "getSidePageInfo" && n.source === "sidepanel" ? (J().then(() => {
      e({ success: !0 });
    }).catch((a) => {
      e({ success: !1, error: a.message });
    }), !0) : n.type === "accountData" ? (E({
      action: "userProfileLoaded",
      success: n.success,
      data: n.success ? n.data : null,
      error: n.success ? null : n.error || "Failed to get account data"
    }), e({ received: !0 }), !0) : (r ? "tabId" in n && n.tabId ? s = n.tabId : K && (s = K) : (o = t.tab) != null && o.id && (s = t.tab.id), !s && r ? (chrome.tabs.query({ active: !0, currentWindow: !0 }, (a) => {
      if (a && a.length > 0) {
        const i = a[0].id;
        i && ce(n, r, i, e);
      }
    }), !0) : s ? ce(n, r, s, e) : (e({ error: "Unable to process request" }), !1));
  });
};
rt();
