/* R25: screenshot-only viewer. Coordinates crop source pixels; no node reconstruction. */
(() => {
  'use strict';
  const boot = () => {
    const D = window.FUBGUN_ATLAS_IMAGES_R25;
    if (!D || !Array.isArray(D.variants) || !document.querySelector('[data-ag-root]')) return;
    const variants = new Map(D.variants.map(v => [v.id, v]));
    const regionNames = {full:'完整原图',tree:'全部树区',main:'中央主树',side:'周边与底部树',masters:'顶部大师图标'};
    const clamp = (x,lo,hi) => Math.min(hi,Math.max(lo,x));
    let main = null, modal = null;
    const all = [];
    const dialog = document.querySelector('#ag25-dialog');
    let priorOverflow = '';
    const fromHash = () => {
      try {const s=decodeURIComponent(location.hash.slice(1)).replace(/^variant-/, '');return variants.has(s)?s:null;} catch (_) {return null;}
    };
    const stored = () => {try {const s=JSON.parse(localStorage.getItem('poe2-fubgun-atlas-r24')||'{}');return variants.has(s.variant)?s.variant:null;}catch(_){return null;}};
    class Viewer {
      constructor(root) {
        this.root=root;this.isMain=root.hasAttribute('data-ag-main');this.viewport=root.querySelector('[data-ag-viewport]');
        this.crop=root.querySelector('[data-ag-crop]');this.img=root.querySelector('[data-ag-image]');
        this.regionSelect=root.querySelector('[data-ag-region]');this.variantSelect=root.querySelector('[data-ag-variant]');
        this.region='tree';this.scale=1;this.fitted=true;this.id=root.dataset.agInitial||D.variants[0].id;
        this.img.addEventListener('load',()=>{if(this.fitted)this.fit();});
        this.regionSelect.addEventListener('change',()=>{this.region=this.regionSelect.value;this.fit();});
        root.querySelectorAll('[data-ag-raw]').forEach(a=>a.addEventListener('click',e=>{
          if(!this.v.src.startsWith('data:')||!dialog||!modal)return;
          e.preventDefault();
          if(!dialog.open){priorOverflow=document.body.style.overflow;dialog.showModal();document.body.style.overflow='hidden';}
          modal.region='full';modal.regionSelect.value='full';modal.setVariant(this.id);requestAnimationFrame(()=>modal.fit());
        }));

        if(this.variantSelect)this.variantSelect.addEventListener('change',()=>this.setVariant(this.variantSelect.value));
        root.querySelectorAll('[data-ag-action]').forEach(b=>b.addEventListener('click',()=>{
          const a=b.dataset.agAction;
          if(a==='in')this.zoom(this.scale*1.25);
          if(a==='out')this.zoom(this.scale/1.25);
          if(a==='native')this.zoom(1);
          if(a==='fit')this.fit();
          if(a==='expand'&&dialog&&modal){priorOverflow=document.body.style.overflow;dialog.showModal();document.body.style.overflow='hidden';modal.region=this.region;modal.regionSelect.value=this.region;modal.setVariant(this.id);requestAnimationFrame(()=>modal.fit());}
        }));
        let drag=null;
        this.viewport.addEventListener('pointerdown',e=>{
          if(e.pointerType!=='mouse'||e.button!==0)return;
          drag={x:e.clientX,y:e.clientY,sx:this.viewport.scrollLeft,sy:this.viewport.scrollTop};
          this.viewport.setPointerCapture(e.pointerId);this.viewport.classList.add('is-dragging');
        });
        this.viewport.addEventListener('pointermove',e=>{if(!drag)return;this.viewport.scrollLeft=drag.sx-(e.clientX-drag.x);this.viewport.scrollTop=drag.sy-(e.clientY-drag.y);});
        const end=()=>{drag=null;this.viewport.classList.remove('is-dragging');};
        this.viewport.addEventListener('pointerup',end);this.viewport.addEventListener('pointercancel',end);this.viewport.addEventListener('lostpointercapture',end);
        this.viewport.addEventListener('keydown',e=>{if(e.key==='+'||e.key==='='){e.preventDefault();this.zoom(this.scale*1.25);}else if(e.key==='-'){e.preventDefault();this.zoom(this.scale/1.25);}else if(e.key==='0'){e.preventDefault();this.fit();}});
        if(window.ResizeObserver){let raf=0;this.observer=new ResizeObserver(()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>{if(this.fitted)this.fit();});});this.observer.observe(this.viewport);}
        this.setVariant(this.id,false);
      }
      setVariant(id, notify=true) {
        if(!variants.has(id))return;
        this.id=id;this.v=variants.get(id);
        if(this.img.getAttribute('src')!==this.v.src)this.img.src=this.v.src;
        this.img.alt=`Fubgun ${this.v.name}：用户提供的原始异界加点截图`;
        if(this.variantSelect)this.variantSelect.value=id;
        this.root.querySelectorAll('[data-ag-title]').forEach(n=>n.textContent=this.v.name+' / '+this.v.zh);
        this.root.querySelectorAll('[data-ag-size]').forEach(n=>n.textContent=`原图 ${this.v.width} × ${this.v.height} 像素`);
        this.root.querySelectorAll('[data-ag-raw]').forEach(n=>{n.href=this.v.src;n.setAttribute('aria-label',`打开 ${this.v.name} 原图`);});
        this.fit();
        if(this.isMain){
          document.querySelectorAll('[data-ag-pick]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.agPick===id)));
          document.querySelectorAll('[data-ag-current]').forEach(n=>n.textContent=this.v.name);
          if(notify){try{history.replaceState(null,'','#'+id);}catch(_){};window.dispatchEvent(new CustomEvent('fubgun:select',{detail:{id}}));}
        }
      }
      bounds(){return this.v.regions[this.region]||this.v.regions.tree;}
      render(){
        const [x,y,w,h]=this.bounds(),s=this.scale;
        this.crop.style.width=(w*s)+'px';this.crop.style.height=(h*s)+'px';
        Object.assign(this.img.style,{width:(this.v.width*s)+'px',height:(this.v.height*s)+'px',left:(-x*s)+'px',top:(-y*s)+'px'});
        this.root.querySelector('[data-ag-zoom]').textContent=Math.round(s*100)+'%';
        this.root.querySelector('[data-ag-region-name]').textContent=regionNames[this.region];
      }
      fit(){
        const [, , w,h]=this.bounds();const vw=this.viewport.clientWidth,vh=this.viewport.clientHeight;
        if(vw<30||vh<30){this.fitted=true;return;}
        this.fitted=true;this.scale=clamp(Math.min((vw-28)/w,(vh-28)/h),.15,6);this.render();
        this.viewport.scrollLeft=0;this.viewport.scrollTop=0;
      }
      zoom(value){
        const old=this.scale;const [, ,w,h]=this.bounds();
        const px=(this.viewport.scrollLeft+this.viewport.clientWidth/2)/Math.max(1,w*old+24);
        const py=(this.viewport.scrollTop+this.viewport.clientHeight/2)/Math.max(1,h*old+24);
        this.fitted=false;this.scale=clamp(value,.15,6);this.render();
        this.viewport.scrollLeft=px*(w*this.scale+24)-this.viewport.clientWidth/2;
        this.viewport.scrollTop=py*(h*this.scale+24)-this.viewport.clientHeight/2;
      }
    }
    document.querySelectorAll('[data-ag-enhanced]').forEach(n=>n.hidden=false);
    document.querySelectorAll('[data-ag-viewer]').forEach(root=>{const v=new Viewer(root);all.push(v);if(v.isMain)main=v;if(root.hasAttribute('data-ag-modal'))modal=v;});
    if(main){const forced={'atlas-expedition':'expedition','atlas-ritual':'ritual-belts','atlas-abyss':'currency-abyss','atlas-breach':'breach-rares','atlas-delirium':'deli-rush'}[document.body.dataset.page];const id=fromHash()||forced||stored()||main.id;try{const region=new URLSearchParams(location.search).get('view');if(regionNames[region]){main.region=region;main.regionSelect.value=region;}}catch(_){}main.setVariant(id);}
    document.querySelectorAll('[data-ag-pick]').forEach(b=>b.addEventListener('click',()=>main&&main.setVariant(b.dataset.agPick)));
    document.querySelectorAll('[data-ag-compare-details]').forEach(el=>el.addEventListener('toggle',()=>{if(el.open)requestAnimationFrame(()=>all.filter(v=>el.contains(v.root)).forEach(v=>v.fit()));}));
    document.querySelectorAll('[data-ag-close]').forEach(b=>b.addEventListener('click',()=>dialog&&dialog.close()));
    if(dialog){dialog.addEventListener('close',()=>{document.body.style.overflow=priorOverflow;});dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});}
    window.addEventListener('hashchange',()=>{const id=fromHash();if(main&&id&&main.id!==id)main.setVariant(id,false);});
    window.addEventListener('fubgun:variant',e=>{const id=e.detail&&e.detail.id;if(main&&variants.has(id)&&main.id!==id)main.setVariant(id,false);});
    window.addEventListener('beforeprint',()=>{document.querySelectorAll('[data-ag-originals]').forEach(el=>{el.dataset.wasOpen=String(el.open);el.open=true;});});
    window.addEventListener('afterprint',()=>{document.querySelectorAll('[data-ag-originals]').forEach(el=>el.open=el.dataset.wasOpen==='true');});
    document.documentElement.dataset.agReady='true';
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
