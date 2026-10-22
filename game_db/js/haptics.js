/* 觸覺回饋包裝：僅在 Capacitor 原生殼內有作用，純網頁版自動無聲 */
(function(){
  var c=null;
  try{ c=(window.Capacitor&&window.Capacitor.Plugins&&window.Capacitor.Plugins.Haptics)||null; }catch(e){}
  function safe(fn){ try{ if(c) fn(c); }catch(e){} }
  window.Hap={
    ok:!!c,
    impact:function(s){ safe(function(x){ x.impact({style:s||'MEDIUM'}); }); },
    notify:function(t){ safe(function(x){ x.notification({type:t||'SUCCESS'}); }); }
  };
})();
