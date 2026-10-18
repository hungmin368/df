/* js/ads.js — 統一廣告節點層
   portal SDK（CrazyGames / GameDistribution）存在時接通；不存在時全部降級為
   不擋遊戲的空操作：Ads.break 的 callback 保證會被呼叫（完成／失敗／逾時皆放行）。 */
(function () {
  const A = { ready: false, name: '' };

  function call(fn) { try { fn(); } catch (e) {} }

  function detect() {
    if (A.ready) return;
    try {
      if (window.CrazyGames && window.CrazyGames.SDK) {
        window.CrazyGames.SDK.init();
        A.name = 'crazygames';
        A.ready = true;
        call(function () { window.CrazyGames.SDK.game.loadingStop(); });
        return;
      }
    } catch (e) {}
    try {
      if (window.gdsdk && window.gdsdk.showAd) {
        A.name = 'gamedistribution';
        A.ready = true;
        return;
      }
    } catch (e) {}
  }

  A.init = detect;

  A.gameplayStart = function () {
    if (A.name === 'crazygames') call(function () { window.CrazyGames.SDK.game.gameplayStart(); });
  };
  A.gameplayStop = function () {
    if (A.name === 'crazygames') call(function () { window.CrazyGames.SDK.game.gameplayStop(); });
  };

  /* 插頁廣告：用於關卡結算後的「下一局／重新挑戰」等過場節點 */
  A.break = function (cb) {
    cb = cb || function () {};
    let called = false;
    const once = function () { if (!called) { called = true; cb(); } };
    if (A.name === 'crazygames') {
      call(function () {
        window.CrazyGames.SDK.ad.requestAd('midgame', {
          adFinished: once,
          adError: once,
          adStarted: function () {}
        });
      });
      setTimeout(once, 15000); /* 保險：SDK 未回呼也不卡住 */
      return;
    }
    if (A.name === 'gamedistribution') {
      call(function () {
        window.gdsdk.showAd(window.gdsdk.AdType && window.gdsdk.AdType.Interstitial, {
          onComplete: once,
          onError: once
        });
      });
      setTimeout(once, 15000);
      return;
    }
    setTimeout(cb, 30); /* 無 SDK：幾乎立即放行，遊戲行為不變 */
  };

  window.Ads = A;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', detect);
  else detect();
})();
