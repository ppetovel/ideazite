(function(){
  function buildBreadcrumbs(){
    var mapNames = {
      'awards': 'Awards',
      'canneslions': 'Cannes Lions',
      'eurobest': 'Eurobest',
      'spikes_asia': 'Spikes Asia',
      'dubai_lynx': 'Dubai Lynx',
      'fiap': 'FIAP'
    };

    var bc = document.getElementById('breadcrumbs');
    if(!bc) return;

    var isHttp = location.protocol === 'http:' || location.protocol === 'https:';
    var p = isHttp ? location.pathname.replace(/\/+$/,'') : '';
    var crumbs = ['<a href="/">Home</a>'];
    var jsonItems = [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": location.origin + "/" }
    ];
    var pos = 2;

    if(isHttp){
      var parts = p.split('/'); // ["","awards","canneslions","2025"]

      if(parts[1] === 'awards'){
        crumbs.push('<a href="/awards/">Awards</a>');
        jsonItems.push({
          "@type": "ListItem",
          "position": pos++,
          "name": "Awards",
          "item": location.origin + "/awards/"
        });
      }

      if(parts[2]){
        var festName = mapNames[parts[2]] || parts[2];
        crumbs.push('<a href="/awards/'+parts[2]+'/">'+festName+'</a>');
        jsonItems.push({
          "@type": "ListItem",
          "position": pos++,
          "name": festName,
          "item": location.origin + "/awards/"+parts[2]+"/"
        });
      }

      if(parts[3]){
        crumbs.push('<span>'+parts[3]+'</span>');
        jsonItems.push({
          "@type": "ListItem",
          "position": pos++,
          "name": parts[3],
          "item": location.origin + "/awards/"+parts[2]+"/"+parts[3]+"/"
        });
      }
    }else{
      crumbs.push('<span>Vista local</span>');
    }

    bc.innerHTML = crumbs.join(' / ');

    injectJsonLd(jsonItems);
  }

  function injectJsonLd(items){
    var ld = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": items
    };
    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(ld);
    document.head.appendChild(script);
  }

  function wireBack(){
    var back = document.getElementById('backBtn');
    if(!back) return;
    back.addEventListener('click', function(e){
      e.preventDefault();
      if (document.referrer && document.referrer.indexOf(location.host) !== -1) {
        history.back();
      } else {
        location.href = '/';
      }
    });
  }

  // Expone inicializador
  window.initHeader = function(){
    buildBreadcrumbs();
    wireBack();
  };
})();
