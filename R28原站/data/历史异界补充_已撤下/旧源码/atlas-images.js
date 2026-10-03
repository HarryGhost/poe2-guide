/* R23: exact remote source screenshots. No external script, telemetry, generated tree or auto fetch. */
(()=>{'use strict';
 const figures=Array.from(document.querySelectorAll('[data-r23-figure]'));
 if(!figures.length)return;
 const dialog=document.getElementById('r23-image-dialog');
 const viewer=document.getElementById('r23-viewer-img');
 const title=document.getElementById('r23-image-title');
 const timers=new Map();
 function loadFigure(fig){
  const img=fig.querySelector('img[data-r23-src]');
  const status=fig.querySelector('[data-r23-status]');
  const button=fig.querySelector('[data-r23-load]');
  if(!img||!status||!button||fig.dataset.loading==='true'||fig.dataset.loaded==='true')return;
  const url=img.dataset.r23Src;
  try{if(new URL(url).hostname!=='cdn.mobalytics.gg')throw Error('Unexpected image host');}
  catch(_){status.textContent='图片地址不可用，请打开作者攻略。';return;}
  fig.dataset.loading='true';status.dataset.state='loading';
  status.textContent='正在连接原图来源；打不开时可直接打开原图或作者攻略。';
  button.disabled=true;button.textContent='正在加载…';
  const done=()=>{clearTimeout(timers.get(fig));timers.delete(fig);fig.dataset.loading='false';button.disabled=false;};
  const fail=()=>{done();fig.dataset.loaded='false';img.hidden=true;fig.querySelector('.r23-online-note').hidden=false;status.dataset.state='failed';status.textContent='本次未能载入原图。正文仍可读；可重试、直接打开原图，或打开作者攻略。';button.textContent='重试联网加载';};
  img.onload=()=>{
   if(!img.naturalWidth){fail();return;}
   done();fig.dataset.loaded='true';img.hidden=false;
   fig.querySelector('.r23-online-note').hidden=true;
   const zoom=fig.querySelector('[data-r23-zoom]');if(zoom)zoom.disabled=false;
   status.dataset.state='loaded';status.textContent='原图已加载。点击图片或“放大查看”；本次加载不代表已经离线保存。';
  };
  img.onerror=fail;
  timers.set(fig,setTimeout(fail,15000));
  img.src=url;
 }
 function openFigure(fig){
  const img=fig.querySelector('img[data-r23-src]');
  if(fig.dataset.loaded!=='true'||!img||!dialog||!viewer)return;
  title.textContent=fig.querySelector('h3').textContent;
  viewer.src=img.src;viewer.alt=img.alt;viewer.style.width='100%';
  dialog.showModal();
  const scroller=dialog.querySelector('.r23-viewer-scroll');scroller.scrollTop=0;scroller.scrollLeft=0;
 }
 figures.forEach(fig=>{
  fig.querySelector('[data-r23-load]').addEventListener('click',()=>loadFigure(fig));
  const zoom=fig.querySelector('[data-r23-zoom]');if(zoom)zoom.addEventListener('click',()=>openFigure(fig));
  fig.querySelector('img[data-r23-src]').addEventListener('click',()=>openFigure(fig));
 });
 document.querySelectorAll('[data-r23-load-all]').forEach(btn=>btn.addEventListener('click',()=>figures.forEach(loadFigure)));
 if(dialog){
  dialog.querySelector('[data-r23-close]').addEventListener('click',()=>dialog.close());
  dialog.querySelectorAll('[data-r23-size]').forEach(btn=>btn.addEventListener('click',()=>{viewer.style.width=btn.dataset.r23Size+'%';}));
 }
})();
