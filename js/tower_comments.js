/* 攻略彈幕＋攻略留言板（龍塔專用）— 本地模擬版：留言與讚僅存於本機 localStorage，尚未連線共用。
   掛載：覆寫 newRun／resTowerUI（同 main.js 的 winRound 覆寫模式），
   資料鍵：dinodoku-twcomments-<level>（留言池）、dinodoku-twposted-<level>（該關已留言 id，每關一則）、
   dinodoku-twlikes-<level>（該關已按讚 id，每關 3 個）、dinodoku-twname、dinodoku-danmaku-on、dinodoku-twday */
(function(){
  'use strict';

  var LS = {
    get: function(k, d){ try{ var v=localStorage.getItem(k); return v==null?d:JSON.parse(v); }catch(e){ return d; } },
    set: function(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  };
  var K = {
    cm:     'dinodoku-twcomments-',
    on:     'dinodoku-danmaku-on',
    name:   'dinodoku-twname',
    day:    'dinodoku-twday',
    posted: 'dinodoku-twposted-',
    likes:  'dinodoku-twlikes-'
  };
  var MAXLEN=30, NAMELEN=12, DAILY=10, MAXSTORE=50, FLYSEC=10, TRACKS=2, MAXLIKES=3;
  /* 敏感詞初版黑名單（可持續增補；命中即擋下不送出） */
  var BAD = ['操你','幹你娘','幹林','雞掰','機掰','去死','白癡','白痴','智障','低能','廢物','糞game','垃圾遊戲'];
  var BAD_RE = /https?:\/\/|www\./i;

  var cur=0, on=true, ui=null, resUI=null, queue=[], freeAt={t:[0,0], b:[0,0]}, pumpTimer=null, rafId=null, flying=[];

  function $(id){ return document.getElementById(id); }
  function el(tag, cls, text){ var e=document.createElement(tag); if(cls) e.className=cls; if(text!=null) e.textContent=text; return e; }
  function buddy(msg){ try{ if(typeof doBuddyChat==='function' && typeof BUDDY!=='undefined' && BUDDY.id) doBuddyChat(msg); }catch(e){} }
  function tap(){ try{ if(typeof SFX!=='undefined' && SFX.tap) SFX.tap(); }catch(e){} }

  /* ---------- DOM 建置 ---------- */
  function build(){
    if(ui) return;
    var main=$('main'), controls=$('controls');
    if(!main || !controls) return;

    var top=el('div','dk-band dk-top'); top.hidden=true;
    var bot=el('div','dk-band dk-bot'); bot.hidden=true;

    var name=el('input','dk-name'); name.maxLength=NAMELEN; name.placeholder='暱稱'; name.title='暱稱（可留空，最長 12 字）';
    var text=el('input','dk-text'); text.maxLength=MAXLEN; text.placeholder='攻略短句…（30 字內）';
    var send=el('button','dk-send','送出'); send.type='button';
    var input=el('div','dk-input'); input.appendChild(name); input.appendChild(text); input.appendChild(send);
    bot.appendChild(input);

    main.insertBefore(top, main.firstChild);
    controls.parentNode.insertBefore(bot, controls);

    var btn=el('button','btn btn-ghost dk-toggle','💬 彈幕'); btn.id='btn-danmaku'; btn.type='button';
    btn.title='攻略彈幕開關（本地測試版：留言僅存於此裝置）';
    controls.insertBefore(btn, controls.firstChild);
    btn.addEventListener('click', toggle);

    var bbtn=el('button','btn btn-ghost dk-boardbtn','📋 留言板'); bbtn.type='button';
    bbtn.title='攻略留言板：每關可留 1 則攻略、按 3 個讚（本地測試版：留言僅存於此裝置）';
    controls.insertBefore(bbtn, btn.nextSibling);
    bbtn.addEventListener('click', function(){ tap(); openBoard(); });

    send.addEventListener('click', function(){ submit(name, text, btn); });
    text.addEventListener('keydown', function(e){ if(e.key==='Enter'){ e.preventDefault(); submit(name, text, btn); } });

    ui={ top:top, bot:bot, btn:btn, bbtn:bbtn, name:name, text:text, send:send, input:input };
  }

  function buildResult(){
    if(resUI) return resUI;
    var modal=document.querySelector('#ov-result .modal');
    if(!modal) return null;
    var btns=modal.querySelector('.btns');
    if(!btns) return null;

    var rbtn=el('button','btn btn-ghost dk-resbtn','📋 攻略留言板'); rbtn.type='button';
    rbtn.title='查看這關的攻略留言與按讚（每關限 1 則留言、3 個讚）';
    btns.appendChild(rbtn);
    rbtn.addEventListener('click', function(){ tap(); openBoard(); });

    resUI={ btn:rbtn };
    return resUI;
  }

  /* ---------- 顯示切換 ---------- */
  function applyVis(){
    if(!ui) return;
    ui.btn.hidden = !cur;
    ui.bbtn.hidden = !cur;
    ui.btn.classList.toggle('off', !on);
    ui.top.hidden = !(cur && on);
    ui.bot.hidden = !(cur && on);
  }
  function toggle(){
    tap();
    on=!on;
    LS.set(K.on, on?'1':'0');
    if(ui){ ui.btn.classList.toggle('off', !on); ui.top.hidden=!(cur&&on); ui.bot.hidden=!(cur&&on); }
    if(cur && on) startPlay(); else stopPlay();
  }

  /* ---------- 播放 ---------- */
  function loadQueue(){
    var list=getList(cur).slice().sort(hotSort);
    queue=list.map(function(c){ return String(c.t||'').slice(0,MAXLEN); }).filter(Boolean);
    if(!queue.length) queue=['還沒有攻略，搶頭香！在留言板或下方輸入你的攻略'];
  }
  function startPlay(){
    if(!ui || !cur || !on) return;
    stopPlay();
    loadQueue();
    freeAt={t:[0,0], b:[0,0]};
    pump();
    pumpTimer=setInterval(pump, 250);
  }
  function stopPlay(){
    if(pumpTimer){ clearInterval(pumpTimer); pumpTimer=null; }
    if(rafId!=null){ cancelAnimationFrame(rafId); rafId=null; }
    flying=[];
    queue=[];
    if(ui){
      ui.top.querySelectorAll('.dk-item').forEach(function(n){ n.remove(); });
      ui.bot.querySelectorAll('.dk-item').forEach(function(n){ n.remove(); });
    }
  }
  function pump(){
    if(!on || !cur || !ui || !queue.length) return;
    var now=performance.now();
    var bands=[{el:ui.top, k:'t'}, {el:ui.bot, k:'b'}];
    for(var bi=0; bi<bands.length; bi++){
      var band=bands[bi];
      if(band.el.hidden) continue;
      for(var i=0; i<TRACKS; i++){
        if(!queue.length) return;
        if(freeAt[band.k][i] <= now){
          freeAt[band.k][i] = spawn(band.el, queue.shift());
        }
      }
    }
  }
  function spawn(band, text){
    var item=el('span','dk-item'); item.textContent=text;
    band.appendChild(item);
    var ig = band===ui.bot ? band.querySelector('.dk-input') : null;
    var reserved = ig ? ig.offsetWidth + 12 : 0;
    var bw = band.clientWidth, iw = item.offsetWidth;
    var startX = Math.max(0, bw - reserved);
    item.style.transform='translateX('+startX+'px)';
    var dist = startX + iw + 8;
    var speed = dist/(FLYSEC*1000); /* px/ms */
    flying.push({ el:item, x:startX, w:iw, speed:speed, last:performance.now() });
    ensureLoop();
    return performance.now() + ((iw+36)/speed);
  }
  /* rAF 驅動移動：純 transform 更新（不觸發 layout），飄出左緣即移除 */
  function ensureLoop(){
    if(rafId!=null) return;
    rafId=requestAnimationFrame(tick);
  }
  function tick(){
    rafId=null;
    var now=performance.now();
    for(var i=flying.length-1; i>=0; i--){
      var f=flying[i];
      f.x -= f.speed*(now-f.last);
      f.last=now;
      if(f.x <= -(f.w+8)){
        f.el.remove();
        flying.splice(i,1);
      }else{
        f.el.style.transform='translateX('+f.x+'px)';
      }
    }
    if(flying.length) rafId=requestAnimationFrame(tick);
  }

  /* ---------- 送出 ---------- */
  function bad(text){
    var t=text.toLowerCase();
    if(BAD_RE.test(t)) return true;
    for(var i=0;i<BAD.length;i++){ if(t.indexOf(BAD[i])>=0) return true; }
    return false;
  }
  function todayStr(){
    var d=new Date();
    return d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate();
  }
  function submit(nameEl, textEl, feedbackBtn){
    if(!cur){ return; }
    var name=(nameEl.value||'').trim().slice(0,NAMELEN);
    var text=(textEl.value||'').trim().slice(0,MAXLEN);
    if(!text){
      buddy('想好攻略再送出喔！');
      return;
    }
    var last=LS.get(K.last, null);
    if(last && last.lv===cur && Date.now()-last.ts < COOLDOWN){
      buddy('這關的攻略彈幕還在冷卻（60 秒一則），先繼續闖關吧！');
      return;
    }
    var ds=todayStr();
    var day=LS.get(K.day, null);
    var n=(day && day.d===ds) ? day.n : 0;
    if(n >= DAILY){
      buddy('今天的攻略彈幕額度用完了（每日 '+DAILY+' 則），明天再來分享！');
      return;
    }
    if(bad(text)){
      buddy('這則留言包含不適當的內容，換個說法吧！');
      return;
    }
    var list=LS.get(K.cm+cur, []);
    list.unshift({ n:name||'匿名獵人', t:text, ts:Date.now() });
    if(list.length>MAXSTORE) list.length=MAXSTORE;
    LS.set(K.cm+cur, list);
    LS.set(K.last, { lv:cur, ts:Date.now() });
    LS.set(K.day, { d:ds, n:n+1 });
    if(name) LS.set(K.name, name);
    textEl.value='';
    if(on && cur && ui && !ui.bot.hidden){ queue.unshift(text); pump(); }
    buddy('攻略彈幕已送出！（本地測試版：僅存於此裝置）');
    if(feedbackBtn){
      var old=feedbackBtn.textContent;
      feedbackBtn.textContent='已送出 ✓';
      setTimeout(function(){ feedbackBtn.textContent=old; }, 1500);
    }
  }

  /* ---------- 對外掛載點 ---------- */
  function sync(L){
    build();
    if(!ui) return;
    cur=Math.max(0, +L||0);
    on = LS.get(K.on,'1')==='1'; /* 未設定過時預設開 */
    applyVis();
    if(cur && on) startPlay(); else stopPlay();
  }
  function onResult(towerMode){
    var r=buildResult();
    if(!r) return;
    r.btn.hidden = !towerMode;
    r.box.classList.remove('show');
    r.name.value = LS.get(K.name,'')||'';
  }

  window.TWDANMAKU = { sync: sync, onResult: onResult };

  /* 覆寫掛鉤（同 main.js 的 winRound 覆寫模式）：任何新局開始同步、龍塔結果畫面顯示入口 */
  try{
    if(typeof newRun==='function'){
      var OLD_NEWRUN = newRun;
      newRun = function(){
        var r = OLD_NEWRUN.apply(this, arguments);
        try{ if(window.TWDANMAKU && typeof TOWER!=='undefined') window.TWDANMAKU.sync(TOWER.level); }catch(e){}
        return r;
      };
    }
    if(typeof resTowerUI==='function'){
      var OLD_RESTOWER = resTowerUI;
      resTowerUI = function(){
        var r = OLD_RESTOWER.apply(this, arguments);
        try{ if(window.TWDANMAKU) window.TWDANMAKU.onResult(arguments[0]); }catch(e){}
        return r;
      };
    }
  }catch(e){}

  /* 開機收尾：若載入時已在局中（罕見），隱藏待下次 newRun 同步 */
  document.addEventListener('DOMContentLoaded', function(){ /* DOM 已就緒（本檔置於 body 尾） */ });
})();
